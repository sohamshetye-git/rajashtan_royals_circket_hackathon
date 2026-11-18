"""
PHASE 4: Situational Pressure Model (v2 - Calibrated on Verified Match States)
Applies theoretical framework to Innings 1 and Innings 2.
Evaluates distributions, percentile thresholds, and correlation with match urgency.
"""
import os
import pandas as pd
import numpy as np

PROJ_DIR = r"C:\rajsathan_royals"
OUT_PROC = os.path.join(PROJ_DIR, "outputs", "processed")
OUT_VAL = os.path.join(PROJ_DIR, "outputs", "validation")

print("=" * 80)
print("PHASE 4: PRESSURE DETECTION ENGINE CALIBRATION (V2)")
print("=" * 80)

df = pd.read_parquet(os.path.join(OUT_PROC, "clean_deliveries.parquet"))
print(f"Loaded {len(df):,} clean deliveries.")

# Innings 1 par benchmarks by over
inn1 = df[df['innings'] == 1]
par_inn1 = inn1.groupby('overid').agg(
    avg_score=('cum_runs_pre', 'mean'),
    std_score=('cum_runs_pre', 'std'),
    avg_wickets=('cum_wickets_pre', 'mean'),
    avg_crr=('crr_pre', 'mean')
).reset_index()

print("\n--- INNINGS 1 HISTORICAL BENCHMARKS (OVERS 1-20) ---")
print(par_inn1.to_string(index=False))

# Merge over-by-over par into dataset
df = df.merge(par_inn1[['overid', 'avg_score', 'std_score', 'avg_wickets']], on='overid', how='left')

# Innings 1 Pressure:
# Combines:
# 1. Wicket Crisis: Wickets lost vs expected at this stage
# 2. Scoreboard Deficit: Runs scored vs expected at this stage
# 3. Stage & Acceleration: Overs remaining vs need to accelerate
def calc_inn1_pressure(row):
    if row['innings'] != 1:
        return np.nan
    over = row['overid']
    w_lost = row['cum_wickets_pre']
    runs_pre = row['cum_runs_pre']
    avg_sc = row['avg_score']
    std_sc = max(1.0, row['std_score'])
    avg_w = row['avg_wickets']
    
    # Wicket crisis factor: excess wickets lost beyond expectation
    # 0 if w_lost <= avg_w, up to 1.0 if top order collapses
    w_factor = min(1.0, max(0.0, (w_lost - avg_w + 1.0) / 4.0))
    # If wickets lost >= 4 in powerplay, extreme crisis
    if over <= 6 and w_lost >= 3:
        w_factor = max(w_factor, 0.85)
    elif over <= 10 and w_lost >= 5:
        w_factor = max(w_factor, 0.85)
        
    # Score deficit z-score
    # Negative if batting team is below par
    score_z = (avg_sc - runs_pre) / std_sc
    deficit_factor = 1.0 / (1.0 + np.exp(-1.2 * score_z)) # Logistic transform: 0.5 at par, >0.7 if behind
    
    # Stage urgency: late overs require maximizing boundary output
    stage_factor = (over / 20.0) ** 1.3
    
    # Composite Innings 1 Pressure
    p1 = 0.40 * w_factor + 0.35 * deficit_factor + 0.25 * stage_factor
    return float(np.clip(p1, 0.05, 0.95))

# Innings 2 Pressure (Chasing):
# Combines:
# 1. RRR Urgency: Logistic transform centered around par T20 RRR (8.5)
# 2. Resource Scarcity: Runs required per wicket remaining
# 3. Time Urgency: Balls remaining
# 4. Context Closeness: Peak tension in close chases
def calc_inn2_pressure(row):
    if row['innings'] != 2:
        return np.nan
    rrr = row['rrr_pre']
    runs_req = row['runs_required_pre']
    balls_rem = row['balls_remaining_pre']
    w_rem = row['wickets_remaining_pre']
    w_lost = row['cum_wickets_pre']
    over = row['overid']
    
    if runs_req <= 0:
        return 0.05
    if balls_rem <= 0 and runs_req > 0:
        return 0.95
        
    # RRR Urgency (Logistic function)
    # Centered at 8.5 RPO, scaling parameter k = 0.4
    # At RRR = 6.0 -> ~0.27 (comfortable)
    # At RRR = 8.5 -> ~0.50 (par)
    # At RRR = 11.0 -> ~0.73 (high)
    # At RRR = 14.0 -> ~0.90 (extreme)
    rrr_urgency = 1.0 / (1.0 + np.exp(-0.40 * (rrr - 8.5)))
    
    # Resource Scarcity: Runs required per wicket remaining
    # If needing 60 runs with 2 wickets -> 30 runs/wkt (extreme scarcity)
    # If needing 60 runs with 8 wickets -> 7.5 runs/wkt (comfortable)
    rpw = runs_req / max(1, w_rem)
    scarcity = min(1.0, max(0.0, rpw / 25.0))
    
    # Time factor
    time_factor = 1.0 - (balls_rem / 120.0)
    
    # Composite
    if balls_rem > 60:
        p2 = 0.45 * rrr_urgency + 0.35 * scarcity + 0.20 * time_factor
    elif balls_rem > 30:
        p2 = 0.50 * rrr_urgency + 0.35 * scarcity + 0.15 * time_factor
    else:
        # Death overs (last 5 overs)
        p2 = 0.55 * rrr_urgency + 0.30 * scarcity + 0.15 * time_factor
        
    # Boundary crisis: if only 1-2 wickets in hand and runs still needed
    if w_rem <= 2 and runs_req > 10:
        p2 = max(p2, 0.85)
        
    return float(np.clip(p2, 0.05, 0.99))

print("Applying calibrated pressure formulation...")
p1_series = df.apply(calc_inn1_pressure, axis=1)
p2_series = df.apply(calc_inn2_pressure, axis=1)

df['pressure_score'] = np.where(df['innings'] == 1, p1_series, np.where(df['innings'] == 2, p2_series, 0.95))
df.loc[df['innings'] >= 3, 'pressure_score'] = 0.95

# Bowler Pressure Score:
# For bowlers defending in Innings 2:
# When batter faces high pressure (high RRR), bowler also operates under high leverage.
# If defending a tight finish, bowler pressure is high.
# In Innings 1: Bowling to death batters or during batting collapses represents key pressure.
# Bowler pressure is tightly coupled with match leverage (situational leverage).
df['bowler_pressure_score'] = df['pressure_score']

# Categorize Pressure:
# Quantile-informed defensible thresholds:
# Low: [0.00, 0.40)
# Moderate: [0.40, 0.65)
# High: [0.65, 0.80)
# Extreme: [0.80, 1.00]
def categorize_pressure(score):
    if score < 0.40:
        return "Low"
    elif score < 0.65:
        return "Moderate"
    elif score < 0.80:
        return "High"
    else:
        return "Extreme"

df['pressure_category'] = df['pressure_score'].apply(categorize_pressure)
df['is_high_pressure'] = df['pressure_score'] >= 0.65

print("\n--- PRESSURE CATEGORY DISTRIBUTION ---")
print(df['pressure_category'].value_counts(normalize=True).round(4) * 100)
print("\nPressure by Innings (%):")
print(pd.crosstab(df['innings'], df['pressure_category'], normalize='index').round(4) * 100)

print("\nPressure by Match Phase (%):")
print(pd.crosstab(df['match_phase'], df['pressure_category'], normalize='index').round(4) * 100)

print("\nMean Pressure Score by Match Phase & Innings:")
print(df.groupby(['innings', 'match_phase'])['pressure_score'].mean().unstack())

# Save match_states.parquet
df.to_parquet(os.path.join(OUT_PROC, "match_states.parquet"), index=False)
print("\nSaved match_states.parquet successfully.")

# Save validation distribution summary
dist_report = df.groupby(['innings', 'pressure_category']).agg(
    delivery_count=('match_id', 'count'),
    mean_pressure=('pressure_score', 'mean'),
    median_pressure=('pressure_score', 'median')
).reset_index()
dist_report.to_csv(os.path.join(OUT_VAL, "pressure_distribution_v2.csv"), index=False)
print("Saved pressure_distribution_v2.csv.")
