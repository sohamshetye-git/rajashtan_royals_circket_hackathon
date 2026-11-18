"""
Professional Winning Model Execution: Robust Elite Cohort (Sample >= 150 Balls)
Anchored on Real-World Cricket Evaluation Standards.
"""

import os
import pandas as pd
import numpy as np

BASE_DIR = r"C:\rajsathan_royals"
OUT_PROC = os.path.join(BASE_DIR, "outputs", "processed")
OUT_RANK = os.path.join(BASE_DIR, "outputs", "rankings")
OUT_VAL = os.path.join(BASE_DIR, "outputs", "validation")

df = pd.read_parquet(os.path.join(OUT_PROC, "match_states.parquet"))
df_scope = df[df['competition_type'].isin(['IPL', 'T20I'])].copy()
hp = df_scope[df_scope['pressure_score'] >= 0.65]
norm = df_scope[df_scope['pressure_score'] < 0.65]

mapping = pd.read_csv(os.path.join(BASE_DIR, "data", "Data Pack", "competition_team_player_mapping.csv"))
p_names = mapping[['player_id', 'player_name']].drop_duplicates(subset=['player_id']).set_index('player_id')['player_name'].to_dict()

# Batters Aggregation
b_p = hp.groupby('striker_id').agg(
    p_balls=('runs', 'count'),
    p_runs=('runs', 'sum'),
    p_rae=('batter_rae', 'sum'),
    p_matches=('match_id', 'nunique'),
    ipl_balls=('competition_type', lambda x: (x == 'IPL').sum()),
    t20i_balls=('competition_type', lambda x: (x == 'T20I').sum()),
    p_fours=('is_four', 'sum'),
    p_sixes=('is_six', 'sum'),
    p_dots=('runs', lambda x: (x == 0).sum()),
    p_dismissals=('is_wicket', 'sum')
).reset_index()

b_n = norm.groupby('striker_id').agg(
    n_balls=('runs', 'count'),
    n_runs=('runs', 'sum')
).reset_index()

b = b_p.merge(b_n, on='striker_id', how='left')
b['p_sr'] = (b['p_runs'] / b['p_balls']) * 100.0
b['n_sr'] = np.where(b['n_balls'] > 0, (b['n_runs'] / b['n_balls']) * 100.0, 0.0)
b['sr_delta'] = b['p_sr'] - b['n_sr'].fillna(b['p_sr'])

# Robust Sample Cutoff: >= 150 crisis balls across >= 12 matches
b_q = b[(b['p_balls'] >= 150) & (b['p_matches'] >= 12)].copy()

K = 75.0
b_q['w'] = b_q['p_balls'] / (b_q['p_balls'] + K)
b_q['shrunk_rae_rate'] = b_q['w'] * (b_q['p_rae'] / b_q['p_balls']) + (1 - b_q['w']) * 0.11
b_q['shrunk_sr'] = b_q['w'] * b_q['p_sr'] + (1 - b_q['w']) * 136.75

def z_score(s):
    std = s.std()
    return (s - s.mean()) / (std if std > 0 else 1.0)

b_q['BPRI_raw'] = (
    0.30 * z_score(b_q['p_rae']) +
    0.25 * z_score(b_q['shrunk_sr']) +
    0.15 * z_score(b_q['sr_delta']) +
    0.15 * z_score(b_q['shrunk_rae_rate']) +
    0.15 * z_score(np.log1p(b_q['p_balls']))
)
b_q['BPRI'] = (50.0 + 15.0 * b_q['BPRI_raw']).round(2)
b_q['player_name'] = b_q['striker_id'].map(p_names)
b_top10 = b_q.sort_values('BPRI', ascending=False).head(10).reset_index(drop=True)
b_top10['Rank'] = b_top10.index + 1

# Bowlers Aggregation
bw_p_all = hp.groupby('bowler_id').agg(
    p_all=('bowler_runs_conceded', 'count'),
    p_runs=('bowler_runs_conceded', 'sum'),
    p_wkts=('is_bowler_wicket', 'sum'),
    p_rpa=('bowler_rpa', 'sum'),
    p_matches=('match_id', 'nunique'),
    ipl_del=('competition_type', lambda x: (x == 'IPL').sum()),
    t20i_del=('competition_type', lambda x: (x == 'T20I').sum()),
    p_dots=('delivery_total_runs', lambda x: (x == 0).sum())
).reset_index()

bw_p_leg = hp[hp['is_legal_ball']].groupby('bowler_id').agg(p_legal=('is_legal_ball', 'sum')).reset_index()
bw = bw_p_all.merge(bw_p_leg, on='bowler_id', how='left')
bw['p_legal'] = bw['p_legal'].fillna(0).astype(int)
bw['p_overs'] = bw['p_legal'] / 6.0
bw['p_econ'] = np.where(bw['p_overs'] > 0, bw['p_runs'] / bw['p_overs'], 99.0)

bw_n_all = norm.groupby('bowler_id').agg(n_runs=('bowler_runs_conceded', 'sum')).reset_index()
bw_n_leg = norm[norm['is_legal_ball']].groupby('bowler_id').agg(n_legal=('is_legal_ball', 'sum')).reset_index()
bw_n = bw_n_all.merge(bw_n_leg, on='bowler_id', how='left')
bw_n['n_econ'] = np.where(bw_n['n_legal'] > 0, bw_n['n_runs'] / (bw_n['n_legal'] / 6.0), 99.0)
bw = bw.merge(bw_n[['bowler_id', 'n_econ']], on='bowler_id', how='left')
bw['econ_delta'] = bw['n_econ'].fillna(bw['p_econ']) - bw['p_econ']

# Robust Sample Cutoff: >= 150 legal balls across >= 12 matches
bw_q = bw[(bw['p_legal'] >= 150) & (bw['p_matches'] >= 12)].copy()

bw_q['w'] = bw_q['p_legal'] / (bw_q['p_legal'] + K)
bw_q['shrunk_rpa_rate'] = bw_q['w'] * (bw_q['p_rpa'] / bw_q['p_legal']) + (1 - bw_q['w']) * -0.11
bw_q['shrunk_econ'] = bw_q['w'] * bw_q['p_econ'] + (1 - bw_q['w']) * 8.53

bw_q['PRI_raw'] = (
    0.30 * z_score(bw_q['p_rpa']) +
    0.25 * z_score(-bw_q['shrunk_econ']) +
    0.15 * z_score(bw_q['econ_delta']) +
    0.15 * z_score(bw_q['p_wkts']) +
    0.15 * z_score(np.log1p(bw_q['p_legal']))
)
bw_q['PRI'] = (50.0 + 15.0 * bw_q['PRI_raw']).round(2)
bw_q['player_name'] = bw_q['bowler_id'].map(p_names)
bw_top10 = bw_q.sort_values('PRI', ascending=False).head(10).reset_index(drop=True)
bw_top10['Rank'] = bw_top10.index + 1

# Save canonical final CSVs
b_top10.to_csv(os.path.join(OUT_RANK, "final_batter_top10.csv"), index=False)
bw_top10.to_csv(os.path.join(OUT_RANK, "final_bowler_top10.csv"), index=False)

# Update comparison CSV
comp = pd.DataFrame({
    'Rank': range(1, 11),
    'Robust_Elite_Batter': [f"{row['player_name']} (BPRI: {row['BPRI']})" for _, row in b_top10.iterrows()],
    'Robust_Elite_Bowler': [f"{row['player_name']} (PRI: {row['PRI']})" for _, row in bw_top10.iterrows()]
})
comp.to_csv(os.path.join(OUT_RANK, "ranking_comparison.csv"), index=False)
print("Successfully generated robust elite final rankings CSVs.")
print(b_top10[['Rank', 'player_name', 'p_balls', 'p_sr', 'sr_delta', 'p_rae', 'BPRI']])
print(bw_top10[['Rank', 'player_name', 'p_legal', 'p_econ', 'econ_delta', 'p_rpa', 'p_wkts', 'PRI']])
