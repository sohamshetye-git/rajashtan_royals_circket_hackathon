"""
Refined Ranking Script: Enhancing Exposure Governance
Requires a robust sample size:
- Batters: >= 100 pressure balls faced and >= 10 pressure matches.
- Bowlers: >= 100 pressure legal balls bowled (16.4 overs) and >= 10 pressure matches.
This ensures players selected in the Top 10 have proven multi-season, multi-match reliability,
preventing low-sample volatility.
"""
import os
import pandas as pd
import numpy as np

PROJ_DIR = r"C:\rajsathan_royals"
OUT_PROC = os.path.join(PROJ_DIR, "outputs", "processed")
OUT_RANK = os.path.join(PROJ_DIR, "outputs", "rankings")
OUT_VAL = os.path.join(PROJ_DIR, "outputs", "validation")

b_df = pd.read_parquet(os.path.join(OUT_PROC, "batter_aggregated_raw.parquet"))
bw_df = pd.read_parquet(os.path.join(OUT_PROC, "bowler_aggregated_raw.parquet"))

# 1. BATTERS
# Filter with robust exposure: >= 100 balls, >= 10 matches
MIN_BAT_BALLS = 100
MIN_BAT_MATCHES = 10

b_qual = b_df[(b_df['p_balls'] >= MIN_BAT_BALLS) & (b_df['p_matches'] >= MIN_BAT_MATCHES)].copy()
print(f"Qualified Robust Batters: {len(b_qual)}")

pop_bat_sr = (b_qual['p_runs'].sum() / b_qual['p_balls'].sum()) * 100.0
pop_bat_rae = b_qual['p_rae'].sum() / b_qual['p_balls'].sum()

K_BAT = 60.0
b_qual['eb_weight'] = b_qual['p_balls'] / (b_qual['p_balls'] + K_BAT)
b_qual['shrunk_p_sr'] = b_qual['eb_weight'] * b_qual['p_sr'] + (1.0 - b_qual['eb_weight']) * pop_bat_sr
b_qual['shrunk_p_rae'] = b_qual['eb_weight'] * b_qual['p_mean_rae'] + (1.0 - b_qual['eb_weight']) * pop_bat_rae
b_qual['consistency_score'] = (b_qual['p_consistency_pct'] / 100.0) / (1.0 + 0.05 * b_qual['p_rae_match_std'])

def z_score(series):
    std = series.std()
    return (series - series.mean()) / (std if std > 0 else 1.0)

b_qual['z_rae'] = z_score(b_qual['shrunk_p_rae'])
b_qual['z_sr'] = z_score(b_qual['shrunk_p_sr'])
b_qual['z_avg'] = z_score(np.log1p(b_qual['p_avg']))
b_qual['z_delta'] = z_score(b_qual['sr_delta'])
b_qual['z_consistency'] = z_score(b_qual['consistency_score'])
b_qual['z_volume'] = z_score(np.log1p(b_qual['p_balls']))

b_qual['bpri_raw'] = (
    0.30 * b_qual['z_rae'] +
    0.25 * b_qual['z_sr'] +
    0.15 * b_qual['z_avg'] +
    0.15 * b_qual['z_consistency'] +
    0.10 * b_qual['z_delta'] +
    0.05 * b_qual['z_volume']
)
b_qual['BPRI'] = (50.0 + 15.0 * b_qual['bpri_raw']).round(2)
b_ranked = b_qual.sort_values('BPRI', ascending=False).reset_index(drop=True)
b_ranked['Rank'] = np.arange(1, len(b_ranked) + 1)

print("\n--- REFINED TOP 12 BATTERS (ROBUST SAMPLE) ---")
b_cols = ['Rank', 'player_name', 'striker_id', 'p_matches', 'p_balls', 'p_runs', 'p_sr', 'p_avg', 'n_sr', 'sr_delta', 'p_rae', 'BPRI']
print(b_ranked[b_cols].head(12).to_string(index=False))

# 2. BOWLERS
MIN_BOWL_BALLS = 100
MIN_BOWL_MATCHES = 10

bw_qual = bw_df[(bw_df['p_legal_balls'] >= MIN_BOWL_BALLS) & (bw_df['p_matches'] >= MIN_BOWL_MATCHES)].copy()
print(f"\nQualified Robust Bowlers: {len(bw_qual)}")

pop_bowl_econ = (bw_qual['p_runs_conceded'].sum() / (bw_qual['p_legal_balls'].sum() / 6.0))
pop_bowl_rpa = bw_qual['p_rpa'].sum() / bw_qual['p_legal_balls'].sum()
pop_bowl_wkt = (bw_qual['p_wickets'].sum() / bw_qual['p_legal_balls'].sum())

K_BOWL = 60.0
bw_qual['eb_weight'] = bw_qual['p_legal_balls'] / (bw_qual['p_legal_balls'] + K_BOWL)
bw_qual['shrunk_p_econ'] = bw_qual['eb_weight'] * bw_qual['p_econ'] + (1.0 - bw_qual['eb_weight']) * pop_bowl_econ
bw_qual['shrunk_p_rpa'] = bw_qual['eb_weight'] * bw_qual['p_mean_rpa'] + (1.0 - bw_qual['eb_weight']) * pop_bowl_rpa
bw_qual['shrunk_p_wkt'] = bw_qual['eb_weight'] * (bw_qual['p_wickets'] / bw_qual['p_legal_balls']) + (1.0 - bw_qual['eb_weight']) * pop_bowl_wkt
bw_qual['consistency_score'] = (bw_qual['p_consistency_pct'] / 100.0) / (1.0 + 0.05 * bw_qual['p_rpa_match_std'])

bw_qual['z_rpa'] = z_score(bw_qual['shrunk_p_rpa'])
bw_qual['z_econ_inv'] = z_score(-bw_qual['shrunk_p_econ'])
bw_qual['z_wickets'] = z_score(bw_qual['shrunk_p_wkt'])
bw_qual['z_delta'] = z_score(bw_qual['econ_delta'])
bw_qual['z_consistency'] = z_score(bw_qual['consistency_score'])
bw_qual['z_volume'] = z_score(np.log1p(bw_qual['p_legal_balls']))

bw_qual['bowler_pri_raw'] = (
    0.30 * bw_qual['z_rpa'] +
    0.25 * bw_qual['z_econ_inv'] +
    0.15 * bw_qual['z_wickets'] +
    0.15 * bw_qual['z_consistency'] +
    0.10 * bw_qual['z_delta'] +
    0.05 * bw_qual['z_volume']
)
bw_qual['Bowler_PRI'] = (50.0 + 15.0 * bw_qual['bowler_pri_raw']).round(2)
bw_ranked = bw_qual.sort_values('Bowler_PRI', ascending=False).reset_index(drop=True)
bw_ranked['Rank'] = np.arange(1, len(bw_ranked) + 1)

print("\n--- REFINED TOP 12 BOWLERS (ROBUST SAMPLE) ---")
bw_cols = ['Rank', 'player_name', 'bowler_id', 'p_matches', 'p_legal_balls', 'p_overs', 'p_runs_conceded', 'p_econ', 'p_wickets', 'n_econ', 'econ_delta', 'p_rpa', 'Bowler_PRI']
print(bw_ranked[bw_cols].head(12).to_string(index=False))

# Update rankings files
b_ranked.to_csv(os.path.join(OUT_RANK, "batter_rankings.csv"), index=False)
bw_ranked.to_csv(os.path.join(OUT_RANK, "bowler_rankings.csv"), index=False)

b_top10 = b_ranked.head(10).copy()
bw_top10 = bw_ranked.head(10).copy()

b_top10.to_csv(os.path.join(OUT_RANK, "batter_top10.csv"), index=False)
bw_top10.to_csv(os.path.join(OUT_RANK, "bowler_top10.csv"), index=False)
print("\nFinal rankings saved successfully.")
