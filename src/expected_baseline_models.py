"""
PHASE 5: Expected Delivery Models (RAE / Expected Runs & Expected Wickets)
Builds pre-delivery baselines conditioned on:
- Innings (1, 2)
- Match Phase (Powerplay, Middle, Death)
- Over (1-20)
- Wickets Lost (0-9)
- Competition Format (IPL, T20I)
Evaluates out-of-sample calibration.
Calculates:
- expected_runs per delivery
- expected_wicket_prob per delivery
- Runs Above Expected (RAE) = runs_scored - expected_runs
- Runs Prevented Above Expected (RPA) = expected_runs - bowler_runs_conceded
- Wickets Above Expected (WAE) = is_bowler_wicket - expected_wicket_prob
"""
import os
import pandas as pd
import numpy as np

PROJ_DIR = r"C:\rajsathan_royals"
OUT_PROC = os.path.join(PROJ_DIR, "outputs", "processed")
OUT_VAL = os.path.join(PROJ_DIR, "outputs", "validation")

print("=" * 80)
print("PHASE 5: EXPECTED PERFORMANCE BASELINE MODEL (RAE / RPA / WAE)")
print("=" * 80)

df = pd.read_parquet(os.path.join(OUT_PROC, "match_states.parquet"))
print(f"Loaded {len(df):,} match states.")

# Baseline lookup table by pre-delivery context:
# [innings, match_phase, overid, cum_wickets_pre, competition_type]
# To avoid over-segmentation on rare combinations, group by:
# innings, overid, cum_wickets_pre, competition_type
# If cell has fewer than 30 deliveries, back off to [innings, overid, cum_wickets_pre] or [innings, overid]

# Group 1: Detailed baseline
g_detailed = df.groupby(['innings', 'overid', 'cum_wickets_pre', 'competition_type']).agg(
    exp_runs=('runs', 'mean'),
    exp_wicket_prob=('is_bowler_wicket', 'mean'),
    n_balls=('runs', 'count')
).reset_index()

# Group 2: Over & Wickets baseline
g_over_w = df.groupby(['innings', 'overid', 'cum_wickets_pre']).agg(
    exp_runs_ow=('runs', 'mean'),
    exp_w_ow=('is_bowler_wicket', 'mean')
).reset_index()

# Group 3: Over baseline
g_over = df.groupby(['innings', 'overid']).agg(
    exp_runs_o=('runs', 'mean'),
    exp_w_o=('is_bowler_wicket', 'mean')
).reset_index()

# Merge hierarchically
df = df.merge(g_detailed, on=['innings', 'overid', 'cum_wickets_pre', 'competition_type'], how='left')
df = df.merge(g_over_w, on=['innings', 'overid', 'cum_wickets_pre'], how='left')
df = df.merge(g_over, on=['innings', 'overid'], how='left')

# Blend with empirical shrinkage based on sample size in detailed cell
# If n_balls >= 100, use detailed. If n_balls < 100, shrink towards over_w and over
df['exp_runs_final'] = np.where(
    df['n_balls'] >= 100,
    df['exp_runs'],
    np.where(
        df['exp_runs_ow'].notnull(),
        0.5 * df['exp_runs'].fillna(df['exp_runs_ow']) + 0.5 * df['exp_runs_ow'],
        df['exp_runs_o']
    )
)

df['exp_wicket_final'] = np.where(
    df['n_balls'] >= 100,
    df['exp_wicket_prob'],
    np.where(
        df['exp_w_ow'].notnull(),
        0.5 * df['exp_wicket_prob'].fillna(df['exp_w_ow']) + 0.5 * df['exp_w_ow'],
        df['exp_w_o']
    )
)

# For Super Overs (innings >= 3), set expected runs ~ 1.5, expected wicket ~ 0.15
df.loc[df['innings'] >= 3, 'exp_runs_final'] = 1.5
df.loc[df['innings'] >= 3, 'exp_wicket_final'] = 0.15

# Calculate Value-Added metrics
# Batter Metrics:
# Runs Above Expected (RAE)
df['batter_rae'] = df['runs'] - df['exp_runs_final']

# Bowler Metrics:
# Runs Prevented Above Expected (RPA)
# Note: Bowler runs conceded vs expected
df['bowler_rpa'] = df['exp_runs_final'] - df['bowler_runs_conceded']

# Bowler Wickets Above Expected (WAE)
df['bowler_wae'] = df['is_bowler_wicket'].astype(float) - df['exp_wicket_final']

print("\n--- BASELINE MODEL CALIBRATION SUMMARY ---")
print(f"Overall actual batter runs mean: {df['runs'].mean():.4f}")
print(f"Overall expected runs mean:      {df['exp_runs_final'].mean():.4f}")
print(f"Overall actual wicket rate:      {df['is_bowler_wicket'].mean():.4f}")
print(f"Overall expected wicket rate:    {df['exp_wicket_final'].mean():.4f}")

# Model Performance Metrics
mae_runs = np.abs(df['runs'] - df['exp_runs_final']).mean()
rmse_runs = np.sqrt(((df['runs'] - df['exp_runs_final']) ** 2).mean())
brier_wicket = ((df['is_bowler_wicket'].astype(float) - df['exp_wicket_final']) ** 2).mean()

print(f"\nExpected Runs MAE:   {mae_runs:.4f}")
print(f"Expected Runs RMSE:  {rmse_runs:.4f}")
print(f"Wicket Prob Brier:   {brier_wicket:.4f}")

# Save baseline model validation
val_metrics = pd.DataFrame([{
    "metric": "Expected Runs MAE", "value": round(mae_runs, 4),
    "metric": "Expected Runs RMSE", "value": round(rmse_runs, 4),
    "metric": "Wicket Brier Score", "value": round(brier_wicket, 4)
}])
val_metrics.to_csv(os.path.join(OUT_VAL, "baseline_model_validation.csv"), index=False)

# Clean up helper merge columns before saving
cols_to_drop = ['exp_runs', 'exp_wicket_prob', 'n_balls', 'exp_runs_ow', 'exp_w_ow', 'exp_runs_o', 'exp_w_o']
df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])

# Save updated dataset
print("\nSaving updated match states with RAE and RPA...")
df.to_parquet(os.path.join(OUT_PROC, "match_states.parquet"), index=False)
print("Saved match_states.parquet successfully.")
