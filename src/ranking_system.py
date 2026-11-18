"""
PHASE 8 & 9: Statistical Reliability, Empirical Bayes Shrinkage, & Final Rating Systems
Calculates:
- Batter Pressure Reliability Index (BPRI)
- Bowler Pressure Reliability Index (Bowler_PRI)
Using:
1. Minimum eligibility thresholds (minimum 60 pressure balls, >= 8 pressure matches).
2. Empirical Bayes Shrinkage for Strike Rate, RAE per ball, Economy, and RPA per ball.
3. Multi-dimensional index weighting:
   - Volume & Sample Weight (Logarithmic sample scale)
   - Value-Added per ball (RAE / RPA)
   - Situational Execution (Pressure Strike Rate / Pressure Economy)
   - Dismissal Resistance / Wicket Taking Impact (Balls per dismissal / Pressure Wickets)
   - Match-Level Consistency (% matches with positive impact, match std dev penalty)
   - Pressure Delta vs Normal Baseline
Produces:
- Top 10 Batters and Top 10 Bowlers rankings with full uncertainty, sample, and stability metrics.
"""
import os
import pandas as pd
import numpy as np

PROJ_DIR = r"C:\rajsathan_royals"
OUT_PROC = os.path.join(PROJ_DIR, "outputs", "processed")
OUT_RANK = os.path.join(PROJ_DIR, "outputs", "rankings")
OUT_VAL = os.path.join(PROJ_DIR, "outputs", "validation")

print("=" * 80)
print("PHASE 8 & 9: STATISTICAL RELIABILITY & FINAL RANKING SYSTEM")
print("=" * 80)

b_df = pd.read_parquet(os.path.join(OUT_PROC, "batter_aggregated_raw.parquet"))
bw_df = pd.read_parquet(os.path.join(OUT_PROC, "bowler_aggregated_raw.parquet"))

# -------------------------------------------------------------
# 1. BATTER PRESSURE RELIABILITY INDEX (BPRI)
# -------------------------------------------------------------
print("\n--- CALIBRATING BATTER RELIABILITY INDEX ---")
# Eligibility filter:
# Minimum 60 pressure balls faced and at least 8 pressure matches
MIN_BAT_BALLS = 60
MIN_BAT_MATCHES = 8

b_qual = b_df[(b_df['p_balls'] >= MIN_BAT_BALLS) & (b_df['p_matches'] >= MIN_BAT_MATCHES)].copy()
print(f"Qualified Batters (>= {MIN_BAT_BALLS} pressure balls, >= {MIN_BAT_MATCHES} pressure matches): {len(b_qual)}")

# Population prior benchmarks for Empirical Bayes shrinkage
# Strike rate prior
pop_bat_sr = (b_qual['p_runs'].sum() / b_qual['p_balls'].sum()) * 100.0
# RAE per ball prior
pop_bat_rae = b_qual['p_rae'].sum() / b_qual['p_balls'].sum()

print(f"Batter Population Prior Pressure SR: {pop_bat_sr:.2f}")
print(f"Batter Population Prior Pressure RAE/ball: {pop_bat_rae:.4f}")

# Empirical Bayes Shrinkage:
# Weight w_i = n_i / (n_i + K), where K = 50 balls
K_BAT = 50.0
b_qual['eb_weight'] = b_qual['p_balls'] / (b_qual['p_balls'] + K_BAT)

# Shrunk metrics
b_qual['shrunk_p_sr'] = b_qual['eb_weight'] * b_qual['p_sr'] + (1.0 - b_qual['eb_weight']) * pop_bat_sr
b_qual['shrunk_p_rae'] = b_qual['eb_weight'] * b_qual['p_mean_rae'] + (1.0 - b_qual['eb_weight']) * pop_bat_rae

# Consistency penalty: adjust for high match variance relative to volume
b_qual['consistency_score'] = (b_qual['p_consistency_pct'] / 100.0) / (1.0 + 0.05 * b_qual['p_rae_match_std'])

# Z-score standardization of core components:
def z_score(series):
    std = series.std()
    return (series - series.mean()) / (std if std > 0 else 1.0)

b_qual['z_rae'] = z_score(b_qual['shrunk_p_rae'])
b_qual['z_sr'] = z_score(b_qual['shrunk_p_sr'])
b_qual['z_avg'] = z_score(np.log1p(b_qual['p_avg']))
b_qual['z_delta'] = z_score(b_qual['sr_delta'])
b_qual['z_consistency'] = z_score(b_qual['consistency_score'])
b_qual['z_volume'] = z_score(np.log1p(b_qual['p_balls']))

# Composite Batter Pressure Reliability Index (BPRI):
# Value component (RAE / ball): 30%
# Execution component (Shrunk SR): 25%
# Survival / Average component: 15%
# Match Consistency: 15%
# Delta over baseline: 10%
# Volume / Exposure credibility: 5%
b_qual['bpri_raw'] = (
    0.30 * b_qual['z_rae'] +
    0.25 * b_qual['z_sr'] +
    0.15 * b_qual['z_avg'] +
    0.15 * b_qual['z_consistency'] +
    0.10 * b_qual['z_delta'] +
    0.05 * b_qual['z_volume']
)

# Rescale BPRI to 0 - 100 for intuitive interpretation
b_qual['BPRI'] = 50.0 + 15.0 * b_qual['bpri_raw']
b_qual['BPRI'] = b_qual['BPRI'].round(2)

# Rank batters
b_ranked = b_qual.sort_values('BPRI', ascending=False).reset_index(drop=True)
b_ranked['Rank'] = np.arange(1, len(b_ranked) + 1)

print("\nTOP 15 BATTERS UNDER PRESSURE (BPRI):")
top_bat_cols = ['Rank', 'player_name', 'striker_id', 'p_matches', 'p_balls', 'p_runs', 'p_sr', 'p_avg', 'n_sr', 'sr_delta', 'p_rae', 'BPRI']
print(b_ranked[top_bat_cols].head(15).to_string(index=False))

# -------------------------------------------------------------
# 2. BOWLER PRESSURE RELIABILITY INDEX (Bowler_PRI)
# -------------------------------------------------------------
print("\n--- CALIBRATING BOWLER RELIABILITY INDEX ---")
# Eligibility filter:
# Minimum 60 pressure legal balls (10 overs) and at least 8 pressure matches
MIN_BOWL_BALLS = 60
MIN_BOWL_MATCHES = 8

bw_qual = bw_df[(bw_df['p_legal_balls'] >= MIN_BOWL_BALLS) & (bw_df['p_matches'] >= MIN_BOWL_MATCHES)].copy()
print(f"Qualified Bowlers (>= {MIN_BOWL_BALLS} pressure legal balls, >= {MIN_BOWL_MATCHES} pressure matches): {len(bw_qual)}")

# Population prior benchmarks
pop_bowl_econ = (bw_qual['p_runs_conceded'].sum() / (bw_qual['p_legal_balls'].sum() / 6.0))
pop_bowl_rpa = bw_qual['p_rpa'].sum() / bw_qual['p_legal_balls'].sum()
pop_bowl_wkt_rate = (bw_qual['p_wickets'].sum() / bw_qual['p_legal_balls'].sum())

print(f"Bowler Population Prior Pressure Economy: {pop_bowl_econ:.2f}")
print(f"Bowler Population Prior Pressure RPA/ball: {pop_bowl_rpa:.4f}")

# Empirical Bayes Shrinkage:
K_BOWL = 48.0 # 8 overs shrinkage parameter
bw_qual['eb_weight'] = bw_qual['p_legal_balls'] / (bw_qual['p_legal_balls'] + K_BOWL)

# Shrunk metrics (lower economy is better)
bw_qual['shrunk_p_econ'] = bw_qual['eb_weight'] * bw_qual['p_econ'] + (1.0 - bw_qual['eb_weight']) * pop_bowl_econ
bw_qual['shrunk_p_rpa'] = bw_qual['eb_weight'] * bw_qual['p_mean_rpa'] + (1.0 - bw_qual['eb_weight']) * pop_bowl_rpa
bw_qual['shrunk_p_wkt_rate'] = bw_qual['eb_weight'] * (bw_qual['p_wickets'] / bw_qual['p_legal_balls']) + (1.0 - bw_qual['eb_weight']) * pop_bowl_wkt_rate

# Consistency score
bw_qual['consistency_score'] = (bw_qual['p_consistency_pct'] / 100.0) / (1.0 + 0.05 * bw_qual['p_rpa_match_std'])

# Z-scores (invert economy so higher is better)
bw_qual['z_rpa'] = z_score(bw_qual['shrunk_p_rpa'])
bw_qual['z_econ_inv'] = z_score(-bw_qual['shrunk_p_econ'])
bw_qual['z_wickets'] = z_score(bw_qual['shrunk_p_wkt_rate'])
bw_qual['z_delta'] = z_score(bw_qual['econ_delta'])
bw_qual['z_consistency'] = z_score(bw_qual['consistency_score'])
bw_qual['z_volume'] = z_score(np.log1p(bw_qual['p_legal_balls']))

# Composite Bowler Pressure Reliability Index (Bowler_PRI):
# Prevention component (RPA / ball): 30%
# Economy execution (Shrunk Economy): 25%
# Wicket-taking threat: 15%
# Match Consistency: 15%
# Delta vs Normal Baseline: 10%
# Volume credibility: 5%
bw_qual['bowler_pri_raw'] = (
    0.30 * bw_qual['z_rpa'] +
    0.25 * bw_qual['z_econ_inv'] +
    0.15 * bw_qual['z_wickets'] +
    0.15 * bw_qual['z_consistency'] +
    0.10 * bw_qual['z_delta'] +
    0.05 * bw_qual['z_volume']
)

# Rescale to 0 - 100
bw_qual['Bowler_PRI'] = 50.0 + 15.0 * bw_qual['bowler_pri_raw']
bw_qual['Bowler_PRI'] = bw_qual['Bowler_PRI'].round(2)

# Rank bowlers
bw_ranked = bw_qual.sort_values('Bowler_PRI', ascending=False).reset_index(drop=True)
bw_ranked['Rank'] = np.arange(1, len(bw_ranked) + 1)

print("\nTOP 15 BOWLERS UNDER PRESSURE (Bowler_PRI):")
top_bowl_cols = ['Rank', 'player_name', 'bowler_id', 'p_matches', 'p_legal_balls', 'p_overs', 'p_runs_conceded', 'p_econ', 'p_wickets', 'n_econ', 'econ_delta', 'p_rpa', 'Bowler_PRI']
print(bw_ranked[top_bowl_cols].head(15).to_string(index=False))

# Save rankings
b_ranked.to_csv(os.path.join(OUT_RANK, "batter_rankings.csv"), index=False)
bw_ranked.to_csv(os.path.join(OUT_RANK, "bowler_rankings.csv"), index=False)

# Save official Top 10
b_top10 = b_ranked.head(10).copy()
bw_top10 = bw_ranked.head(10).copy()

b_top10.to_csv(os.path.join(OUT_RANK, "batter_top10.csv"), index=False)
bw_top10.to_csv(os.path.join(OUT_RANK, "bowler_top10.csv"), index=False)

print("\nSaved batter_rankings.csv, bowler_rankings.csv, batter_top10.csv, bowler_top10.csv successfully.")
