"""
Deep check of 'other' and 'extras_2_runs' and match totals verification
"""
import os
import pandas as pd

DATA_DIR = r"C:\rajsathan_royals\data\Data Pack"
bbb = pd.read_csv(os.path.join(DATA_DIR, "ball_by_ball.csv"), low_memory=False)

print("Rows where extras_2_runs > 0:")
sample_e2 = bbb[bbb['extras_2_runs'] > 0][['runs', 'extras_type', 'extras1_runs', 'extras_2_runs', 'is_four', 'is_six', 'dismissal_type']]
print(sample_e2.head(20))

print("\nWhat is 'other' extras_type?")
sample_other = bbb[bbb['extras_type'] == 'other'][['runs', 'extras_type', 'extras1_runs', 'extras_2_runs', 'is_four', 'is_six', 'dismissal_type']]
print(sample_other.head(20))

# Check match scores: let's verify a few completed matches against matches.csv results
matches = pd.read_csv(os.path.join(DATA_DIR, "matches.csv"))
print("\nSample 5 matches:")
sample_m = matches[matches['result'].str.contains('Won', na=False)].head(5)
print(sample_m[['match_id', 'match_date', 'home_team', 'away_team', 'result']])

for mid in sample_m['match_id']:
    m_bbb = bbb[bbb['match_id'] == mid]
    print(f"\n--- MATCH {mid} ---")
    for inn in sorted(m_bbb['innings'].unique()):
        inn_bbb = m_bbb[m_bbb['innings'] == inn]
        bat_runs = inn_bbb['runs'].sum()
        e1 = inn_bbb['extras1_runs'].sum()
        e2 = inn_bbb['extras_2_runs'].sum()
        tot_runs_1 = bat_runs + e1 + e2
        tot_wickets = inn_bbb['is_wicket'].sum()
        # legal balls
        legal_balls = inn_bbb[~inn_bbb['extras_type'].isin(['wide', 'Overstep', 'other', 'Penalty'])].shape[0]
        # or wide + overstep
        wides = (inn_bbb['extras_type'] == 'wide').sum()
        noballs = inn_bbb['extras_type'].isin(['Overstep', 'other']).sum()
        legal_balls_2 = len(inn_bbb) - wides - noballs
        print(f"Innings {inn}: Bat runs={bat_runs}, E1={e1}, E2={e2} -> Total Score={tot_runs_1}, Wickets={tot_wickets}, Total Balls={len(inn_bbb)}, Legal balls={legal_balls_2} ({legal_balls_2//6}.{legal_balls_2%6} ov)")
