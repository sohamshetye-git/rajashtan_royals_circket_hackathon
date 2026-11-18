"""
PHASE 6 & 7: Comprehensive Player Aggregation & Pressure Metrics Pipeline
Calculates for Batters and Bowlers:
- Overall baseline vs High-Pressure (P >= 0.65) vs Normal (P < 0.65)
- Runs, Balls Faced, Strike Rate, Average, Boundary %, Dot Ball %
- Pressure Runs Above Expected (RAE) per ball
- Bowler Economy, Wickets, Dot %, Boundary Concession %, RPA per ball, WAE
- Match-level consistency (matches with positive impact, std dev, match sample size)
- Formats: IPL, T20I, Combined
"""
import os
import pandas as pd
import numpy as np

PROJ_DIR = r"C:\rajsathan_royals"
OUT_PROC = os.path.join(PROJ_DIR, "outputs", "processed")
OUT_RANK = os.path.join(PROJ_DIR, "outputs", "rankings")
OUT_VAL = os.path.join(PROJ_DIR, "outputs", "validation")

os.makedirs(OUT_RANK, exist_ok=True)

print("=" * 80)
print("PHASE 6 & 7: PLAYER PERFORMANCE AGGREGATION UNDER PRESSURE")
print("=" * 80)

# Load master player names
mapping = pd.read_csv(r"C:\rajsathan_royals\data\Data Pack\competition_team_player_mapping.csv")
player_names = mapping[['player_id', 'player_name']].drop_duplicates(subset=['player_id']).set_index('player_id')['player_name'].to_dict()

df = pd.read_parquet(os.path.join(OUT_PROC, "match_states.parquet"))
# Filter to official scope: IPL and T20I
df_scope = df[df['competition_type'].isin(['IPL', 'T20I'])].copy()
print(f"Total IPL & T20I Deliveries: {len(df_scope):,}")

# -------------------------------------------------------------
# 1. BATTER AGGREGATION PIPELINE
# -------------------------------------------------------------
print("\n--- AGGREGATING BATTER METRICS ---")

def aggregate_batters(data, suffix=""):
    # Normal deliveries: pressure_score < 0.65
    # Pressure deliveries: pressure_score >= 0.65
    
    # Pressure metrics
    p_data = data[data['is_high_pressure']]
    # Normal metrics
    n_data = data[~data['is_high_pressure']]
    
    # 1. Pressure aggregations
    p_agg = p_data.groupby('striker_id').agg(
        p_balls=('runs', 'count'),
        p_runs=('runs', 'sum'),
        p_dismissals=('is_wicket', 'sum'), # Striker was on strike when wicket fell
        p_fours=('is_four', 'sum'),
        p_sixes=('is_six', 'sum'),
        p_dots=('runs', lambda x: (x == 0).sum()),
        p_rae=('batter_rae', 'sum'),
        p_mean_rae=('batter_rae', 'mean'),
        p_matches=('match_id', 'nunique'),
        p_mean_pressure=('pressure_score', 'mean')
    ).reset_index()
    
    # Match-level consistency for pressure
    p_match = p_data.groupby(['striker_id', 'match_id']).agg(
        m_runs=('runs', 'sum'),
        m_balls=('runs', 'count'),
        m_rae=('batter_rae', 'sum')
    ).reset_index()
    
    p_consistency = p_match.groupby('striker_id').agg(
        p_pos_rae_matches=('m_rae', lambda x: (x > 0).sum()),
        p_rae_match_std=('m_rae', 'std')
    ).reset_index()
    
    p_agg = p_agg.merge(p_consistency, on='striker_id', how='left')
    p_agg['p_consistency_pct'] = (p_agg['p_pos_rae_matches'] / p_agg['p_matches']) * 100.0
    p_agg['p_rae_match_std'] = p_agg['p_rae_match_std'].fillna(0.0)
    
    p_agg['p_sr'] = np.where(p_agg['p_balls'] > 0, (p_agg['p_runs'] / p_agg['p_balls']) * 100.0, 0.0)
    p_agg['p_avg'] = np.where(p_agg['p_dismissals'] > 0, p_agg['p_runs'] / p_agg['p_dismissals'], p_agg['p_runs'])
    p_agg['p_boundary_pct'] = np.where(p_agg['p_balls'] > 0, ((p_agg['p_fours'] + p_agg['p_sixes']) / p_agg['p_balls']) * 100.0, 0.0)
    p_agg['p_dot_pct'] = np.where(p_agg['p_balls'] > 0, (p_agg['p_dots'] / p_agg['p_balls']) * 100.0, 0.0)
    
    # 2. Normal / Baseline aggregations
    n_agg = n_data.groupby('striker_id').agg(
        n_balls=('runs', 'count'),
        n_runs=('runs', 'sum'),
        n_dismissals=('is_wicket', 'sum'),
        n_matches=('match_id', 'nunique')
    ).reset_index()
    n_agg['n_sr'] = np.where(n_agg['n_balls'] > 0, (n_agg['n_runs'] / n_agg['n_balls']) * 100.0, 0.0)
    n_agg['n_avg'] = np.where(n_agg['n_dismissals'] > 0, n_agg['n_runs'] / n_agg['n_dismissals'], n_agg['n_runs'])
    
    # Overall total matches and balls
    tot_agg = data.groupby('striker_id').agg(
        tot_balls=('runs', 'count'),
        tot_runs=('runs', 'sum'),
        tot_matches=('match_id', 'nunique'),
        tot_ipl_matches=('match_id', lambda x: data.loc[x.index][data.loc[x.index, 'competition_type'] == 'IPL']['match_id'].nunique()),
        tot_t20i_matches=('match_id', lambda x: data.loc[x.index][data.loc[x.index, 'competition_type'] == 'T20I']['match_id'].nunique())
    ).reset_index()
    
    # Merge all
    b_df = p_agg.merge(n_agg, on='striker_id', how='left').merge(tot_agg, on='striker_id', how='left')
    b_df['player_name'] = b_df['striker_id'].map(player_names).fillna("Unknown")
    
    # Deltas
    b_df['sr_delta'] = b_df['p_sr'] - b_df['n_sr'].fillna(b_df['p_sr'])
    
    if suffix:
        b_df = b_df.add_suffix(f"_{suffix}")
        b_df = b_df.rename(columns={f"striker_id_{suffix}": "striker_id", f"player_name_{suffix}": "player_name"})
    return b_df

batters_combined = aggregate_batters(df_scope)
print(f"Total Batters with pressure deliveries: {len(batters_combined)}")

# -------------------------------------------------------------
# 2. BOWLER AGGREGATION PIPELINE
# -------------------------------------------------------------
print("\n--- AGGREGATING BOWLER METRICS ---")

def aggregate_bowlers(data, suffix=""):
    p_data = data[data['is_high_pressure']]
    n_data = data[~data['is_high_pressure']]
    
    # 1. Pressure aggregations
    # Legal balls only for economy and ball counting
    p_agg = p_data.groupby('bowler_id').agg(
        p_deliveries=('delivery_total_runs', 'count'),
        p_legal_balls=('is_legal_ball', 'sum'),
        p_runs_conceded=('bowler_runs_conceded', 'sum'),
        p_wickets=('is_bowler_wicket', 'sum'),
        p_fours_conceded=('is_four', 'sum'),
        p_sixes_conceded=('is_six', 'sum'),
        p_dots=('delivery_total_runs', lambda x: (x == 0).sum()),
        p_rpa=('bowler_rpa', 'sum'),
        p_mean_rpa=('bowler_rpa', 'mean'),
        p_wae=('bowler_wae', 'sum'),
        p_matches=('match_id', 'nunique'),
        p_mean_pressure=('bowler_pressure_score', 'mean')
    ).reset_index()
    
    # Match-level consistency for pressure
    p_match = p_data.groupby(['bowler_id', 'match_id']).agg(
        m_rpa=('bowler_rpa', 'sum'),
        m_wickets=('is_bowler_wicket', 'sum')
    ).reset_index()
    
    p_consistency = p_match.groupby('bowler_id').agg(
        p_pos_rpa_matches=('m_rpa', lambda x: (x > 0).sum()),
        p_rpa_match_std=('m_rpa', 'std')
    ).reset_index()
    
    p_agg = p_agg.merge(p_consistency, on='bowler_id', how='left')
    p_agg['p_consistency_pct'] = (p_agg['p_pos_rpa_matches'] / p_agg['p_matches']) * 100.0
    p_agg['p_rpa_match_std'] = p_agg['p_rpa_match_std'].fillna(0.0)
    
    # Pressure overs, economy, boundary concession %, dot %
    p_agg['p_overs'] = p_agg['p_legal_balls'] / 6.0
    p_agg['p_econ'] = np.where(p_agg['p_overs'] > 0, p_agg['p_runs_conceded'] / p_agg['p_overs'], 99.0)
    p_agg['p_sr_bowl'] = np.where(p_agg['p_wickets'] > 0, p_agg['p_legal_balls'] / p_agg['p_wickets'], 99.0)
    p_agg['p_boundary_pct'] = np.where(p_agg['p_legal_balls'] > 0, ((p_agg['p_fours_conceded'] + p_agg['p_sixes_conceded']) / p_agg['p_legal_balls']) * 100.0, 0.0)
    p_agg['p_dot_pct'] = np.where(p_agg['p_legal_balls'] > 0, (p_agg['p_dots'] / p_agg['p_legal_balls']) * 100.0, 0.0)
    
    # 2. Normal / Baseline aggregations
    n_agg = n_data.groupby('bowler_id').agg(
        n_legal_balls=('is_legal_ball', 'sum'),
        n_runs_conceded=('bowler_runs_conceded', 'sum'),
        n_wickets=('is_bowler_wicket', 'sum'),
        n_matches=('match_id', 'nunique')
    ).reset_index()
    n_agg['n_overs'] = n_agg['n_legal_balls'] / 6.0
    n_agg['n_econ'] = np.where(n_agg['n_overs'] > 0, n_agg['n_runs_conceded'] / n_agg['n_overs'], 99.0)
    
    # Overall total matches and overs
    tot_agg = data.groupby('bowler_id').agg(
        tot_legal_balls=('is_legal_ball', 'sum'),
        tot_runs_conceded=('bowler_runs_conceded', 'sum'),
        tot_wickets=('is_bowler_wicket', 'sum'),
        tot_matches=('match_id', 'nunique'),
        tot_ipl_matches=('match_id', lambda x: data.loc[x.index][data.loc[x.index, 'competition_type'] == 'IPL']['match_id'].nunique()),
        tot_t20i_matches=('match_id', lambda x: data.loc[x.index][data.loc[x.index, 'competition_type'] == 'T20I']['match_id'].nunique())
    ).reset_index()
    tot_agg['tot_overs'] = tot_agg['tot_legal_balls'] / 6.0
    
    # Merge all
    bw_df = p_agg.merge(n_agg, on='bowler_id', how='left').merge(tot_agg, on='bowler_id', how='left')
    bw_df['player_name'] = bw_df['bowler_id'].map(player_names).fillna("Unknown")
    
    # Delta (lower economy in pressure vs normal is positive improvement)
    bw_df['econ_delta'] = bw_df['n_econ'].fillna(bw_df['p_econ']) - bw_df['p_econ'] # Positive means improved in pressure
    
    if suffix:
        bw_df = bw_df.add_suffix(f"_{suffix}")
        bw_df = bw_df.rename(columns={f"bowler_id_{suffix}": "bowler_id", f"player_name_{suffix}": "player_name"})
    return bw_df

bowlers_combined = aggregate_bowlers(df_scope)
print(f"Total Bowlers with pressure deliveries: {len(bowlers_combined)}")

# Save intermediate player metrics
batters_combined.to_parquet(os.path.join(OUT_PROC, "batter_aggregated_raw.parquet"), index=False)
bowlers_combined.to_parquet(os.path.join(OUT_PROC, "bowler_aggregated_raw.parquet"), index=False)

print("Player aggregations complete and saved.")
