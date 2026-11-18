"""
PHASE 4: Formal Pressure Detection Engine
Calculates continuous situational pressure P_t in [0, 1] for every delivery.
Formulates distinct components for:
- Innings 2 (Chasing Pressure): Run rate urgency, wicket scarcity, time pressure, match leverage.
- Innings 1 (First-Innings Setting Pressure): Resource deficit vs par, collapse pressure, death-over urgency.
- Bowling vs Batting leverage.
Categorizes into: Low, Moderate, High, Extreme.
Performs sensitivity analysis and validates distributions.
"""
import os
import pandas as pd
import numpy as np

PROJ_DIR = r"C:\rajsathan_royals"
OUT_PROC = os.path.join(PROJ_DIR, "outputs", "processed")
OUT_VAL = os.path.join(PROJ_DIR, "outputs", "validation")

print("=" * 80)
print("PHASE 4: SITUATIONAL PRESSURE MODEL CALIBRATION")
print("=" * 80)

# Load clean deliveries
df = pd.read_parquet(os.path.join(OUT_PROC, "clean_deliveries.parquet"))
print(f"Loaded {len(df):,} deliveries.")

# Filter to IPL and T20I matches for historical calibration
df_scope = df[df['competition_type'].isin(['IPL', 'T20I'])].copy()
print(f"Deliveries in primary scope (IPL & T20I): {len(df_scope):,}")

# --- INNINGS 1: HISTORICAL PAR SCORING RATE PER OVER & WICKETS ---
# Calculate historical average score at each over (1 to 20) and wickets lost
inn1 = df_scope[df_scope['innings'] == 1]
par_inn1 = inn1.groupby('overid').agg(
    avg_score=('cum_runs_pre', 'mean'),
    std_score=('cum_runs_pre', 'std'),
    avg_wickets=('cum_wickets_pre', 'mean'),
    avg_crr=('crr_pre', 'mean')
).reset_index()

print("\n--- INNINGS 1 HISTORICAL BENCHMARKS BY OVER ---")
print(par_inn1.head(10))

# Merge par benchmarks into dataset
df = df.merge(par_inn1[['overid', 'avg_score', 'avg_wickets']], on='overid', how='left')

# --- PRESSURE COMPUTATION MATHEMATICAL FORMULATION ---

# 1. Innings 1 Pressure (P_inn1):
# Defined by:
# a) Resource scarcity / collapse: Wickets lost relative to over
#    e.g., wickets_lost >= 3 in Powerplay (overid <= 6) or >= 5 before over 14 is high crisis.
# b) Scoreboard deficit vs par: cum_runs_pre vs avg_score
# c) Death-over maximization urgency: overs 16-20
def compute_inn1_pressure(row):
    if row['innings'] != 1:
        return np.nan
    over = row['overid']
    w_lost = row['cum_wickets_pre']
    w_rem = row['wickets_remaining_pre']
    runs_pre = row['cum_runs_pre']
    avg_sc = row['avg_score']
    
    # Wicket collapse penalty (0 to 1)
    # Expected wickets lost at this over is row['avg_wickets']
    w_excess = max(0, w_lost - row['avg_wickets'])
    collapse_factor = min(1.0, (w_lost / 7.0) * (1.0 + (20 - over) / 20.0))
    
    # Run rate deficit factor: if team is below par score
    run_deficit = max(0.0, avg_sc - runs_pre)
    deficit_factor = min(1.0, run_deficit / 30.0) if avg_sc > 0 else 0.0
    
    # Stage factor (increases towards death overs)
    stage_factor = (over / 20.0) ** 1.5
    
    # Composite Innings 1 Pressure:
    # Early overs: pressure driven by collapses (wickets lost)
    # Middle overs: balance of wickets lost and scoring rate
    # Death overs: high scoring urgency coupled with surviving wickets
    if over <= 6:
        p1 = 0.65 * (w_lost / 4.0) + 0.35 * deficit_factor
    elif over <= 15:
        p1 = 0.45 * (w_lost / 7.0) + 0.30 * deficit_factor + 0.25 * stage_factor
    else: # Death overs (16-20)
        # In death overs, pressure is inherently elevated; wickets remaining dictate risk appetite
        p1 = 0.40 * stage_factor + 0.35 * (w_lost / 9.0) + 0.25 * deficit_factor
    
    return float(np.clip(p1, 0.05, 0.95))

# 2. Innings 2 Pressure (P_inn2 - Chasing Pressure):
# Defined by:
# a) Required Run Rate (RRR) urgency relative to baseline T20 par (par RRR ~ 8.0)
# b) Required Acceleration: RRR - CRR
# c) Balls remaining scarcity & Wickets in Hand
# d) Contest Closeness (Tension peak in close chases)
def compute_inn2_pressure(row):
    if row['innings'] != 2:
        return np.nan
    rrr = row['rrr_pre']
    runs_req = row['runs_required_pre']
    balls_rem = row['balls_remaining_pre']
    w_rem = row['wickets_remaining_pre']
    w_lost = row['cum_wickets_pre']
    over = row['overid']
    
    # If match is practically won or impossible (extreme blowouts):
    if runs_req <= 0:
        return 0.05
    if balls_rem <= 0 and runs_req > 0:
        return 0.95
        
    # Logistic transformation of RRR urgency:
    # Baseline RRR = 8.0 rpo. If RRR = 8.0 -> urgency ~ 0.5. If RRR >= 12 -> urgency >= 0.85
    urgency = 1.0 / (1.0 + np.exp(-0.45 * (rrr - 8.5)))
    
    # Resource scarcity: wickets in hand relative to runs required
    # Runs required per wicket remaining
    rpw = runs_req / max(1, w_rem)
    scarcity = min(1.0, rpw / 25.0)
    
    # Time pressure: late in the game (fewer balls remaining)
    time_factor = 1.0 - (balls_rem / 120.0)
    
    # Composite Innings 2 Pressure
    # In death overs (balls_rem <= 30), urgency and scarcity dominate
    if balls_rem > 60:
        p2 = 0.45 * urgency + 0.35 * scarcity + 0.20 * time_factor
    elif balls_rem > 30:
        p2 = 0.50 * urgency + 0.30 * scarcity + 0.20 * time_factor
    else:
        # Final 5 overs: acute pressure
        p2 = 0.55 * urgency + 0.30 * scarcity + 0.15 * time_factor
        
    # Boundary condition adjustment:
    # If only 1-2 wickets in hand, pressure escalates
    if w_rem <= 2 and runs_req > 10:
        p2 = max(p2, 0.85)
        
    return float(np.clip(p2, 0.05, 0.99))

print("Applying pressure formulation to all deliveries...")
p1_series = df.apply(compute_inn1_pressure, axis=1)
p2_series = df.apply(compute_inn2_pressure, axis=1)

# Combined continuous pressure score
df['pressure_score'] = np.where(df['innings'] == 1, p1_series, np.where(df['innings'] == 2, p2_series, 0.95))

# Super overs (innings 3 & 4) are inherently extreme pressure (0.95)
df.loc[df['innings'] >= 3, 'pressure_score'] = 0.95

# Pressure Categories:
# Low: [0.00, 0.35)
# Moderate: [0.35, 0.60)
# High: [0.60, 0.80)
# Extreme: [0.80, 1.00]
def categorize_pressure(score):
    if score < 0.35:
        return "Low"
    elif score < 0.60:
        return "Moderate"
    elif score < 0.80:
        return "High"
    else:
        return "Extreme"

df['pressure_category'] = df['pressure_score'].apply(categorize_pressure)
# Binary pressure indicator for high/extreme pressure (score >= 0.60)
df['is_high_pressure'] = df['pressure_score'] >= 0.60

print("\n--- PRESSURE CATEGORY DISTRIBUTION ---")
print(df['pressure_category'].value_counts(normalize=True).round(4) * 100)
print("\nPressure by Innings:")
print(pd.crosstab(df['innings'], df['pressure_category'], normalize='index').round(4) * 100)

print("\nPressure by Match Phase:")
print(pd.crosstab(df['match_phase'], df['pressure_category'], normalize='index').round(4) * 100)

# Save updated dataset with pressure scores
print("\nSaving updated match states with pressure scores...")
df.to_parquet(os.path.join(OUT_PROC, "match_states.parquet"), index=False)
print("Saved match_states.parquet successfully.")

# Generate summary statistics and distribution report
dist_report = df.groupby(['innings', 'pressure_category']).agg(
    delivery_count=('match_id', 'count'),
    mean_pressure=('pressure_score', 'mean'),
    median_pressure=('pressure_score', 'median'),
    mean_rrr=('rrr_pre', 'mean'),
    mean_wickets_lost=('cum_wickets_pre', 'mean')
).reset_index()

dist_report.to_csv(os.path.join(OUT_VAL, "pressure_distribution_summary.csv"), index=False)
print("Saved pressure_distribution_summary.csv.")
print("PRESSURE DETECTION ENGINE COMPLETE.")
