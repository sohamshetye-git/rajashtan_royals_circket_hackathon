"""
Fast Vectorized Adversarial Statistical Audit Script
Using pure numpy 2D array matrix multiplication for 2,000 bootstrap iterations.
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
print("FAST ADVERSARIAL STATISTICAL AUDIT & 2,000 BOOTSTRAP")
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
        "Total_Mat": p_del['match_id'].nunique(),
        "Total_Balls": len(p_del),
        "Total_Runs": int(p_del['runs'].sum()),
        "Total_SR": round((p_del['runs'].sum() / len(p_del)) * 100.0, 1),
        "IPL_Mat": ipl_del['match_id'].nunique(),
        "IPL_Balls": len(ipl_del),
        "IPL_Runs": int(ipl_del['runs'].sum()),
        "IPL_SR": round((ipl_del['runs'].sum() / len(ipl_del)) * 100.0, 1) if len(ipl_del) > 0 else np.nan,
        "T20I_Mat": t20i_del['match_id'].nunique(),
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
        "Total_Mat": p_del['match_id'].nunique(),
        "Total_Balls": len(p_del),
        "Total_Wkts": int(p_del['is_bowler_wicket'].sum()),
        "Total_Econ": round((p_del['bowler_runs_conceded'].sum() / (len(p_del) / 6.0)), 2),
        "IPL_Mat": ipl_del['match_id'].nunique(),
        "IPL_Balls": len(ipl_del),
        "IPL_Wkts": int(ipl_del['is_bowler_wicket'].sum()),
        "IPL_Econ": round((ipl_del['bowler_runs_conceded'].sum() / (len(ipl_del) / 6.0)), 2) if len(ipl_del) > 0 else np.nan,
        "T20I_Mat": t20i_del['match_id'].nunique(),
        "T20I_Balls": len(t20i_del),
        "T20I_Wkts": int(t20i_del['is_bowler_wicket'].sum()),
        "T20I_Econ": round((t20i_del['bowler_runs_conceded'].sum() / (len(t20i_del) / 6.0)), 2) if len(t20i_del) > 0 else np.nan,
    })

bw_prof_df = pd.DataFrame(bowl_profiles)
print(bw_prof_df.to_string(index=False))

# -------------------------------------------------------------
# 2. MATRIX VECTORIZED 2,000 BOOTSTRAP ITERATIONS
# -------------------------------------------------------------
print("\n" + "=" * 80)
print("STARTING VECTORIZED 2,000 BOOTSTRAP ITERATIONS...")
print("=" * 80)

# Build pivot tables: rows = match_id, cols = player_id
# 1. Batters
b_piv_runs = df_scope[df_scope['is_high_pressure']].pivot_table(index='match_id', columns='striker_id', values='runs', aggfunc='sum', fill_value=0)
b_piv_balls = df_scope[df_scope['is_high_pressure']].pivot_table(index='match_id', columns='striker_id', values='runs', aggfunc='count', fill_value=0)
b_piv_rae = df_scope[df_scope['is_high_pressure']].pivot_table(index='match_id', columns='striker_id', values='batter_rae', aggfunc='sum', fill_value=0)

b_players = b_piv_runs.columns.values
b_runs_mat = b_piv_runs.values # shape: (N_matches, N_batters)
b_balls_mat = b_piv_balls.values
b_rae_mat = b_piv_rae.values
N_matches = b_runs_mat.shape[0]

# 2. Bowlers
bw_piv_runs = df_scope[df_scope['is_high_pressure'] & df_scope['is_legal_ball']].pivot_table(index='match_id', columns='bowler_id', values='bowler_runs_conceded', aggfunc='sum', fill_value=0)
bw_piv_balls = df_scope[df_scope['is_high_pressure'] & df_scope['is_legal_ball']].pivot_table(index='match_id', columns='bowler_id', values='is_legal_ball', aggfunc='sum', fill_value=0)
bw_piv_rpa = df_scope[df_scope['is_high_pressure'] & df_scope['is_legal_ball']].pivot_table(index='match_id', columns='bowler_id', values='bowler_rpa', aggfunc='sum', fill_value=0)

# Align matches between batter and bowler matrices
all_mids = df_scope['match_id'].unique()
mid_to_idx = {m: i for i, m in enumerate(all_mids)}

N_TOTAL_MATCHES = len(all_mids)
N_BOOT = 2000

print(f"Total Unique Matches: {N_TOTAL_MATCHES}. Re-indexing pivot tables to common match index...")
b_runs_mat = b_piv_runs.reindex(all_mids, fill_value=0).values
b_balls_mat = b_piv_balls.reindex(all_mids, fill_value=0).values
b_rae_mat = b_piv_rae.reindex(all_mids, fill_value=0).values

bw_runs_mat = bw_piv_runs.reindex(all_mids, fill_value=0).values
bw_balls_mat = bw_piv_balls.reindex(all_mids, fill_value=0).values
bw_rpa_mat = bw_piv_rpa.reindex(all_mids, fill_value=0).values
bw_players = bw_piv_runs.columns.values

t0 = time.time()
np.random.seed(42)

# Generate bootstrap match counts: Multinomial distribution over matches
# shape: (N_BOOT, N_TOTAL_MATCHES)
boot_weights = np.random.multinomial(N_TOTAL_MATCHES, [1.0/N_TOTAL_MATCHES]*N_TOTAL_MATCHES, size=N_BOOT)
print(f"Generated bootstrap sample weights matrix ({boot_weights.shape}) in {time.time()-t0:.2f}s")

# Vectorized Matrix Multiplication!
# boot_weights: (2000, M) @ mat: (M, P) -> (2000, P)
boot_b_runs = boot_weights @ b_runs_mat
boot_b_balls = boot_weights @ b_balls_mat
boot_b_rae = boot_weights @ b_rae_mat

boot_bw_runs = boot_weights @ bw_runs_mat
boot_bw_balls = boot_weights @ bw_balls_mat
boot_bw_rpa = boot_weights @ bw_rpa_mat

print(f"Matrix products computed in {time.time()-t0:.2f}s! Calculating rankings across 2,000 iterations...")

# Batter Scores across 2,000 iterations
# score = rae + 0.15 * (runs / balls * 100)
# mask for balls >= 60
valid_b_mask = boot_b_balls >= 60
with np.errstate(divide='ignore', invalid='ignore'):
    boot_b_sr = np.where(valid_b_mask, (boot_b_runs / boot_b_balls) * 100.0, 0.0)
    boot_b_score = np.where(valid_b_mask, boot_b_rae + 0.15 * boot_b_sr, -9999.0)

# Bowler Scores across 2,000 iterations
# score = rpa - 0.15 * (runs / (balls / 6))
valid_bw_mask = boot_bw_balls >= 60
with np.errstate(divide='ignore', invalid='ignore'):
    boot_bw_econ = np.where(valid_bw_mask, boot_bw_runs / (boot_bw_balls / 6.0), 99.0)
    boot_bw_score = np.where(valid_bw_mask, boot_bw_rpa - 0.15 * boot_bw_econ, -9999.0)

# Rank calculation: argsort in descending order
# argsort(-score, axis=1) gives ranking order
b_ranks = np.argsort(np.argsort(-boot_b_score, axis=1), axis=1) + 1 # 1-indexed ranks
bw_ranks = np.argsort(np.argsort(-boot_bw_score, axis=1), axis=1) + 1

# Map player IDs to column indices
b_id_to_col = {pid: i for i, pid in enumerate(b_players)}
bw_id_to_col = {pid: i for i, pid in enumerate(bw_players)}

# Compile Batter Bootstrap Summary
bat_boot_results = []
for idx, r in top10_bat.iterrows():
    pid = r['striker_id']
    col = b_id_to_col[pid]
    p_ranks = b_ranks[:, col]
    # Check if qualified in that iteration
    # If score == -9999, rank will be pushed to the back (> 50)
    p10 = (p_ranks <= 10).mean() * 100.0
    p15 = (p_ranks <= 15).mean() * 100.0
    med = np.median(p_ranks)
    p5 = np.percentile(p_ranks, 5)
    p95 = np.percentile(p_ranks, 95)
    bat_boot_results.append({
        "Rank": int(r['Rank']),
        "Name": r['player_name'],
        "ID": pid,
        "P_Top10_pct": round(p10, 1),
        "P_Top15_pct": round(p15, 1),
        "Median_Rank": round(med, 1),
        "P5_Rank": round(p5, 1),
        "P95_Rank": round(p95, 1),
        "Confidence_Tier": "High (>=75%)" if p15 >= 75 else ("Moderate (50-74%)" if p15 >= 50 else "Context-Sensitive (<50%)")
    })

bat_boot_df = pd.DataFrame(bat_boot_results)
print("\n=== TOP 10 BATTERS: 2,000 BOOTSTRAP INCLUSION PROBABILITIES ===")
print(bat_boot_df.to_string(index=False))
bat_boot_df.to_csv(os.path.join(OUT_VAL, "batter_bootstrap_2000.csv"), index=False)

# Compile Bowler Bootstrap Summary
bowl_boot_results = []
for idx, r in top10_bowl.iterrows():
    pid = r['bowler_id']
    col = bw_id_to_col[pid]
    p_ranks = bw_ranks[:, col]
    p10 = (p_ranks <= 10).mean() * 100.0
    p15 = (p_ranks <= 15).mean() * 100.0
    med = np.median(p_ranks)
    p5 = np.percentile(p_ranks, 5)
    p95 = np.percentile(p_ranks, 95)
    bowl_boot_results.append({
        "Rank": int(r['Rank']),
        "Name": r['player_name'],
        "ID": pid,
        "P_Top10_pct": round(p10, 1),
        "P_Top15_pct": round(p15, 1),
        "Median_Rank": round(med, 1),
        "P5_Rank": round(p5, 1),
        "P95_Rank": round(p95, 1),
        "Confidence_Tier": "High (>=75%)" if p15 >= 75 else ("Moderate (50-74%)" if p15 >= 50 else "Context-Sensitive (<50%)")
    })

bowl_boot_df = pd.DataFrame(bowl_boot_results)
print("\n=== TOP 10 BOWLERS: 2,000 BOOTSTRAP INCLUSION PROBABILITIES ===")
print(bowl_boot_df.to_string(index=False))
bowl_boot_df.to_csv(os.path.join(OUT_VAL, "bowler_bootstrap_2000.csv"), index=False)

# -------------------------------------------------------------
# 3. WEIGHT SENSITIVITY TESTING
# -------------------------------------------------------------
print("\n" + "=" * 80)
print("TESTING ALTERNATIVE RANKING WEIGHTS (ROBUST QUALIFIED COHORT)")
print("=" * 80)

b_raw = pd.read_parquet(os.path.join(OUT_PROC, "batter_aggregated_raw.parquet"))
bw_raw = pd.read_parquet(os.path.join(OUT_PROC, "bowler_aggregated_raw.parquet"))

b_q = b_raw[(b_raw['p_balls'] >= 100) & (b_raw['p_matches'] >= 10)].copy()
bw_q = bw_raw[(bw_raw['p_legal_balls'] >= 100) & (bw_raw['p_matches'] >= 10)].copy()

def z_score(s):
    std = s.std()
    return (s - s.mean()) / (std if std > 0 else 1.0)

b_q['z_rae'] = z_score(b_q['p_rae'] / b_q['p_balls'])
b_q['z_sr'] = z_score(b_q['p_sr'])
b_q['z_avg'] = z_score(np.log1p(b_q['p_avg']))
b_q['z_delta'] = z_score(b_q['sr_delta'])
b_q['z_cons'] = z_score(b_q['p_consistency_pct'] / (1.0 + 0.05 * b_q['p_rae_match_std']))
b_q['z_vol'] = z_score(np.log1p(b_q['p_balls']))

b_q['Current'] = 0.30*b_q['z_rae'] + 0.25*b_q['z_sr'] + 0.15*b_q['z_avg'] + 0.15*b_q['z_cons'] + 0.10*b_q['z_delta'] + 0.05*b_q['z_vol']
b_q['Equal_Weights'] = (1/6)*(b_q['z_rae'] + b_q['z_sr'] + b_q['z_avg'] + b_q['z_cons'] + b_q['z_delta'] + b_q['z_vol'])
b_q['Perf_Heavy'] = 0.40*b_q['z_rae'] + 0.35*b_q['z_sr'] + 0.10*b_q['z_avg'] + 0.05*b_q['z_cons'] + 0.05*b_q['z_delta'] + 0.05*b_q['z_vol']
b_q['Reliability_Heavy'] = 0.15*b_q['z_rae'] + 0.15*b_q['z_sr'] + 0.15*b_q['z_avg'] + 0.30*b_q['z_cons'] + 0.05*b_q['z_delta'] + 0.20*b_q['z_vol']

b_sens = pd.DataFrame({
    "Current": b_q.sort_values('Current', ascending=False)['player_name'].head(10).values,
    "Equal_Weights": b_q.sort_values('Equal_Weights', ascending=False)['player_name'].head(10).values,
    "Perf_Heavy": b_q.sort_values('Perf_Heavy', ascending=False)['player_name'].head(10).values,
    "Reliability_Heavy": b_q.sort_values('Reliability_Heavy', ascending=False)['player_name'].head(10).values
})
print("\n=== BATTER TOP 10 UNDER ALTERNATIVE WEIGHTS ===")
print(b_sens.to_string())

bw_q['z_rpa'] = z_score(bw_q['p_rpa'] / bw_q['p_legal_balls'])
bw_q['z_econ'] = z_score(-bw_q['p_econ'])
bw_q['z_wkt'] = z_score(bw_q['p_wickets'] / bw_q['p_legal_balls'])
bw_q['z_delta'] = z_score(bw_q['econ_delta'])
bw_q['z_cons'] = z_score(bw_q['p_consistency_pct'] / (1.0 + 0.05 * bw_q['p_rpa_match_std']))
bw_q['z_vol'] = z_score(np.log1p(bw_q['p_legal_balls']))

bw_q['Current'] = 0.30*bw_q['z_rpa'] + 0.25*bw_q['z_econ'] + 0.15*bw_q['z_wkt'] + 0.15*bw_q['z_cons'] + 0.10*bw_q['z_delta'] + 0.05*bw_q['z_vol']
bw_q['Equal_Weights'] = (1/6)*(bw_q['z_rpa'] + bw_q['z_econ'] + bw_q['z_wkt'] + bw_q['z_cons'] + bw_q['z_delta'] + bw_q['z_vol'])
bw_q['Perf_Heavy'] = 0.40*bw_q['z_rpa'] + 0.35*bw_q['z_econ'] + 0.10*bw_q['z_wkt'] + 0.05*bw_q['z_cons'] + 0.05*bw_q['z_delta'] + 0.05*bw_q['z_vol']
bw_q['Reliability_Heavy'] = 0.15*bw_q['z_rpa'] + 0.15*bw_q['z_econ'] + 0.15*bw_q['z_wkt'] + 0.30*bw_q['z_cons'] + 0.05*bw_q['z_delta'] + 0.20*bw_q['z_vol']

bw_sens = pd.DataFrame({
    "Current": bw_q.sort_values('Current', ascending=False)['player_name'].head(10).values,
    "Equal_Weights": bw_q.sort_values('Equal_Weights', ascending=False)['player_name'].head(10).values,
    "Perf_Heavy": bw_q.sort_values('Perf_Heavy', ascending=False)['player_name'].head(10).values,
    "Reliability_Heavy": bw_q.sort_values('Reliability_Heavy', ascending=False)['player_name'].head(10).values
})
print("\n=== BOWLER TOP 10 UNDER ALTERNATIVE WEIGHTS ===")
print(bw_sens.to_string())

print("\nAUDIT SCRIPT EXECUTION FINISHED SUCCESSFULLY.")
