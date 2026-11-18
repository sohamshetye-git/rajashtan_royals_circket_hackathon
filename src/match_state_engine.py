"""
PHASE 2 & 3: Match State Engine (v2 - Fixed Cumulative Vectorization)
Constructs clean deliveries and pre-delivery match states for all 200,999 records.
Properly shifts cumulative runs, legal balls, and wickets within each match_id and innings.
"""
import os
import pandas as pd
import numpy as np

DATA_DIR = r"C:\rajsathan_royals\data\Data Pack"
OUT_PROC = r"C:\rajsathan_royals\outputs\processed"
OUT_VAL = r"C:\rajsathan_royals\outputs\validation"

os.makedirs(OUT_PROC, exist_ok=True)
os.makedirs(OUT_VAL, exist_ok=True)

print("=" * 80)
print("BUILDING CLEAN DELIVERIES & MATCH STATE ENGINE (V2)")
print("=" * 80)

# Load raw datasets
bbb = pd.read_csv(os.path.join(DATA_DIR, "ball_by_ball.csv"), low_memory=False)
matches = pd.read_csv(os.path.join(DATA_DIR, "matches.csv"))
comps = pd.read_csv(os.path.join(DATA_DIR, "competitions.csv"))

# Merge metadata
bbb = bbb.merge(
    matches[['match_id', 'comp_id', 'match_date', 'stage', 'venue_id', 'venue_country',
             'home_team_id', 'away_team_id', 'knock_out', 'revised_target',
             'first_inn_revised_overs', 'second_inn_revised_overs', 'win_team_id', 'result']],
    on='match_id',
    how='left'
)
bbb = bbb.merge(comps[['comp_id', 'comp_name', 'match_format', 'season']], on='comp_id', how='left')

# Classify competition type
def classify_comp(row):
    comp_name = str(row['comp_name'])
    match_format = str(row['match_format'])
    if "IPL" in comp_name or "Indian Premier League" in comp_name:
        return "IPL"
    elif match_format == "T20I":
        return "T20I"
    else:
        return "OTHER_T20"

bbb['competition_type'] = bbb.apply(classify_comp, axis=1)

# Cricket scoring mechanics
illegal_types = {'wide', 'Overstep', 'other'}
bbb['is_illegal_ball'] = bbb['extras_type'].isin(illegal_types)
bbb['is_legal_ball'] = ~bbb['is_illegal_ball']

bbb['extras1_runs'] = bbb['extras1_runs'].fillna(0).astype(int)
bbb['extras_2_runs'] = bbb['extras_2_runs'].fillna(0).astype(int)
bbb['runs'] = bbb['runs'].fillna(0).astype(int)
bbb['delivery_total_runs'] = bbb['runs'] + bbb['extras1_runs'] + bbb['extras_2_runs']

# Bowler debited runs
non_bowler_extras = {'byes', 'legbyes'}
bbb['is_bye_or_legbye'] = bbb['extras_type'].isin(non_bowler_extras)
bbb['bowler_runs_conceded'] = np.where(
    bbb['is_bye_or_legbye'],
    0,
    bbb['delivery_total_runs']
)

# Bowler credited wickets
bowler_dismissal_types = {'Bowled', 'Caught', 'LBW', 'Stump', 'Hit Wicket'}
bbb['is_bowler_wicket'] = bbb['is_wicket'] & bbb['dismissal_type'].isin(bowler_dismissal_types)

# Match Phase
def assign_phase(overid):
    if overid <= 6:
        return "Powerplay"
    elif overid <= 15:
        return "Middle"
    else:
        return "Death"

bbb['match_phase'] = bbb['overid'].apply(assign_phase)

# Sort strictly by match, innings, and innings_ball_num
bbb = bbb.sort_values(['match_id', 'innings', 'innings_ball_num']).reset_index(drop=True)

print("Calculating cumulative pre-delivery match states correctly...")
# Post-delivery cumsums
bbb['cum_runs_post'] = bbb.groupby(['match_id', 'innings'])['delivery_total_runs'].cumsum()
bbb['cum_legal_balls_post'] = bbb.groupby(['match_id', 'innings'])['is_legal_ball'].cumsum()
bbb['cum_wickets_post'] = bbb.groupby(['match_id', 'innings'])['is_wicket'].cumsum()

# Pre-delivery: shift the post-cumsum by 1 within group, and fill first delivery with 0
bbb['cum_runs_pre'] = bbb.groupby(['match_id', 'innings'])['cum_runs_post'].shift(1).fillna(0).astype(int)
bbb['cum_legal_balls_pre'] = bbb.groupby(['match_id', 'innings'])['cum_legal_balls_post'].shift(1).fillna(0).astype(int)
bbb['cum_wickets_pre'] = bbb.groupby(['match_id', 'innings'])['cum_wickets_post'].shift(1).fillna(0).astype(int)

# Allocated balls per innings
def get_allocated_balls(row):
    inn = row['innings']
    if inn == 1:
        rev = row['first_inn_revised_overs']
        if pd.notnull(rev) and rev > 0:
            return int(rev) if rev > 20 else int(rev * 6)
        return 120
    elif inn == 2:
        rev = row['second_inn_revised_overs']
        if pd.notnull(rev) and rev > 0:
            return int(rev) if rev > 20 else int(rev * 6)
        return 120
    else:
        return 6

bbb['allocated_balls'] = bbb.apply(get_allocated_balls, axis=1)

# Balls and wickets remaining
bbb['balls_remaining_pre'] = np.maximum(0, bbb['allocated_balls'] - bbb['cum_legal_balls_pre'])
bbb['wickets_remaining_pre'] = np.maximum(0, 10 - bbb['cum_wickets_pre'])

# Current Run Rate (CRR)
bbb['overs_bowled_pre'] = bbb['cum_legal_balls_pre'] / 6.0
bbb['crr_pre'] = np.where(
    bbb['overs_bowled_pre'] > 0,
    bbb['cum_runs_pre'] / bbb['overs_bowled_pre'],
    0.0
)

# Target for Innings 2
inn1_totals = bbb[bbb['innings'] == 1].groupby('match_id')['delivery_total_runs'].sum().to_dict()

def compute_target(row):
    if row['innings'] != 2:
        return np.nan
    rev_target = row['revised_target']
    if pd.notnull(rev_target) and rev_target > 0:
        return float(rev_target)
    inn1_tot = inn1_totals.get(row['match_id'], np.nan)
    if pd.notnull(inn1_tot):
        return float(inn1_tot + 1)
    return np.nan

bbb['target_score'] = bbb.apply(compute_target, axis=1)
bbb['runs_required_pre'] = np.where(
    bbb['innings'] == 2,
    np.maximum(0, bbb['target_score'] - bbb['cum_runs_pre']),
    np.nan
)
bbb['rrr_pre'] = np.where(
    (bbb['innings'] == 2) & (bbb['balls_remaining_pre'] > 0),
    (bbb['runs_required_pre'] / (bbb['balls_remaining_pre'] / 6.0)),
    np.where((bbb['innings'] == 2) & (bbb['balls_remaining_pre'] == 0), 99.0, np.nan)
)

print("Saving clean deliveries...")
bbb.to_parquet(os.path.join(OUT_PROC, "clean_deliveries.parquet"), index=False)
print("Saved clean_deliveries.parquet successfully.")

# Verify sample match
m1 = bbb[(bbb['match_id'] == 13511) & (bbb['innings'] == 1)]
print("\nSample Innings 1 check (Match 13511):")
print(m1[['innings_ball_num', 'overid', 'cum_runs_pre', 'delivery_total_runs', 'cum_runs_post', 'cum_wickets_pre', 'balls_remaining_pre']].head(10))
print(m1[['innings_ball_num', 'overid', 'cum_runs_pre', 'delivery_total_runs', 'cum_runs_post', 'cum_wickets_pre', 'balls_remaining_pre']].tail(10))
