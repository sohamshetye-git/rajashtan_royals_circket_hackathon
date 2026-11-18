"""
Comprehensive Audit of Named Elite Players:
Batters:
1. Virat Kohli (47)
2. Hardik Pandya (3330)
3. Shubman Gill (6288)
4. Yashasvi Jaiswal (6819)
5. Rishabh Pant (4703)
6. Suryakumar Yadav (1699)
7. Sanju Samson (2258)
8. David Miller (1077)
9. Jos Buttler (813)
10. Heinrich Klaasen (4260)

Bowlers:
1. Jasprit Bumrah (2933)
2. Sunil Narine (781)
3. Rashid Khan (4722)
4. Arshdeep Singh (6464)
5. Varun Chakravarthy (6256)
6. Kuldeep Yadav (3644)
7. Mohammed Siraj (5944)
8. Pat Cummins (1758)
9. Matheesha Pathirana (8661)
10. Mustafizur Rahman (4373)
"""
import pandas as pd
import numpy as np

PROJ_DIR = r"C:\rajsathan_royals"
OUT_PROC = r"C:\rajsathan_royals\outputs\processed"
OUT_RANK = r"C:\rajsathan_royals\outputs\rankings"

df = pd.read_parquet(f"{OUT_PROC}/match_states.parquet")
df_scope = df[df['competition_type'].isin(['IPL', 'T20I'])].copy()

bat_dict = {
    'Virat Kohli': 47,
    'Hardik Pandya': 3330,
    'Shubman Gill': 6288,
    'Yashasvi Jaiswal': 6819,
    'Rishabh Pant': 4703,
    'Suryakumar Yadav': 1699,
    'Sanju Samson': 2258,
    'David Miller': 1077,
    'Jos Buttler': 813,
    'Heinrich Klaasen': 4260
}

bowl_dict = {
    'Jasprit Bumrah': 2933,
    'Sunil Narine': 781,
    'Rashid Khan': 4722,
    'Arshdeep Singh': 6464,
    'Varun Chakravarthy': 6256,
    'Kuldeep Yadav': 3644,
    'Mohammed Siraj': 5944,
    'Pat Cummins': 1758,
    'Matheesha Pathirana': 8661,
    'Mustafizur Rahman': 4373
}

print("=" * 80)
print("INVESTIGATION 1: NAMED BATTERS AUDIT (CRISP METRICS)")
print("=" * 80)

bat_rows = []
for name, pid in bat_dict.items():
    all_b = df_scope[df_scope['striker_id'] == pid]
    p_b = all_b[all_b['is_high_pressure']]
    n_b = all_b[~all_b['is_high_pressure']]
    
    tot_mat = all_b['match_id'].nunique()
    tot_balls = len(all_b)
    p_mat = p_b['match_id'].nunique()
    p_balls = len(p_b)
    p_runs = p_b['runs'].sum()
    p_dismissals = p_b['is_wicket'].sum()
    p_sr = (p_runs / p_balls * 100.0) if p_balls > 0 else 0.0
    p_avg = (p_runs / p_dismissals) if p_dismissals > 0 else (p_runs if p_balls > 0 else 0.0)
    p_rae = p_b['batter_rae'].sum()
    
    n_runs = n_b['runs'].sum()
    n_balls = len(n_b)
    n_sr = (n_runs / n_balls * 100.0) if n_balls > 0 else 0.0
    sr_delta = p_sr - n_sr
    
    # Chasing vs 1st innings pressure
    p_chase = p_b[p_b['innings'] == 2]
    p_set = p_b[p_b['innings'] == 1]
    
    chase_balls = len(p_chase)
    chase_sr = (p_chase['runs'].sum() / chase_balls * 100.0) if chase_balls > 0 else np.nan
    set_balls = len(p_set)
    set_sr = (p_set['runs'].sum() / set_balls * 100.0) if set_balls > 0 else np.nan
    
    # Check qualification in current CRISP (p_balls >= 100 and p_matches >= 10)
    qualifies = (p_balls >= 100) and (p_mat >= 10)
    
    bat_rows.append({
        'Name': name,
        'ID': pid,
        'Tot_Mat': tot_mat,
        'Tot_Balls': tot_balls,
        'P_Mat': p_mat,
        'P_Balls': p_balls,
        'P_Runs': p_runs,
        'P_SR': round(p_sr, 1),
        'P_Avg': round(p_avg, 1),
        'N_SR': round(n_sr, 1),
        'SR_Delta': round(sr_delta, 1),
        'P_RAE': round(p_rae, 1),
        'Chase_Balls': chase_balls,
        'Chase_SR': round(chase_sr, 1) if pd.notnull(chase_sr) else 'N/A',
        'Set_Balls': set_balls,
        'Set_SR': round(set_sr, 1) if pd.notnull(set_sr) else 'N/A',
        'Meets_Cutoff': 'YES' if qualifies else 'NO'
    })

bat_audit_df = pd.DataFrame(bat_rows)
print(bat_audit_df.to_string(index=False))

print("\n" + "=" * 80)
print("INVESTIGATION 1: NAMED BOWLERS AUDIT (CRISP METRICS)")
print("=" * 80)

bowl_rows = []
for name, pid in bowl_dict.items():
    all_bw = df_scope[df_scope['bowler_id'] == pid]
    all_legal = all_bw[all_bw['is_legal_ball']]
    
    p_bw = all_bw[all_bw['is_high_pressure']]
    p_legal = p_bw[p_bw['is_legal_ball']]
    n_legal = all_bw[~all_bw['is_high_pressure'] & all_bw['is_legal_ball']]
    
    tot_mat = all_bw['match_id'].nunique()
    tot_balls = len(all_legal)
    
    p_mat = p_bw['match_id'].nunique()
    p_balls = len(p_legal)
    p_runs = p_legal['bowler_runs_conceded'].sum()
    p_wkts = p_legal['is_bowler_wicket'].sum()
    p_econ = (p_runs / (p_balls / 6.0)) if p_balls > 0 else 99.0
    p_rpa = p_legal['bowler_rpa'].sum()
    
    n_runs = n_legal['bowler_runs_conceded'].sum()
    n_balls = len(n_legal)
    n_econ = (n_runs / (n_balls / 6.0)) if n_balls > 0 else 99.0
    econ_delta = n_econ - p_econ # Positive means improved
    
    qualifies = (p_balls >= 100) and (p_mat >= 10)
    
    bowl_rows.append({
        'Name': name,
        'ID': pid,
        'Tot_Mat': tot_mat,
        'Tot_Balls': tot_balls,
        'P_Mat': p_mat,
        'P_Balls': p_balls,
        'P_Runs': p_runs,
        'P_Wkts': p_wkts,
        'P_Econ': round(p_econ, 2),
        'N_Econ': round(n_econ, 2),
        'Econ_Delta': round(econ_delta, 2),
        'P_RPA': round(p_rpa, 1),
        'Meets_Cutoff': 'YES' if qualifies else 'NO'
    })

bowl_audit_df = pd.DataFrame(bowl_rows)
print(bowl_audit_df.to_string(index=False))
