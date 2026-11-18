"""
Deep Audit of Player Innings and Format Splits
"""
import pandas as pd

top10_bat = pd.read_csv('C:/rajsathan_royals/outputs/rankings/batter_top10.csv')
top10_bowl = pd.read_csv('C:/rajsathan_royals/outputs/rankings/bowler_top10.csv')
df = pd.read_parquet('C:/rajsathan_royals/outputs/processed/match_states.parquet')
df_scope = df[df['competition_type'].isin(['IPL', 'T20I'])]

print('=== TOP 10 BATTERS INNINGS & FORMAT SPLIT ===')
for idx, r in top10_bat.iterrows():
    p_del = df_scope[(df_scope['striker_id'] == r['striker_id']) & (df_scope['is_high_pressure'])]
    inn1_b = (p_del['innings'] == 1).sum()
    inn2_b = (p_del['innings'] == 2).sum()
    ipl_b = (p_del['competition_type'] == 'IPL').sum()
    t20i_b = (p_del['competition_type'] == 'T20I').sum()
    pct1 = (inn1_b / len(p_del)) * 100 if len(p_del) > 0 else 0
    pct2 = (inn2_b / len(p_del)) * 100 if len(p_del) > 0 else 0
    print(f"{int(r['Rank'])}. {r['player_name']}: total_p_balls={len(p_del)} | Inn1={inn1_b} ({pct1:.1f}%), Inn2={inn2_b} ({pct2:.1f}%) | IPL={ipl_b}, T20I={t20i_b}")

print('\n=== TOP 10 BOWLERS INNINGS & FORMAT SPLIT ===')
for idx, r in top10_bowl.iterrows():
    p_del = df_scope[(df_scope['bowler_id'] == r['bowler_id']) & (df_scope['is_high_pressure']) & (df_scope['is_legal_ball'])]
    inn1_b = (p_del['innings'] == 1).sum()
    inn2_b = (p_del['innings'] == 2).sum()
    ipl_b = (p_del['competition_type'] == 'IPL').sum()
    t20i_b = (p_del['competition_type'] == 'T20I').sum()
    pct1 = (inn1_b / len(p_del)) * 100 if len(p_del) > 0 else 0
    pct2 = (inn2_b / len(p_del)) * 100 if len(p_del) > 0 else 0
    print(f"{int(r['Rank'])}. {r['player_name']}: total_p_balls={len(p_del)} | Inn1={inn1_b} ({pct1:.1f}%), Inn2={inn2_b} ({pct2:.1f}%) | IPL={ipl_b}, T20I={t20i_b}")
