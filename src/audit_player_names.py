"""
Audit players in ball_by_ball vs competition_team_player_mapping.csv
"""
import os
import pandas as pd

DATA_DIR = r"C:\rajsathan_royals\data\Data Pack"
bbb = pd.read_csv(os.path.join(DATA_DIR, "ball_by_ball.csv"), low_memory=False)
mapping = pd.read_csv(os.path.join(DATA_DIR, "competition_team_player_mapping.csv"))
p11 = pd.read_csv(os.path.join(DATA_DIR, "playing_eleven.csv"))

batters = bbb[['striker_id', 'striker_name']].drop_duplicates().rename(columns={'striker_id': 'player_id', 'striker_name': 'name'})
bowlers = bbb[['bowler_id', 'bowler_name']].drop_duplicates().rename(columns={'bowler_id': 'player_id', 'bowler_name': 'name'})

all_bbb_players = pd.concat([batters, bowlers]).drop_duplicates(subset=['player_id'])
print(f"Total unique players in ball_by_ball: {len(all_bbb_players)}")

mapped_ids = set(mapping['player_id'].unique())
p11_ids = set(p11['player_id'].unique())

missing_from_mapping = all_bbb_players[~all_bbb_players['player_id'].isin(mapped_ids)]
print(f"Players in BBB missing from mapping: {len(missing_from_mapping)}")
if len(missing_from_mapping) > 0:
    print(missing_from_mapping.head(10))

missing_from_p11 = all_bbb_players[~all_bbb_players['player_id'].isin(p11_ids)]
print(f"Players in BBB missing from playing_eleven: {len(missing_from_p11)}")

# Check name consistency between bbb and mapping
merged_names = mapping[['player_id', 'player_name']].drop_duplicates().merge(all_bbb_players, on='player_id')
print(f"Merged player count: {len(merged_names)}")
name_mismatches = merged_names[merged_names['player_name'] != merged_names['name']]
print(f"Name mismatches between BBB and mapping: {len(name_mismatches)}")
if len(name_mismatches) > 0:
    print(name_mismatches.head(10))
