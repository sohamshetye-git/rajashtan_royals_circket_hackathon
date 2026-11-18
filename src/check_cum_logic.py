"""
Check cumulative runs logic in match_state_engine
"""
import os
import pandas as pd

df = pd.read_parquet(r"C:\rajsathan_royals\outputs\processed\clean_deliveries.parquet")
m1 = df[(df['match_id'] == 13511) & (df['innings'] == 1)]
print(m1[['innings_ball_num', 'overid', 'over_ball_num', 'delivery_total_runs', 'cum_runs_post', 'cum_runs_pre']].head(15))
print(m1[['innings_ball_num', 'overid', 'over_ball_num', 'delivery_total_runs', 'cum_runs_post', 'cum_runs_pre']].tail(15))
