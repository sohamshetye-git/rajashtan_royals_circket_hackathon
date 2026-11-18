"""
PHASE 1: Deep Audit & Cricket Mechanics Inspector (v3)
Inspects the actual columns:
overid, over_ball_num, innings_ball_num, striker_id, striker_name, non_striker_id, non_striker_name,
bowler_id, bowler_name, runs, is_four, is_six, is_wicket, dismissal_type_id, dismissal_type,
dismissed_player_id, extras_type, extras1_runs, extras_2_runs, pace_or_spin, bowl_speed, stroke, delivery_style, etc.
"""
import os
import pandas as pd
import numpy as np

DATA_DIR = r"C:\rajsathan_royals\data\Data Pack"
OUTPUT_DIR = r"C:\rajsathan_royals\outputs\validation"
os.makedirs(OUTPUT_DIR, exist_ok=True)

bbb = pd.read_csv(os.path.join(DATA_DIR, "ball_by_ball.csv"), low_memory=False)

print("=" * 80)
print("BALL-BY-BALL DEEP MECHANICS INSPECTION")
print("=" * 80)
print(f"Total rows: {len(bbb):,}")
print(f"Columns: {list(bbb.columns)}")

print("\n--- OVERID & OVER_BALL_NUM DISTRIBUTION ---")
print(f"overid min: {bbb['overid'].min()}, max: {bbb['overid'].max()}")
print("overid value counts (sample):")
print(bbb['overid'].value_counts().sort_index())

print("\n--- OVER_BALL_NUM DISTRIBUTION ---")
print(bbb['over_ball_num'].value_counts().sort_index())

print("\n--- INNINGS_BALL_NUM DISTRIBUTION ---")
print(f"innings_ball_num min: {bbb['innings_ball_num'].min()}, max: {bbb['innings_ball_num'].max()}")

print("\n--- RUNS DISTRIBUTION ---")
print(bbb['runs'].value_counts().sort_index())

print("\n--- EXTRAS TYPE & EXTRAS RUNS ---")
print("extras_type distribution:")
print(bbb['extras_type'].value_counts(dropna=False))
print("\nextras1_runs distribution:")
print(bbb['extras1_runs'].value_counts(dropna=False).head(10))
print("\nextras_2_runs distribution:")
print(bbb['extras_2_runs'].value_counts(dropna=False).head(10))

# Cross-tab extras_type vs runs vs extras1_runs vs extras_2_runs
print("\nSample rows with extras:")
sample_extras = bbb[bbb['extras_type'].notnull()][['runs', 'extras_type', 'extras1_runs', 'extras_2_runs', 'is_four', 'is_six']].drop_duplicates()
print(sample_extras.head(25))

# What does runs represent when extras_type is Wide?
print("\nWhen extras_type == 'Wide':")
print(bbb[bbb['extras_type'] == 'Wide'][['runs', 'extras1_runs', 'extras_2_runs']].drop_duplicates().head(10))

# What does runs represent when extras_type is No Ball?
print("\nWhen extras_type == 'No Ball':")
print(bbb[bbb['extras_type'] == 'No Ball'][['runs', 'extras1_runs', 'extras_2_runs', 'is_four', 'is_six']].drop_duplicates().head(10))

# What does runs represent when extras_type is Leg Bye or Bye?
print("\nWhen extras_type == 'Leg Bye':")
print(bbb[bbb['extras_type'] == 'Leg Bye'][['runs', 'extras1_runs', 'extras_2_runs']].drop_duplicates().head(10))
print("\nWhen extras_type == 'Bye':")
print(bbb[bbb['extras_type'] == 'Bye'][['runs', 'extras1_runs', 'extras_2_runs']].drop_duplicates().head(10))

# Wickets & Dismissal types
print("\n--- WICKETS & DISMISSALS ---")
print("is_wicket value counts:")
print(bbb['is_wicket'].value_counts(dropna=False))
print("\ndismissal_type value counts:")
print(bbb['dismissal_type'].value_counts(dropna=False))
print("\ndismissal_type_id vs dismissal_type:")
print(bbb[['dismissal_type_id', 'dismissal_type']].drop_duplicates().sort_values('dismissal_type_id'))

# Check non-bowler wickets: Run Out, Retired Hurt, Obstructing the field, Timed Out, etc.
bowler_wickets = ['Bowled', 'Caught', 'Caught Behind', 'Caught & Bowled', 'Lbw', 'Stumped', 'Hit Wicket']
print("\nDismissals breakdown by Bowler-Credited vs Non-Bowler-Credited:")
for dt in bbb['dismissal_type'].dropna().unique():
    count = (bbb['dismissal_type'] == dt).sum()
    is_bowler = dt in bowler_wickets
    print(f"  - {dt}: {count:,} dismissals (Bowler credited: {is_bowler})")

# Check 16 matches in matches.csv that have 0 deliveries in ball_by_ball
matches = pd.read_csv(os.path.join(DATA_DIR, "matches.csv"))
missing_match_ids = set(matches['match_id']) - set(bbb['match_id'])
print("\n--- 16 MATCHES WITHOUT DELIVERIES ---")
missing_matches = matches[matches['match_id'].isin(missing_match_ids)]
print(missing_matches[['match_id', 'match_date', 'home_team', 'away_team', 'result']])

# Check other T20 competitions in competitions.csv
comps = pd.read_csv(os.path.join(DATA_DIR, "competitions.csv"))
t20_comps = comps[comps['match_format'] == 'T20']
print("\n--- ALL T20 FORMAT COMPETITIONS ---")
print(t20_comps[['comp_id', 'comp_name', 'season']])

# Check matches per T20 competition
matches_comp = matches.merge(comps, on="comp_id", how="left")
print("\nT20 matches per competition:")
print(matches_comp[matches_comp['match_format'] == 'T20'].groupby(['comp_id', 'comp_name', 'season']).size().reset_index(name='matches'))

print("\n--- INSPECTION COMPLETE ---")
