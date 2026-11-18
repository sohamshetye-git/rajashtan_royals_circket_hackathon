"""
Deep Investigation into Extras and Delivery Legality
"""
import os
import pandas as pd

DATA_DIR = r"C:\rajsathan_royals\data\Data Pack"
bbb = pd.read_csv(os.path.join(DATA_DIR, "ball_by_ball.csv"), low_memory=False)

print("Unique extras_type:", bbb['extras_type'].unique())

for et in bbb['extras_type'].unique():
    subset = bbb[bbb['extras_type'] == et] if pd.notnull(et) else bbb[bbb['extras_type'].isnull()]
    print(f"\n--- EXTRAS TYPE: {et} (Count: {len(subset)}) ---")
    print("runs value counts:")
    print(subset['runs'].value_counts().head(5).to_dict())
    print("extras1_runs value counts:")
    print(subset['extras1_runs'].value_counts().head(5).to_dict())
    print("extras_2_runs value counts:")
    print(subset['extras_2_runs'].value_counts().head(5).to_dict())
    sample = subset[['runs', 'extras_type', 'extras1_runs', 'extras_2_runs', 'is_four', 'is_six', 'dismissal_type']].head(5)
    print(sample.to_string())
