"""
PHASE 1: Comprehensive Dataset Audit Script (v2)
Corrected column names and deep inspects all schemas, values, distributions, and links.
"""
import os
import pandas as pd
import numpy as np

DATA_DIR = r"C:\rajsathan_royals\data\Data Pack"
OUTPUT_DIR = r"C:\rajsathan_royals\outputs\validation"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Competitions
print("=" * 80)
print("1. COMPETITIONS AUDIT")
print("=" * 80)
comp_df = pd.read_csv(os.path.join(DATA_DIR, "competitions.csv"))
print(f"Competitions: {len(comp_df)} rows, columns: {list(comp_df.columns)}")
print(comp_df["match_format"].value_counts())
print("\nUnique formats and seasons:")
print(comp_df.groupby(["match_format", "season"]).size().unstack(fill_value=0))
print("\nSample competitions:")
print(comp_df.head(10))

# Identify IPL competitions vs T20I
ipl_comps = comp_df[comp_df["comp_name"].str.contains("IPL|Indian Premier League", case=False, na=False)]
print(f"\nIPL Competitions found ({len(ipl_comps)}):")
print(ipl_comps[["comp_id", "comp_name", "match_format", "season"]].to_string())

# 2. Teams
print("\n" + "=" * 80)
print("2. TEAMS AUDIT")
print("=" * 80)
teams_df = pd.read_csv(os.path.join(DATA_DIR, "teams.csv"))
print(f"Teams: {len(teams_df)} rows, unique teams: {teams_df['team_id'].nunique()}")
print("Unique team names:")
print(teams_df[["team_id", "team_name"]].drop_duplicates().sort_values("team_name").to_string(index=False))

# 3. Matches
print("\n" + "=" * 80)
print("3. MATCHES AUDIT")
print("=" * 80)
matches_df = pd.read_csv(os.path.join(DATA_DIR, "matches.csv"))
print(f"Total Matches: {len(matches_df)}")
print(f"Columns: {list(matches_df.columns)}")

matches_comp = matches_df.merge(comp_df, on="comp_id", how="left")
print(f"Matches joined with comp_df nulls in comp_name: {matches_comp['comp_name'].isnull().sum()}")

# Summary by format & season
summary = matches_comp.groupby(["match_format", "season"]).agg(
    match_count=("match_id", "count"),
    start_date=("match_date", "min"),
    end_date=("match_date", "max")
).reset_index()
print("\nMatches breakdown by Format and Season:")
print(summary.to_string())

# Check IPL matches specifically
ipl_matches = matches_comp[matches_comp["comp_name"].str.contains("IPL|Indian Premier League", case=False, na=False)]
print(f"\nTotal IPL Matches: {len(ipl_matches)} across seasons {ipl_matches['season'].unique()}")
print(ipl_matches.groupby(["comp_id", "comp_name", "season"]).size().reset_index(name="matches"))

# 4. Ball by Ball
print("\n" + "=" * 80)
print("4. BALL BY BALL DEEP AUDIT")
print("=" * 80)
bbb_df = pd.read_csv(os.path.join(DATA_DIR, "ball_by_ball.csv"), low_memory=False)
print(f"BBB Rows: {len(bbb_df):,}, Columns: {len(bbb_df.columns)}")
print(f"BBB Columns: {list(bbb_df.columns)}")

# Check matches in BBB vs matches.csv
bbb_match_ids = set(bbb_df["match_id"].unique())
matches_ids = set(matches_df["match_id"].unique())
print(f"Matches in matches.csv: {len(matches_ids)}")
print(f"Matches in ball_by_ball: {len(bbb_match_ids)}")
print(f"Matches in matches.csv but NOT in BBB: {len(matches_ids - bbb_match_ids)}")
print(f"Matches in BBB but NOT in matches.csv: {len(bbb_match_ids - matches_ids)}")

# Deliveries per innings
print("\nDeliveries by innings:")
print(bbb_df["innings"].value_counts().sort_index())

# Check over and ball numbering
print(f"Over range: {bbb_df['over'].min()} to {bbb_df['over'].max()}")
print(f"Ball range: {bbb_df['ball'].min()} to {bbb_df['ball'].max()}")

# Inspect runs and extras breakdown
print("\n--- RUNS AND EXTRAS STRUCTURE ---")
run_cols = ['runs', 'batter_runs', 'extra_runs', 'extra_type', 'is_wide', 'is_noball', 'is_bye', 'is_legbye', 'is_penalty']
available_run_cols = [c for c in run_cols if c in bbb_df.columns]
print("Available run cols:", available_run_cols)
for c in available_run_cols:
    print(f"\nColumn: {c}")
    print(bbb_df[c].value_counts(dropna=False).head(10))

# Test mathematical relationships:
# Does runs == batter_runs + extra_runs?
if 'batter_runs' in bbb_df.columns and 'extra_runs' in bbb_df.columns:
    diff = bbb_df['runs'] - (bbb_df['batter_runs'] + bbb_df['extra_runs'])
    print(f"\nDoes runs == batter_runs + extra_runs for all rows? {(diff == 0).all()}")
    if not (diff == 0).all():
        print(f"Mismatches: {(diff != 0).sum()}")
        print(bbb_df[diff != 0][['runs', 'batter_runs', 'extra_runs', 'extra_type']].head())

# Inspect Wickets
print("\n--- WICKETS & DISMISSALS STRUCTURE ---")
wicket_cols = [c for c in bbb_df.columns if 'wicket' in c.lower() or 'dismiss' in c.lower() or 'out' in c.lower()]
print("Wicket cols:", wicket_cols)
for c in wicket_cols:
    print(f"\nColumn: {c}")
    print(bbb_df[c].value_counts(dropna=False).head(15))

# Check player mappings
print("\n" + "=" * 80)
print("5. PLAYER MAPPING & PLAYING ELEVEN AUDIT")
print("=" * 80)
p11_df = pd.read_csv(os.path.join(DATA_DIR, "playing_eleven.csv"))
mapping_df = pd.read_csv(os.path.join(DATA_DIR, "competition_team_player_mapping.csv"))

print(f"Playing 11 rows: {len(p11_df)}, unique player_ids: {p11_df['player_id'].nunique()}")
print(f"Player mapping rows: {len(mapping_df)}, unique player_ids: {mapping_df['player_id'].nunique()}")

# Unique names per player_id
name_counts = mapping_df.groupby('player_id')['player_name'].nunique()
multinamed_players = name_counts[name_counts > 1]
print(f"Players with multiple names: {len(multinamed_players)}")
if len(multinamed_players) > 0:
    print("Examples of multi-named players:")
    print(mapping_df[mapping_df['player_id'].isin(multinamed_players.index[:5])][['player_id', 'player_name']].drop_duplicates())

# Unique IDs per player_name
id_counts = mapping_df.groupby('player_name')['player_id'].nunique()
multi_id_names = id_counts[id_counts > 1]
print(f"Names with multiple player_ids: {len(multi_id_names)}")
if len(multi_id_names) > 0:
    print("Examples of multi-ID names:")
    print(mapping_df[mapping_df['player_name'].isin(multi_id_names.index[:5])][['player_name', 'player_id']].drop_duplicates())

# Check player ID overlap between BBB and mapping
batters = set(bbb_df['batter_id'].unique())
bowlers = set(bbb_df['bowler_id'].unique())
non_strikers = set(bbb_df['non_striker_id'].unique())
all_bbb_players = batters | bowlers | non_strikers
mapped_players = set(mapping_df['player_id'].unique())

print(f"\nTotal players in BBB: {len(all_bbb_players)}")
print(f"BBB players present in mapping: {len(all_bbb_players & mapped_players)}")
print(f"BBB players missing from mapping: {len(all_bbb_players - mapped_players)}")
if len(all_bbb_players - mapped_players) > 0:
    print("Missing player IDs sample:", list(all_bbb_players - mapped_players)[:10])

print("\n" + "=" * 80)
print("AUDIT COMPLETE")
print("=" * 80)
