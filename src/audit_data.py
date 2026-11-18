"""
PHASE 1: Comprehensive Dataset Audit Script
Inspects all CSV files, extracts schemas, row counts, unique IDs, missing values,
and cross-table relational integrity.
"""
import os
import pandas as pd
import numpy as np

DATA_DIR = r"C:\rajsathan_royals\data\Data Pack"
OUTPUT_DIR = r"C:\rajsathan_royals\outputs\validation"

csv_files = [
    "competitions.csv",
    "teams.csv",
    "matches.csv",
    "playing_eleven.csv",
    "competition_team_player_mapping.csv",
    "ball_by_ball.csv"
]

print("=" * 80)
print("PHASE 1: COMPREHENSIVE DATASET AUDIT")
print("=" * 80)

audit_records = []

for filename in csv_files:
    filepath = os.path.join(DATA_DIR, filename)
    print(f"\n--- AUDITING: {filename} ---")
    df = pd.read_csv(filepath, low_memory=False)
    
    nrows, ncols = df.shape
    dups = df.duplicated().sum()
    print(f"Shape: {nrows:,} rows x {ncols} columns | Duplicate rows: {dups:,}")
    print("Columns and Non-Null Counts:")
    for col in df.columns:
        n_null = df[col].isnull().sum()
        pct_null = (n_null / nrows) * 100
        n_uniq = df[col].nunique()
        dtype = str(df[col].dtype)
        sample_vals = df[col].dropna().unique()[:3].tolist()
        audit_records.append({
            "file": filename,
            "column": col,
            "dtype": dtype,
            "non_null_count": nrows - n_null,
            "null_count": n_null,
            "null_pct": round(pct_null, 2),
            "unique_count": n_uniq,
            "sample_values": str(sample_vals)
        })
        print(f"  - {col} ({dtype}): {n_null:,} nulls ({pct_null:.1f}%), {n_uniq:,} unique, sample: {sample_vals}")

audit_df = pd.DataFrame(audit_records)
audit_df.to_csv(os.path.join(OUTPUT_DIR, "dataset_columns_audit.csv"), index=False)
print("\nColumn audit saved to dataset_columns_audit.csv")

# Now check competitions specifically
print("\n" + "=" * 80)
print("COMPETITIONS AUDIT")
print("=" * 80)
comp_df = pd.read_csv(os.path.join(DATA_DIR, "competitions.csv"))
print(comp_df.to_string())

# Check matches per competition
matches_df = pd.read_csv(os.path.join(DATA_DIR, "matches.csv"))
print("\n" + "=" * 80)
print("MATCHES AUDIT")
print("=" * 80)
print(f"Total Matches: {len(matches_df)}")
print("\nMatches by comp_id:")
matches_comp = matches_df.merge(comp_df, on="comp_id", how="left")
summary = matches_comp.groupby(["comp_id", "name", "season"]).size().reset_index(name="match_count")
print(summary.to_string())

# Check ball_by_ball deliveries per competition & match
print("\n" + "=" * 80)
print("BALL BY BALL AUDIT")
print("=" * 80)
bbb_df = pd.read_csv(os.path.join(DATA_DIR, "ball_by_ball.csv"), low_memory=False)
bbb_matches = bbb_df["match_id"].nunique()
print(f"Total Deliveries: {len(bbb_df):,}")
print(f"Matches in ball_by_ball: {bbb_matches:,} (vs {len(matches_df):,} in matches.csv)")

# Check orphans
bbb_orphan_matches = set(bbb_df["match_id"]) - set(matches_df["match_id"])
matches_without_bbb = set(matches_df["match_id"]) - set(bbb_df["match_id"])
print(f"Orphan match_ids in ball_by_ball: {len(bbb_orphan_matches)}")
print(f"Matches in matches.csv without ball_by_ball deliveries: {len(matches_without_bbb)}")

# Check delivery extras and runs structure
print("\nRuns & Extras columns in ball_by_ball:")
run_cols = [c for c in bbb_df.columns if "run" in c.lower() or "extra" in c.lower() or "wide" in c.lower() or "noball" in c.lower() or "bye" in c.lower() or "wicket" in c.lower() or "dismiss" in c.lower()]
print(run_cols)
for c in run_cols:
    print(f"Value counts for {c}:")
    print(bbb_df[c].value_counts(dropna=False).head(10))
    print()

# Check player mappings
print("\n" + "=" * 80)
print("PLAYER INTEGRITY AUDIT")
print("=" * 80)
p11_df = pd.read_csv(os.path.join(DATA_DIR, "playing_eleven.csv"))
mapping_df = pd.read_csv(os.path.join(DATA_DIR, "competition_team_player_mapping.csv"))

print(f"Playing Eleven rows: {len(p11_df):,}, unique players: {p11_df['player_id'].nunique():,}")
print(f"Mapping rows: {len(mapping_df):,}, unique players: {mapping_df['player_id'].nunique():,}")

batters_in_bbb = set(bbb_df["batter_id"].dropna().unique())
bowlers_in_bbb = set(bbb_df["bowler_id"].dropna().unique())
all_bbb_players = batters_in_bbb | bowlers_in_bbb
print(f"Unique Batters in BBB: {len(batters_in_bbb):,}")
print(f"Unique Bowlers in BBB: {len(bowlers_in_bbb):,}")
print(f"Total Unique Players in BBB: {len(all_bbb_players):,}")

unmapped_batters = batters_in_bbb - set(mapping_df["player_id"])
unmapped_bowlers = bowlers_in_bbb - set(mapping_df["player_id"])
print(f"Batters missing from player mapping: {len(unmapped_batters)}")
print(f"Bowlers missing from player mapping: {len(unmapped_bowlers)}")

print("\nAUDIT FINISHED SUCCESSFULLY.")
