"""
FAST COMPLETE BOOTSTRAP FOR TOP 20 CANDIDATES
Computes exact 2,000 match-clustered bootstrap distributions across all eligible candidates.
"""
import os
import pandas as pd
import numpy as np

PROJ_DIR = r"C:\rajsathan_royals"
OUT_VAL = os.path.join(PROJ_DIR, "outputs", "validation")
OUT_RANK = os.path.join(PROJ_DIR, "outputs", "rankings")

top20_b = pd.read_csv(os.path.join(OUT_RANK, "Top20_Pressure_Batters.csv"))
top20_bw = pd.read_csv(os.path.join(OUT_RANK, "Top20_Pressure_Bowlers.csv"))
df_clean = pd.read_parquet(os.path.join(PROJ_DIR, "outputs", "processed", "clean_deliveries.parquet"))
df_ms = pd.read_parquet(os.path.join(PROJ_DIR, "outputs", "processed", "match_states.parquet"))

df_clean['is_high_pressure'] = df_ms['is_high_pressure']
df_clean['batter_rae'] = df_clean['runs'] - df_ms['exp_runs_final']
df_clean['bowler_rpa'] = df_ms['exp_runs_final'] - df_clean['bowler_runs_conceded']

p_del = df_clean[df_clean['is_high_pressure']].copy()

# Pre-aggregate by match_id and player
match_b = p_del.groupby(['match_id', 'striker_id', 'striker_name']).agg(
    balls=('is_legal_ball', 'sum'),
    runs=('runs', 'sum'),
    rae=('batter_rae', 'sum')
).reset_index()

match_bw = p_del.groupby(['match_id', 'bowler_id', 'bowler_name']).agg(
    balls=('is_legal_ball', 'sum'),
    runs=('bowler_runs_conceded', 'sum'),
    rpa=('bowler_rpa', 'sum')
).reset_index()

unique_matches = df_clean['match_id'].unique()
n_m = len(unique_matches)
N_BOOT = 2000

# Pre-filter to candidate players who faced >= 100 balls overall
b_overall_balls = match_b.groupby('striker_id')['balls'].sum()
qual_b_ids = b_overall_balls[b_overall_balls >= 100].index

bw_overall_balls = match_bw.groupby('bowler_id')['balls'].sum()
qual_bw_ids = bw_overall_balls[bw_overall_balls >= 100].index

match_b_qual = match_b[match_b['striker_id'].isin(qual_b_ids)]
match_bw_qual = match_bw[match_bw['bowler_id'].isin(qual_bw_ids)]

# Create match x player matrices with fillna before and after reindex to guarantee zero NaNs
pivot_b_balls = match_b_qual.pivot(index='match_id', columns='striker_id', values='balls').fillna(0).reindex(index=unique_matches, fill_value=0)
pivot_b_runs = match_b_qual.pivot(index='match_id', columns='striker_id', values='runs').fillna(0).reindex(index=unique_matches, fill_value=0)
pivot_b_rae = match_b_qual.pivot(index='match_id', columns='striker_id', values='rae').fillna(0).reindex(index=unique_matches, fill_value=0)

pivot_bw_balls = match_bw_qual.pivot(index='match_id', columns='bowler_id', values='balls').fillna(0).reindex(index=unique_matches, fill_value=0)
pivot_bw_runs = match_bw_qual.pivot(index='match_id', columns='bowler_id', values='runs').fillna(0).reindex(index=unique_matches, fill_value=0)
pivot_bw_rpa = match_bw_qual.pivot(index='match_id', columns='bowler_id', values='rpa').fillna(0).reindex(index=unique_matches, fill_value=0)

b_ids = pivot_b_balls.columns.values
bw_ids = pivot_bw_balls.columns.values

np.random.seed(42)
weights = np.random.multinomial(n_m, np.ones(n_m)/n_m, size=N_BOOT)

print("Calculating 2,000 bootstrap iterations via matrix projection...")
boot_b_balls = weights @ pivot_b_balls.values
boot_b_runs = weights @ pivot_b_runs.values
boot_b_rae = weights @ pivot_b_rae.values

boot_bw_balls = weights @ pivot_bw_balls.values
boot_bw_runs = weights @ pivot_bw_runs.values
boot_bw_rpa = weights @ pivot_bw_rpa.values

# Scoring function:
# Batters: 0.5 * (RAE / balls) + 0.35 * (SR / 100)
with np.errstate(divide='ignore', invalid='ignore'):
    boot_b_sr = (boot_b_runs * 100.0) / np.maximum(boot_b_balls, 1)
    boot_b_score = (boot_b_rae / np.maximum(boot_b_balls, 1)) * 50.0 + (boot_b_sr / 100.0) * 35.0
    boot_b_score[boot_b_balls < 80] = -9999.0
    b_ranks_matrix = (-boot_b_score).argsort(axis=1).argsort(axis=1) + 1

    boot_bw_econ = (boot_bw_runs * 6.0) / np.maximum(boot_bw_balls, 1)
    boot_bw_score = (boot_bw_rpa / np.maximum(boot_bw_balls, 1)) * 50.0 - boot_bw_econ * 5.0
    boot_bw_score[boot_bw_balls < 80] = -9999.0
    bw_ranks_matrix = (-boot_bw_score).argsort(axis=1).argsort(axis=1) + 1

# Map back names
b_names = match_b[['striker_id', 'striker_name']].drop_duplicates().set_index('striker_id')['striker_name'].to_dict()
bw_names = match_bw[['bowler_id', 'bowler_name']].drop_duplicates().set_index('bowler_id')['bowler_name'].to_dict()

# Produce Bootstrap Results for Top 20 Batters
top_b_results = []
b_id_map = {pid: idx for idx, pid in enumerate(b_ids)}

for rank_idx, r in top20_b.iterrows():
    pname = r['Player']
    # find pid
    matching_pids = [pid for pid, name in b_names.items() if name == pname]
    if not matching_pids:
        continue
    pid = matching_pids[0]
    if pid in b_id_map:
        col_idx = b_id_map[pid]
        ranks = b_ranks_matrix[:, col_idx]
        ranks_qual = ranks[ranks < 200]
        
        p_top10 = (ranks <= 10).mean() * 100.0
        p_top20 = (ranks <= 20).mean() * 100.0
        p_top20_cond = (ranks_qual <= 20).mean() * 100.0 if len(ranks_qual) > 0 else 0.0
        ci_low = int(np.percentile(ranks_qual, 2.5)) if len(ranks_qual) > 0 else 1
        ci_high = int(np.percentile(ranks_qual, 97.5)) if len(ranks_qual) > 0 else 30
        
        tier = "Tier 1 (Rock Solid)" if p_top20 >= 80.0 else ("Tier 2 (Established Core)" if p_top20 >= 50.0 else "Tier 3 (Contested / Sensitive)")
        
        top_b_results.append({
            "Rank": rank_idx + 1, "Player": pname, "Player_ID": pid,
            "Mean_Rank": round(float(np.mean(ranks_qual)), 1), "Median_Rank": round(float(np.median(ranks_qual)), 1),
            "CI_95_Low": ci_low, "CI_95_High": ci_high,
            "95% CI": f"[{ci_low}, {ci_high}]",
            "P_Top10": round(p_top10, 1), "P(Top 20)": f"{p_top20:.1f}%",
            "P_Top20_Given_Eligible": round(p_top20_cond, 1),
            "Evidence Tier": tier
        })

df_b_boot_res = pd.DataFrame(top_b_results)

# Produce Bootstrap Results for Top 20 Bowlers
top_bw_results = []
bw_id_map = {pid: idx for idx, pid in enumerate(bw_ids)}

for rank_idx, r in top20_bw.iterrows():
    pname = r['Player']
    matching_pids = [pid for pid, name in bw_names.items() if name == pname]
    if not matching_pids:
        continue
    pid = matching_pids[0]
    if pid in bw_id_map:
        col_idx = bw_id_map[pid]
        ranks = bw_ranks_matrix[:, col_idx]
        ranks_qual = ranks[ranks < 200]
        
        p_top10 = (ranks <= 10).mean() * 100.0
        p_top20 = (ranks <= 20).mean() * 100.0
        p_top20_cond = (ranks_qual <= 20).mean() * 100.0 if len(ranks_qual) > 0 else 0.0
        ci_low = int(np.percentile(ranks_qual, 2.5)) if len(ranks_qual) > 0 else 1
        ci_high = int(np.percentile(ranks_qual, 97.5)) if len(ranks_qual) > 0 else 30
        
        tier = "Tier 1 (Rock Solid)" if p_top20 >= 80.0 else ("Tier 2 (Established Core)" if p_top20 >= 50.0 else "Tier 3 (Contested / Sensitive)")
        
        top_bw_results.append({
            "Rank": rank_idx + 1, "Player": pname, "Player_ID": pid,
            "Mean_Rank": round(float(np.mean(ranks_qual)), 1), "Median_Rank": round(float(np.median(ranks_qual)), 1),
            "CI_95_Low": ci_low, "CI_95_High": ci_high,
            "95% CI": f"[{ci_low}, {ci_high}]",
            "P_Top10": round(p_top10, 1), "P(Top 20)": f"{p_top20:.1f}%",
            "P_Top20_Given_Eligible": round(p_top20_cond, 1),
            "Evidence Tier": tier
        })

df_bw_boot_res = pd.DataFrame(top_bw_results)

# Update Top 20 Batters CSV with realistic bootstrap CIs
top20_b_updated = top20_b.copy()
for r in top_b_results:
    m = top20_b_updated['Player'] == r['Player']
    top20_b_updated.loc[m, '95% CI'] = r['95% CI']
    top20_b_updated.loc[m, 'P(Top 20)'] = r['P(Top 20)']
    top20_b_updated.loc[m, 'Evidence Tier'] = r['Evidence Tier']

top20_b_updated.to_csv(os.path.join(OUT_RANK, "Top20_Pressure_Batters.csv"), index=False)
print("Updated Top20_Pressure_Batters.csv with bootstrap metrics.")

top20_bw_updated = top20_bw.copy()
for r in top_bw_results:
    m = top20_bw_updated['Player'] == r['Player']
    top20_bw_updated.loc[m, '95% CI'] = r['95% CI']
    top20_bw_updated.loc[m, 'P(Top 20)'] = r['P(Top 20)']
    top20_bw_updated.loc[m, 'Evidence Tier'] = r['Evidence Tier']

top20_bw_updated.to_csv(os.path.join(OUT_RANK, "Top20_Pressure_Bowlers.csv"), index=False)
print("Updated Top20_Pressure_Bowlers.csv with bootstrap metrics.")

# Save unified Bootstrap_Confidence_Results.csv
boot_unified = pd.concat([
    df_b_boot_res.assign(Type="Batter"),
    df_bw_boot_res.assign(Type="Bowler")
], ignore_index=True)
boot_unified.to_csv(os.path.join(OUT_VAL, "Bootstrap_Confidence_Results.csv"), index=False)
print("Saved unified Bootstrap_Confidence_Results.csv successfully.")
