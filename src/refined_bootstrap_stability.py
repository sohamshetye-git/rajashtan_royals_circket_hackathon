"""
Re-run bootstrap stability on the refined Top 10 with robust sample sizes
"""
import os
import pandas as pd
import numpy as np

PROJ_DIR = r"C:\rajsathan_royals"
OUT_PROC = os.path.join(PROJ_DIR, "outputs", "processed")
OUT_VAL = os.path.join(PROJ_DIR, "outputs", "validation")
OUT_RANK = os.path.join(PROJ_DIR, "outputs", "rankings")

df = pd.read_parquet(os.path.join(OUT_PROC, "match_states.parquet"))
df_scope = df[df['competition_type'].isin(['IPL', 'T20I'])].copy()

top10_batters = pd.read_csv(os.path.join(OUT_RANK, "batter_top10.csv"))
top10_bowlers = pd.read_csv(os.path.join(OUT_RANK, "bowler_top10.csv"))

bat_top10_ids = set(top10_batters['striker_id'])
bowl_top10_ids = set(top10_bowlers['bowler_id'])

matches_list = df_scope['match_id'].unique()
np.random.seed(42)
N_BOOT = 200

bat_ranks_record = {pid: [] for pid in bat_top10_ids}
bowl_ranks_record = {pid: [] for pid in bowl_top10_ids}

print(f"Running {N_BOOT} match-clustered bootstrap iterations on refined Top 10...")
for b in range(N_BOOT):
    sample_mids = np.random.choice(matches_list, size=len(matches_list), replace=True)
    boot_deliveries = df_scope[df_scope['match_id'].isin(sample_mids)]
    boot_p = boot_deliveries[boot_deliveries['is_high_pressure']]
    
    # Batters
    b_agg = boot_p.groupby('striker_id').agg(
        p_balls=('runs', 'count'),
        p_runs=('runs', 'sum'),
        p_rae=('batter_rae', 'sum')
    ).reset_index()
    b_agg = b_agg[b_agg['p_balls'] >= 60]
    b_agg['sr'] = (b_agg['p_runs'] / b_agg['p_balls']) * 100.0
    b_agg['score'] = b_agg['p_rae'] + 0.15 * b_agg['sr']
    b_agg = b_agg.sort_values('score', ascending=False).reset_index(drop=True)
    b_agg['rank'] = np.arange(1, len(b_agg) + 1)
    
    b_rank_dict = b_agg.set_index('striker_id')['rank'].to_dict()
    for pid in bat_top10_ids:
        bat_ranks_record[pid].append(b_rank_dict.get(pid, 50))
        
    # Bowlers
    bw_agg = boot_p.groupby('bowler_id').agg(
        p_balls=('is_legal_ball', 'sum'),
        p_runs=('bowler_runs_conceded', 'sum'),
        p_rpa=('bowler_rpa', 'sum')
    ).reset_index()
    bw_agg = bw_agg[bw_agg['p_balls'] >= 60]
    bw_agg['score'] = bw_agg['p_rpa'] - 0.15 * (bw_agg['p_runs'] / (bw_agg['p_balls'] / 6.0))
    bw_agg = bw_agg.sort_values('score', ascending=False).reset_index(drop=True)
    bw_agg['rank'] = np.arange(1, len(bw_agg) + 1)
    
    bw_rank_dict = bw_agg.set_index('bowler_id')['rank'].to_dict()
    for pid in bowl_top10_ids:
        bowl_ranks_record[pid].append(bw_rank_dict.get(pid, 50))

bat_stability = []
for idx, row in top10_batters.iterrows():
    pid = row['striker_id']
    ranks = bat_ranks_record[pid]
    top15_freq = (np.array(ranks) <= 15).mean() * 100.0
    med_rank = np.median(ranks)
    iqr = np.percentile(ranks, 75) - np.percentile(ranks, 25)
    bat_stability.append({
        "Rank": row['Rank'],
        "player_name": row['player_name'],
        "striker_id": pid,
        "median_bootstrap_rank": med_rank,
        "top15_appearance_pct": round(top15_freq, 1),
        "rank_iqr": iqr,
        "confidence_tier": "High" if top15_freq >= 75 else ("Moderate" if top15_freq >= 50 else "Context-Sensitive")
    })

bat_stab_df = pd.DataFrame(bat_stability)
print("\nBATTER TOP 10 REFINED BOOTSTRAP STABILITY:")
print(bat_stab_df.to_string(index=False))
bat_stab_df.to_csv(os.path.join(OUT_VAL, "batter_stability.csv"), index=False)

bowl_stability = []
for idx, row in top10_bowlers.iterrows():
    pid = row['bowler_id']
    ranks = bowl_ranks_record[pid]
    top15_freq = (np.array(ranks) <= 15).mean() * 100.0
    med_rank = np.median(ranks)
    iqr = np.percentile(ranks, 75) - np.percentile(ranks, 25)
    bowl_stability.append({
        "Rank": row['Rank'],
        "player_name": row['player_name'],
        "bowler_id": pid,
        "median_bootstrap_rank": med_rank,
        "top15_appearance_pct": round(top15_freq, 1),
        "rank_iqr": iqr,
        "confidence_tier": "High" if top15_freq >= 75 else ("Moderate" if top15_freq >= 50 else "Context-Sensitive")
    })

bowl_stab_df = pd.DataFrame(bowl_stability)
print("\nBOWLER TOP 10 REFINED BOOTSTRAP STABILITY:")
print(bowl_stab_df.to_string(index=False))
bowl_stab_df.to_csv(os.path.join(OUT_VAL, "bowler_stability.csv"), index=False)
