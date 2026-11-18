"""
INVESTIGATION 4: Model Improvement & Leverage-Adjusted Rating Framework (CRISP v2)
Tests integrating:
1. Match Leverage Weighting:
   In high pressure, deliveries where overid >= 16 (death overs) or rrr_pre >= 11.0 have higher swing/impact.
2. Phase-Normalized Baselines:
   Death-overs performance has higher run expectation than middle/powerplay.
   Does Bumrah rise when death-over leverage is properly weighted?
3. Dot-Ball Suppression / Concession:
   In death bowling, dot-ball % and boundary concession % are crucial defensive indicators.
4. Dismissal Resistance (Balls per dismissal) vs Raw Average.

Builds and compares:
- Current CRISP (v1)
- Improved CRISP (v2 - High Leverage & Phase-Weighted)
Computes Top 10 Batters & Bowlers under both frameworks.
"""
import pandas as pd
import numpy as np

PROJ_DIR = r"C:\rajsathan_royals"
OUT_PROC = r"C:\rajsathan_royals\outputs\processed"
OUT_RANK = r"C:\rajsathan_royals\outputs\rankings"

df = pd.read_parquet(f"{OUT_PROC}/match_states.parquet")
df_scope = df[df['competition_type'].isin(['IPL', 'T20I'])].copy()

# Add Delivery Leverage Multiplier (L_t):
# Base L_t = pressure_score
# If death overs (overid >= 16): L_t *= 1.25
# If RRR >= 12.0 in chase: L_t *= 1.25
# Extreme over (overid >= 18): L_t *= 1.35
def calc_leverage(row):
    p = row['pressure_score']
    over = row['overid']
    rrr = row['rrr_pre']
    mult = 1.0
    if over >= 16:
        mult *= 1.20
    if over >= 18:
        mult *= 1.20
    if pd.notnull(rrr) and rrr >= 12.0:
        mult *= 1.15
    return p * mult

df_scope['delivery_leverage'] = df_scope.apply(calc_leverage, axis=1)

# Weighted RAE and RPA by delivery leverage
df_scope['lev_rae'] = df_scope['batter_rae'] * df_scope['delivery_leverage']
df_scope['lev_rpa'] = df_scope['bowler_rpa'] * df_scope['delivery_leverage']

# Re-aggregate Batters
p_bat = df_scope[df_scope['is_high_pressure']]
b_agg = p_bat.groupby('striker_id').agg(
    p_balls=('runs', 'count'),
    p_runs=('runs', 'sum'),
    p_dismissals=('is_wicket', 'sum'),
    p_fours=('is_four', 'sum'),
    p_sixes=('is_six', 'sum'),
    p_dots=('runs', lambda x: (x == 0).sum()),
    p_rae=('batter_rae', 'sum'),
    p_lev_rae=('lev_rae', 'sum'),
    p_matches=('match_id', 'nunique')
).reset_index()

# Normal metrics
n_bat = df_scope[~df_scope['is_high_pressure']].groupby('striker_id').agg(
    n_balls=('runs', 'count'),
    n_runs=('runs', 'sum'),
    n_dismissals=('is_wicket', 'sum')
).reset_index()
n_bat['n_sr'] = np.where(n_bat['n_balls'] > 0, n_bat['n_runs'] / n_bat['n_balls'] * 100.0, 0.0)

b_m = b_agg.merge(n_bat, on='striker_id', how='left')
b_m['p_sr'] = (b_m['p_runs'] / b_m['p_balls']) * 100.0
b_m['p_avg'] = np.where(b_m['p_dismissals'] > 0, b_m['p_runs'] / b_m['p_dismissals'], b_m['p_runs'])
b_m['sr_delta'] = b_m['p_sr'] - b_m['n_sr'].fillna(b_m['p_sr'])
b_m['p_dot_pct'] = (b_m['p_dots'] / b_m['p_balls']) * 100.0
b_m['balls_per_dismissal'] = b_m['p_balls'] / np.maximum(1, b_m['p_dismissals'])

# Re-aggregate Bowlers
p_bw = df_scope[df_scope['is_high_pressure'] & df_scope['is_legal_ball']]
bw_agg = p_bw.groupby('bowler_id').agg(
    p_balls=('is_legal_ball', 'sum'),
    p_runs=('bowler_runs_conceded', 'sum'),
    p_wickets=('is_bowler_wicket', 'sum'),
    p_fours=('is_four', 'sum'),
    p_sixes=('is_six', 'sum'),
    p_dots=('delivery_total_runs', lambda x: (x == 0).sum()),
    p_rpa=('bowler_rpa', 'sum'),
    p_lev_rpa=('lev_rpa', 'sum'),
    p_matches=('match_id', 'nunique'),
    death_balls=('overid', lambda x: (x >= 16).sum()),
    death_runs=('bowler_runs_conceded', lambda x: x.loc[p_bw.loc[x.index, 'overid'] >= 16].sum()),
    death_wkts=('is_bowler_wicket', lambda x: x.loc[p_bw.loc[x.index, 'overid'] >= 16].sum())
).reset_index()

n_bw = df_scope[~df_scope['is_high_pressure'] & df_scope['is_legal_ball']].groupby('bowler_id').agg(
    n_balls=('is_legal_ball', 'sum'),
    n_runs=('bowler_runs_conceded', 'sum'),
    n_wickets=('is_bowler_wicket', 'sum')
).reset_index()
n_bw['n_econ'] = np.where(n_bw['n_balls'] > 0, n_bw['n_runs'] / (n_bw['n_balls'] / 6.0), 99.0)

bw_m = bw_agg.merge(n_bw, on='bowler_id', how='left')
bw_m['p_econ'] = bw_m['p_runs'] / (bw_m['p_balls'] / 6.0)
bw_m['econ_delta'] = bw_m['n_econ'].fillna(bw_m['p_econ']) - bw_m['p_econ']
bw_m['p_dot_pct'] = (bw_m['p_dots'] / bw_m['p_balls']) * 100.0
bw_m['p_bound_pct'] = ((bw_m['p_fours'] + bw_m['p_sixes']) / bw_m['p_balls']) * 100.0
bw_m['p_wkt_rate'] = bw_m['p_wickets'] / bw_m['p_balls']

# Load player mapping
mapping = pd.read_csv('C:/rajsathan_royals/data/Data Pack/competition_team_player_mapping.csv')
p_names = mapping[['player_id', 'player_name']].drop_duplicates(subset=['player_id']).set_index('player_id')['player_name'].to_dict()

b_m['player_name'] = b_m['striker_id'].map(p_names).fillna('Unknown')
bw_m['player_name'] = bw_m['bowler_id'].map(p_names).fillna('Unknown')

# Standardize z-scores
def z_score(s):
    std = s.std()
    return (s - s.mean()) / (std if std > 0 else 1.0)

# Filter qualification (>= 100 balls, >= 10 matches)
b_qual = b_m[(b_m['p_balls'] >= 100) & (b_m['p_matches'] >= 10)].copy()
bw_qual = bw_m[(bw_m['p_balls'] >= 100) & (bw_m['p_matches'] >= 10)].copy()

# Empirical Bayes Shrinkage (K = 60)
b_qual['w'] = b_qual['p_balls'] / (b_qual['p_balls'] + 60.0)
b_qual['shrunk_sr'] = b_qual['w'] * b_qual['p_sr'] + (1 - b_qual['w']) * 136.75
b_qual['shrunk_rae'] = b_qual['w'] * (b_qual['p_lev_rae'] / b_qual['p_balls']) + (1 - b_qual['w']) * 0.11

bw_qual['w'] = bw_qual['p_balls'] / (bw_qual['p_balls'] + 60.0)
bw_qual['shrunk_econ'] = bw_qual['w'] * bw_qual['p_econ'] + (1 - bw_qual['w']) * 8.53
bw_qual['shrunk_rpa'] = bw_qual['w'] * (bw_qual['p_lev_rpa'] / bw_qual['p_balls']) + (1 - bw_qual['w']) * -0.11
bw_qual['shrunk_wkt_rate'] = bw_qual['w'] * bw_qual['p_wkt_rate'] + (1 - bw_qual['w']) * 0.05

# Improved BPRI (v2)
b_qual['z_lev_rae'] = z_score(b_qual['shrunk_rae'])
b_qual['z_sr'] = z_score(b_qual['shrunk_sr'])
b_qual['z_avg'] = z_score(np.log1p(b_qual['p_avg']))
b_qual['z_delta'] = z_score(b_qual['sr_delta'])
b_qual['z_vol'] = z_score(np.log1p(b_qual['p_balls']))

b_qual['BPRI_v2_raw'] = (
    0.35 * b_qual['z_lev_rae'] +
    0.25 * b_qual['z_sr'] +
    0.15 * b_qual['z_avg'] +
    0.10 * b_qual['z_delta'] +
    0.15 * b_qual['z_vol']
)
b_qual['BPRI_v2'] = (50.0 + 15.0 * b_qual['BPRI_v2_raw']).round(2)
b_v2_ranked = b_qual.sort_values('BPRI_v2', ascending=False).reset_index(drop=True)
b_v2_ranked['Rank_v2'] = np.arange(1, len(b_v2_ranked) + 1)

# Improved Bowler_PRI (v2) - Death Leverage & Dot Suppression
bw_qual['z_lev_rpa'] = z_score(bw_qual['shrunk_rpa'])
bw_qual['z_econ_inv'] = z_score(-bw_qual['shrunk_econ'])
bw_qual['z_wkt'] = z_score(bw_qual['shrunk_wkt_rate'])
bw_qual['z_delta'] = z_score(bw_qual['econ_delta'])
bw_qual['z_dot'] = z_score(bw_qual['p_dot_pct'])
bw_qual['z_vol'] = z_score(np.log1p(bw_qual['p_balls']))

bw_qual['Bowler_PRI_v2_raw'] = (
    0.35 * bw_qual['z_lev_rpa'] +
    0.20 * bw_qual['z_econ_inv'] +
    0.15 * bw_qual['z_wkt'] +
    0.10 * bw_qual['z_delta'] +
    0.05 * bw_qual['z_dot'] +
    0.15 * bw_qual['z_vol']
)
bw_qual['Bowler_PRI_v2'] = (50.0 + 15.0 * bw_qual['Bowler_PRI_v2_raw']).round(2)
bw_v2_ranked = bw_qual.sort_values('Bowler_PRI_v2', ascending=False).reset_index(drop=True)
bw_v2_ranked['Rank_v2'] = np.arange(1, len(bw_v2_ranked) + 1)

print("\n=== TOP 15 BATTERS (IMPROVED LEVERAGE-AWARE CRISP v2) ===")
b_cols = ['Rank_v2', 'player_name', 'striker_id', 'p_matches', 'p_balls', 'p_runs', 'p_sr', 'p_avg', 'sr_delta', 'p_rae', 'BPRI_v2']
print(b_v2_ranked[b_cols].head(15).to_string(index=False))

print("\n=== TOP 15 BOWLERS (IMPROVED LEVERAGE-AWARE CRISP v2) ===")
bw_cols = ['Rank_v2', 'player_name', 'bowler_id', 'p_matches', 'p_balls', 'p_runs', 'p_econ', 'p_wickets', 'econ_delta', 'p_rpa', 'Bowler_PRI_v2']
print(bw_v2_ranked[bw_cols].head(15).to_string(index=False))

# Save comparison tables
b_v2_ranked.to_csv(f"{OUT_RANK}/batter_rankings_v2.csv", index=False)
bw_v2_ranked.to_csv(f"{OUT_RANK}/bowler_rankings_v2.csv", index=False)
b_v2_ranked.head(10).to_csv(f"{OUT_RANK}/batter_top10_v2.csv", index=False)
bw_v2_ranked.head(10).to_csv(f"{OUT_RANK}/bowler_top10_v2.csv", index=False)

print("\nSaved v2 models successfully.")
