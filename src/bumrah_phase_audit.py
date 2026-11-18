"""
INVESTIGATION 2: In-Depth Phase Breakdown and High-Leverage Audit for Jasprit Bumrah vs Top Bowlers
Compares:
1. Jasprit Bumrah (2933)
2. Sunil Narine (781)
3. Matheesha Pathirana (8661)
4. Mustafizur Rahman (4373)
5. Abrar Ahmed (5979)
6. Mohammad Nawaz (2490)
7. Mohit Sharma (2878)
8. Arshdeep Singh (6464)
9. Pat Cummins (1758)
Across:
- Powerplay (Overs 1-6)
- Middle Overs (Overs 7-15)
- Death Overs (Overs 16-20)
- Acute High-Leverage Over (Overs 18-20, Pressure >= 0.70)
Metrics:
- Legal Balls, Overs, Runs Conceded, Economy, Wickets, Strike Rate (Balls/Wkt), Dot %, Boundary Concession %, RPA
"""
import pandas as pd
import numpy as np

PROJ_DIR = r"C:\rajsathan_royals"
OUT_PROC = r"C:\rajsathan_royals\outputs\processed"

df = pd.read_parquet(f"{OUT_PROC}/match_states.parquet")
df_scope = df[df['competition_type'].isin(['IPL', 'T20I'])].copy()

bowlers_to_compare = {
    'Jasprit Bumrah': 2933,
    'Sunil Narine': 781,
    'Matheesha Pathirana': 8661,
    'Mustafizur Rahman': 4373,
    'Abrar Ahmed': 5979,
    'Mohammad Nawaz': 2490,
    'Mohit Sharma': 2878,
    'Arshdeep Singh': 6464,
    'Pat Cummins': 1758
}

print("=" * 80)
print("INVESTIGATION 2: PHASE-SPECIFIC BOWLING BREAKDOWN UNDER HIGH PRESSURE (P >= 0.65)")
print("=" * 80)

phase_rows = []
for name, pid in bowlers_to_compare.items():
    bw_del = df_scope[(df_scope['bowler_id'] == pid) & (df_scope['is_high_pressure']) & (df_scope['is_legal_ball'])]
    
    for phase in ['Powerplay', 'Middle', 'Death', 'All_Pressure']:
        if phase == 'All_Pressure':
            sub = bw_del
        else:
            sub = bw_del[bw_del['match_phase'] == phase]
            
        balls = len(sub)
        runs = sub['bowler_runs_conceded'].sum()
        wkts = sub['is_bowler_wicket'].sum()
        dots = (sub['bowler_runs_conceded'] == 0).sum()
        boundaries = (sub['is_four'] | sub['is_six']).sum()
        rpa = sub['bowler_rpa'].sum()
        
        econ = (runs / (balls / 6.0)) if balls > 0 else np.nan
        sr = (balls / wkts) if wkts > 0 else np.nan
        dot_pct = (dots / balls * 100.0) if balls > 0 else np.nan
        bound_pct = (boundaries / balls * 100.0) if balls > 0 else np.nan
        
        phase_rows.append({
            'Bowler': name,
            'Phase': phase,
            'Balls': balls,
            'Overs': round(balls / 6.0, 1),
            'Runs': runs,
            'Econ': round(econ, 2) if pd.notnull(econ) else 'N/A',
            'Wkts': wkts,
            'SR': round(sr, 1) if pd.notnull(sr) else 'N/A',
            'Dot_Pct': round(dot_pct, 1) if pd.notnull(dot_pct) else 'N/A',
            'Bound_Pct': round(bound_pct, 1) if pd.notnull(bound_pct) else 'N/A',
            'RPA': round(rpa, 1)
        })

phase_df = pd.DataFrame(phase_rows)
# Show death overs comparison
print("\n--- DEATH OVERS (OVERS 16-20) UNDER HIGH PRESSURE ---")
print(phase_df[phase_df['Phase'] == 'Death'].sort_values('RPA', ascending=False).to_string(index=False))

print("\n--- MIDDLE OVERS (OVERS 7-15) UNDER HIGH PRESSURE ---")
print(phase_df[phase_df['Phase'] == 'Middle'].sort_values('RPA', ascending=False).to_string(index=False))

print("\n--- POWERPLAY (OVERS 1-6) UNDER HIGH PRESSURE ---")
print(phase_df[phase_df['Phase'] == 'Powerplay'].sort_values('RPA', ascending=False).to_string(index=False))

# Extreme Death Leverage: Overs 18-20 under P >= 0.70
print("\n" + "=" * 80)
print("EXTREME DEATH LEVERAGE (OVERS 18-20, P >= 0.70)")
print("=" * 80)

extreme_rows = []
for name, pid in bowlers_to_compare.items():
    sub = df_scope[(df_scope['bowler_id'] == pid) & (df_scope['overid'] >= 18) & (df_scope['pressure_score'] >= 0.70) & (df_scope['is_legal_ball'])]
    balls = len(sub)
    runs = sub['bowler_runs_conceded'].sum()
    wkts = sub['is_bowler_wicket'].sum()
    dots = (sub['bowler_runs_conceded'] == 0).sum()
    boundaries = (sub['is_four'] | sub['is_six']).sum()
    rpa = sub['bowler_rpa'].sum()
    
    econ = (runs / (balls / 6.0)) if balls > 0 else np.nan
    sr = (balls / wkts) if wkts > 0 else np.nan
    dot_pct = (dots / balls * 100.0) if balls > 0 else np.nan
    bound_pct = (boundaries / balls * 100.0) if balls > 0 else np.nan
    
    extreme_rows.append({
        'Bowler': name,
        'Balls': balls,
        'Overs': round(balls / 6.0, 1),
        'Runs': runs,
        'Econ': round(econ, 2) if pd.notnull(econ) else 'N/A',
        'Wkts': wkts,
        'SR': round(sr, 1) if pd.notnull(sr) else 'N/A',
        'Dot_Pct': round(dot_pct, 1) if pd.notnull(dot_pct) else 'N/A',
        'Bound_Pct': round(bound_pct, 1) if pd.notnull(bound_pct) else 'N/A',
        'RPA': round(rpa, 1)
    })

ext_df = pd.DataFrame(extreme_rows)
print(ext_df.sort_values('RPA', ascending=False).to_string(index=False))
