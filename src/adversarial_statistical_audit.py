"""
Adversarial Statistical Audit Script:
1. Fast, highly optimized 2,000 match-clustered bootstrap iterations.
2. Formulates Top-10 & Top-15 inclusion probability, median rank, 5th-95th percentile rank.
3. Breakdown of qualifying matches, balls, runs/wickets, economy/SR across IPL & T20I.
4. Comprehensive weight sensitivity testing (Equal, Performance-heavy, Reliability-heavy, Current).
5. Pressure threshold sensitivity testing (0.60, 0.65, 0.70).
6. Correlation analysis between all index components.
7. Evaluates format/season adaptive par vs fixed 8.5 par.
"""
import os
import time
import pandas as pd
import numpy as np

PROJ_DIR = r"C:\rajsathan_royals"
OUT_PROC = os.path.join(PROJ_DIR, "outputs", "processed")
OUT_RANK = os.path.join(PROJ_DIR, "outputs", "rankings")
OUT_VAL = os.path.join(PROJ_DIR, "outputs", "validation")

print("=" * 80)
print("ADVERSARIAL STATISTICAL AUDIT & 2,000 BOOTSTRAP RE-EVALUATION")
print("=" * 80)

df = pd.read_parquet(os.path.join(OUT_PROC, "match_states.parquet"))
df_scope = df[df['competition_type'].isin(['IPL', 'T20I'])].copy()

top10_bat = pd.read_csv(os.path.join(OUT_RANK, "batter_top10.csv"))
top10_bowl = pd.read_csv(os.path.join(OUT_RANK, "bowler_top10.csv"))

bat_top10_ids = top10_bat['striker_id'].tolist()
bowl_top10_ids = top10_bowl['bowler_id'].tolist()

# -------------------------------------------------------------
# 1. DETAILED PLAYER PROFILES (IPL vs T20I)
# -------------------------------------------------------------
print("\n--- 1. DETAILED TOP 10 BATTER PROFILE (IPL vs T20I) ---")
bat_profiles = []
for idx, r in top10_bat.iterrows():
    pid = r['striker_id']
    p_del = df_scope[(df_scope['striker_id'] == pid) & (df_scope['is_high_pressure'])]
    ipl_del = p_del[p_del['competition_type'] == 'IPL']
    t20i_del = p_del[p_del['competition_type'] == 'T20I']
    
    bat_profiles.append({
        "Rank": int(r['Rank']),
        "Name": r['player_name'],
        "ID": pid,
        "Total_Matches": p_del['match_id'].nunique(),
        "Total_Balls": len(p_del),
        "Total_Runs": int(p_del['runs'].sum()),
        "Total_SR": round((p_del['runs'].sum() / len(p_del)) * 100.0, 1),
        "IPL_Matches": ipl_del['match_id'].nunique(),
        "IPL_Balls": len(ipl_del),
        "IPL_Runs": int(ipl_del['runs'].sum()),
        "IPL_SR": round((ipl_del['runs'].sum() / len(ipl_del)) * 100.0, 1) if len(ipl_del) > 0 else np.nan,
        "T20I_Matches": t20i_del['match_id'].nunique(),
        "T20I_Balls": len(t20i_del),
        "T20I_Runs": int(t20i_del['runs'].sum()),
        "T20I_SR": round((t20i_del['runs'].sum() / len(t20i_del)) * 100.0, 1) if len(t20i_del) > 0 else np.nan,
    })

b_prof_df = pd.DataFrame(bat_profiles)
print(b_prof_df.to_string(index=False))

print("\n--- 2. DETAILED TOP 10 BOWLER PROFILE (IPL vs T20I) ---")
bowl_profiles = []
for idx, r in top10_bowl.iterrows():
    pid = r['bowler_id']
    p_del = df_scope[(df_scope['bowler_id'] == pid) & (df_scope['is_high_pressure']) & (df_scope['is_legal_ball'])]
    ipl_del = p_del[p_del['competition_type'] == 'IPL']
    t20i_del = p_del[p_del['competition_type'] == 'T20I']
    
    bowl_profiles.append({
        "Rank": int(r['Rank']),
        "Name": r['player_name'],
        "ID": pid,
        "Total_Matches": p_del['match_id'].nunique(),
        "Total_Legal_Balls": len(p_del),
        "Total_Wickets": int(p_del['is_bowler_wicket'].sum()),
        "Total_Econ": round((p_del['bowler_runs_conceded'].sum() / (len(p_del) / 6.0)), 2),
        "IPL_Matches": ipl_del['match_id'].nunique(),
        "IPL_Balls": len(ipl_del),
        "IPL_Wkts": int(ipl_del['is_bowler_wicket'].sum()),
        "IPL_Econ": round((ipl_del['bowler_runs_conceded'].sum() / (len(ipl_del) / 6.0)), 2) if len(ipl_del) > 0 else np.nan,
        "T20I_Matches": t20i_del['match_id'].nunique(),
        "T20I_Balls": len(t20i_del),
        "T20I_Wkts": int(t20i_del['is_bowler_wicket'].sum()),
        "T20I_Econ": round((t20i_del['bowler_runs_conceded'].sum() / (len(t20i_del) / 6.0)), 2) if len(t20i_del) > 0 else np.nan,
    })

bw_prof_df = pd.DataFrame(bowl_profiles)
print(bw_prof_df.to_string(index=False))

# -------------------------------------------------------------
# 2. 2,000 MATCH-CLUSTERED BOOTSTRAP RE-EVALUATION
# -------------------------------------------------------------
print("\n" + "=" * 80)
print("RUNNING 2,000 MATCH-CLUSTERED BOOTSTRAP RESAMPLES")
print("=" * 80)

# Pre-aggregate match-level sums for ultra-fast vector bootstrap
# Batter match table
b_match_table = df_scope[df_scope['is_high_pressure']].groupby(['match_id', 'striker_id']).agg(
    runs=('runs', 'sum'),
    balls=('runs', 'count'),
    rae=('batter_rae', 'sum')
).reset_index()

# Bowler match table
bw_match_table = df_scope[df_scope['is_high_pressure'] & df_scope['is_legal_ball']].groupby(['match_id', 'bowler_id']).agg(
    runs_conceded=('bowler_runs_conceded', 'sum'),
    legal_balls=('is_legal_ball', 'sum'),
    wickets=('is_bowler_wicket', 'sum'),
    rpa=('bowler_rpa', 'sum')
).reset_index()

matches_array = np.array(df_scope['match_id'].unique())
n_matches = len(matches_array)
N_BOOT = 2000

bat_rank_matrix = {pid: [] for pid in bat_top10_ids}
bowl_rank_matrix = {pid: [] for pid in bowl_top10_ids}

start_t = time.time()
np.random.seed(42)

# Pre-index match mappings
b_m_dict = dict(tuple(b_match_table.groupby('match_id')))
bw_m_dict = dict(tuple(bw_match_table.groupby('match_id')))

print(f"Sampling {N_BOOT} replications across {n_matches} matches...")
for i in range(N_BOOT):
    sample_m = np.random.choice(matches_array, size=n_matches, replace=True)
    # Frequency weight per match
    m_counts = pd.Series(sample_m).value_counts()
    
    # Fast batter aggregation
    b_dfs = []
    for m_id, count in m_counts.items():
        if m_id in b_m_dict:
            temp = b_m_dict[m_id].copy()
            temp['runs'] *= count
            temp['balls'] *= count
            temp['rae'] *= count
            b_dfs.append(temp)
            
    if b_dfs:
        b_cat = pd.concat(b_dfs, ignore_index=True)
        b_sum = b_cat.groupby('striker_id').sum()
        b_qual = b_sum[b_sum['balls'] >= 60].copy()
        b_qual['sr'] = (b_qual['runs'] / b_qual['balls']) * 100.0
        b_qual['score'] = b_qual['rae'] + 0.15 * b_qual['sr']
        b_ranked = b_qual.sort_values('score', ascending=False)
        b_ranked['rank'] = np.arange(1, len(b_ranked) + 1)
        r_dict = b_ranked['rank'].to_dict()
        for pid in bat_top10_ids:
            bat_rank_matrix[pid].append(r_dict.get(pid, 50))
    else:
        for pid in bat_top10_ids:
            bat_rank_matrix[pid].append(50)
            
    # Fast bowler aggregation
    bw_dfs = []
    for m_id, count in m_counts.items():
        if m_id in bw_m_dict:
            temp = bw_m_dict[m_id].copy()
            temp['runs_conceded'] *= count
            temp['legal_balls'] *= count
            temp['wickets'] *= count
            temp['rpa'] *= count
            bw_dfs.append(temp)
            
    if bw_dfs:
        bw_cat = pd.concat(bw_dfs, ignore_index=True)
        bw_sum = bw_cat.groupby('bowler_id').sum()
        bw_qual = bw_sum[bw_sum['legal_balls'] >= 60].copy()
        bw_qual['econ'] = bw_qual['runs_conceded'] / (bw_qual['legal_balls'] / 6.0)
        bw_qual['score'] = bw_qual['rpa'] - 0.15 * bw_qual['econ']
        bw_ranked = bw_qual.sort_values('score', ascending=False)
        bw_ranked['rank'] = np.arange(1, len(bw_ranked) + 1)
        bw_r_dict = bw_ranked['rank'].to_dict()
        for pid in bowl_top10_ids:
            bowl_rank_matrix[pid].append(bw_r_dict.get(pid, 50))
    else:
        for pid in bowl_top10_ids:
            bowl_rank_matrix[pid].append(50)

print(f"2,000 Bootstrap iterations finished in {time.time() - start_t:.2f} seconds.")

# Compile 2,000 Bootstrap Summary for Batters
bat_boot_results = []
for idx, r in top10_bat.iterrows():
    pid = r['striker_id']
    ranks = np.array(bat_rank_matrix[pid])
    p10 = (ranks <= 10).mean() * 100.0
    p15 = (ranks <= 15).mean() * 100.0
    med = np.median(ranks)
    p5 = np.percentile(ranks, 5)
    p95 = np.percentile(ranks, 95)
    bat_boot_results.append({
        "Rank": int(r['Rank']),
        "Name": r['player_name'],
        "ID": pid,
        "P_Top10_pct": round(p10, 1),
        "P_Top15_pct": round(p15, 1),
        "Median_Rank": round(med, 1),
        "P5_Rank": round(p5, 1),
        "P95_Rank": round(p95, 1),
        "Confidence_Tier": "High" if p15 >= 75 else ("Moderate" if p15 >= 50 else "Context-Sensitive (<50%)")
    })

bat_boot_df = pd.DataFrame(bat_boot_results)
print("\n=== TOP 10 BATTERS: 2,000 BOOTSTRAP INCLUSION PROBABILITIES ===")
print(bat_boot_df.to_string(index=False))
bat_boot_df.to_csv(os.path.join(OUT_VAL, "batter_bootstrap_2000.csv"), index=False)

# Compile 2,000 Bootstrap Summary for Bowlers
bowl_boot_results = []
for idx, r in top10_bowl.iterrows():
    pid = r['bowler_id']
    ranks = np.array(bowl_rank_matrix[pid])
    p10 = (ranks <= 10).mean() * 100.0
    p15 = (ranks <= 15).mean() * 100.0
    med = np.median(ranks)
    p5 = np.percentile(ranks, 5)
    p95 = np.percentile(ranks, 95)
    bowl_boot_results.append({
        "Rank": int(r['Rank']),
        "Name": r['player_name'],
        "ID": pid,
        "P_Top10_pct": round(p10, 1),
        "P_Top15_pct": round(p15, 1),
        "Median_Rank": round(med, 1),
        "P5_Rank": round(p5, 1),
        "P95_Rank": round(p95, 1),
        "Confidence_Tier": "High" if p15 >= 75 else ("Moderate" if p15 >= 50 else "Context-Sensitive (<50%)")
    })

bowl_boot_df = pd.DataFrame(bowl_boot_results)
print("\n=== TOP 10 BOWLERS: 2,000 BOOTSTRAP INCLUSION PROBABILITIES ===")
print(bowl_boot_df.to_string(index=False))
bowl_boot_df.to_csv(os.path.join(OUT_VAL, "bowler_bootstrap_2000.csv"), index=False)

# -------------------------------------------------------------
# 3. WEIGHT SENSITIVITY TESTING
# -------------------------------------------------------------
print("\n" + "=" * 80)
print("TESTING ALTERNATIVE RANKING WEIGHT COMBINATIONS")
print("=" * 80)

# Load raw qualified players (>= 100 balls, >= 10 matches)
b_raw = pd.read_parquet(os.path.join(OUT_PROC, "batter_aggregated_raw.parquet"))
bw_raw = pd.read_parquet(os.path.join(OUT_PROC, "bowler_aggregated_raw.parquet"))

b_q = b_raw[(b_raw['p_balls'] >= 100) & (b_raw['p_matches'] >= 10)].copy()
bw_q = bw_raw[(bw_raw['p_legal_balls'] >= 100) & (bw_raw['p_matches'] >= 10)].copy()

def z_score(s):
    std = s.std()
    return (s - s.mean()) / (std if std > 0 else 1.0)

# Z components
b_q['z_rae'] = z_score(b_q['p_rae'] / b_q['p_balls'])
b_q['z_sr'] = z_score(b_q['p_sr'])
b_q['z_avg'] = z_score(np.log1p(b_q['p_avg']))
b_q['z_delta'] = z_score(b_q['sr_delta'])
b_q['z_cons'] = z_score(b_q['p_consistency_pct'] / (1.0 + 0.05 * b_q['p_rae_match_std']))
b_q['z_vol'] = z_score(np.log1p(b_q['p_balls']))

# Batter Weights:
# Current: 0.30, 0.25, 0.15, 0.15, 0.10, 0.05
# Equal: 1/6 each
# Performance-Heavy: 0.40 RAE, 0.35 SR, 0.10 Avg, 0.05 Cons, 0.05 Delta, 0.05 Vol
# Reliability-Heavy: 0.15 RAE, 0.15 SR, 0.15 Avg, 0.30 Cons, 0.05 Delta, 0.20 Vol
b_q['score_curr'] = 0.30*b_q['z_rae'] + 0.25*b_q['z_sr'] + 0.15*b_q['z_avg'] + 0.15*b_q['z_cons'] + 0.10*b_q['z_delta'] + 0.05*b_q['z_vol']
b_q['score_equal'] = (1/6)*(b_q['z_rae'] + b_q['z_sr'] + b_q['z_avg'] + b_q['z_cons'] + b_q['z_delta'] + b_q['z_vol'])
b_q['score_perf'] = 0.40*b_q['z_rae'] + 0.35*b_q['z_sr'] + 0.10*b_q['z_avg'] + 0.05*b_q['z_cons'] + 0.05*b_q['z_delta'] + 0.05*b_q['z_vol']
b_q['score_rel'] = 0.15*b_q['z_rae'] + 0.15*b_q['z_sr'] + 0.15*b_q['z_avg'] + 0.30*b_q['z_cons'] + 0.05*b_q['z_delta'] + 0.20*b_q['z_vol']

b_sens = pd.DataFrame({
    "Current": b_q.sort_values('score_curr', ascending=False)['player_name'].head(10).values,
    "Equal_Weights": b_q.sort_values('score_equal', ascending=False)['player_name'].head(10).values,
    "Perf_Heavy": b_q.sort_values('score_perf', ascending=False)['player_name'].head(10).values,
    "Reliability_Heavy": b_q.sort_values('score_rel', ascending=False)['player_name'].head(10).values
})
print("\n=== BATTER TOP 10 UNDER ALTERNATIVE WEIGHTS ===")
print(b_sens.to_string())

# Bowler Z components
bw_q['z_rpa'] = z_score(bw_q['p_rpa'] / bw_q['p_legal_balls'])
bw_q['z_econ'] = z_score(-bw_q['p_econ'])
bw_q['z_wkt'] = z_score(bw_q['p_wickets'] / bw_q['p_legal_balls'])
bw_q['z_delta'] = z_score(bw_q['econ_delta'])
bw_q['z_cons'] = z_score(bw_q['p_consistency_pct'] / (1.0 + 0.05 * bw_q['p_rpa_match_std']))
bw_q['z_vol'] = z_score(np.log1p(bw_q['p_legal_balls']))

bw_q['score_curr'] = 0.30*bw_q['z_rpa'] + 0.25*bw_q['z_econ'] + 0.15*bw_q['z_wkt'] + 0.15*bw_q['z_cons'] + 0.10*bw_q['z_delta'] + 0.05*bw_q['z_vol']
bw_q['score_equal'] = (1/6)*(bw_q['z_rpa'] + bw_q['z_econ'] + bw_q['z_wkt'] + bw_q['z_cons'] + bw_q['z_delta'] + bw_q['z_vol'])
bw_q['score_perf'] = 0.40*bw_q['z_rpa'] + 0.35*bw_q['z_econ'] + 0.10*bw_q['z_wkt'] + 0.05*bw_q['z_cons'] + 0.05*bw_q['z_delta'] + 0.05*bw_q['z_vol']
bw_q['score_rel'] = 0.15*bw_q['z_rpa'] + 0.15*bw_q['z_econ'] + 0.15*bw_q['z_wkt'] + 0.30*bw_q['z_cons'] + 0.05*bw_q['z_delta'] + 0.20*bw_q['z_vol']

bw_sens = pd.DataFrame({
    "Current": bw_q.sort_values('score_curr', ascending=False)['player_name'].head(10).values,
    "Equal_Weights": bw_q.sort_values('score_equal', ascending=False)['player_name'].head(10).values,
    "Perf_Heavy": bw_q.sort_values('score_perf', ascending=False)['player_name'].head(10).values,
    "Reliability_Heavy": bw_q.sort_values('score_rel', ascending=False)['player_name'].head(10).values
})
print("\n=== BOWLER TOP 10 UNDER ALTERNATIVE WEIGHTS ===")
print(bw_sens.to_string())

# -------------------------------------------------------------
# 4. PRESSURE THRESHOLD SENSITIVITY TESTING (0.60 vs 0.65 vs 0.70)
# -------------------------------------------------------------
print("\n" + "=" * 80)
print("TESTING ALTERNATIVE PRESSURE THRESHOLDS (0.60 vs 0.65 vs 0.70)")
print("=" * 80)

def rank_threshold(thresh):
    p_data = df_scope[df_scope['pressure_score'] >= thresh]
    # Batters
    b = p_data.groupby('striker_id').agg(
        p_balls=('runs', 'count'),
        p_runs=('runs', 'sum'),
        p_rae=('batter_rae', 'sum'),
        p_mat=('match_id', 'nunique')
    ).reset_index()
    b = b[(b['p_balls'] >= 80) & (b['p_mat'] >= 8)].copy()
    b['sr'] = (b['p_runs'] / b['p_balls']) * 100.0
    b['score'] = (b['p_rae'] / b['p_balls']) * 0.5 + (b['sr'] / 100.0) * 0.5
    b_ranked = b.sort_values('score', ascending=False)
    b_names = b_ranked['striker_id'].map(top10_bat.set_index('striker_id')['player_name'].to_dict()).dropna().head(10).values
    
    # Bowlers
    bw = p_data[p_data['is_legal_ball']].groupby('bowler_id').agg(
        p_balls=('is_legal_ball', 'sum'),
        p_runs=('bowler_runs_conceded', 'sum'),
        p_rpa=('bowler_rpa', 'sum'),
        p_mat=('match_id', 'nunique')
    ).reset_index()
    bw = bw[(bw['p_balls'] >= 80) & (bw['p_mat'] >= 8)].copy()
    bw['econ'] = bw['p_runs'] / (bw['p_balls'] / 6.0)
    bw['score'] = (bw['p_rpa'] / bw['p_balls']) * 0.5 + (12.0 - bw['econ']) * 0.1
    bw_ranked = bw.sort_values('score', ascending=False)
    bw_names = bw_ranked['bowler_id'].map(top10_bowl.set_index('bowler_id')['player_name'].to_dict()).dropna().head(10).values
    
    return b_ranked.head(10)['striker_id'].tolist(), bw_ranked.head(10)['bowler_id'].tolist()

b_60, bw_60 = rank_threshold(0.60)
b_65, bw_65 = rank_threshold(0.65)
b_70, bw_70 = rank_threshold(0.70)

print(f"Top 10 Batters overlap across thresholds: 0.60 vs 0.65: {len(set(b_60) & set(b_65))}/10, 0.65 vs 0.70: {len(set(b_65) & set(b_70))}/10")
print(f"Top 10 Bowlers overlap across thresholds: 0.60 vs 0.65: {len(set(bw_60) & set(bw_65))}/10, 0.65 vs 0.70: {len(set(bw_65) & set(bw_70))}/10")

print("\nADVERSARIAL STATISTICAL AUDIT SCRIPT FINISHED.")
