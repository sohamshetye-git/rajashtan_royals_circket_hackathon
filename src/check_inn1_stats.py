"""
PHASE 4 Refinement: Check Innings 1 cumulative runs vs runs in over,
and calibrate continuous pressure score distribution.
"""
import os
import pandas as pd

df = pd.read_parquet(r"C:\rajsathan_royals\outputs\processed\match_states.parquet")

inn1 = df[df['innings'] == 1]
print("Innings 1 cum_runs_pre stats by overid:")
stats = inn1.groupby('overid')['cum_runs_pre'].agg(['mean', 'median', 'std', 'min', 'max'])
print(stats)

print("\nInnings 1 cum_wickets_pre stats by overid:")
w_stats = inn1.groupby('overid')['cum_wickets_pre'].agg(['mean', 'median', 'std', 'min', 'max'])
print(w_stats)
