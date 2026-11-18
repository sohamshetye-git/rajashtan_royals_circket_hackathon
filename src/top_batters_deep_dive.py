"""
INVESTIGATION 3: In-Depth Breakdown for Virat Kohli, Hardik Pandya, Shubman Gill, Yashasvi Jaiswal (Fixed)
"""
import pandas as pd
import numpy as np

PROJ_DIR = r"C:\rajsathan_royals"
OUT_PROC = r"C:\rajsathan_royals\outputs\processed"

df = pd.read_parquet(f"{OUT_PROC}/match_states.parquet")
df_scope = df[df['competition_type'].isin(['IPL', 'T20I'])].copy()

focus_batters = {
    'Virat Kohli': 47,
    'Hardik Pandya': 3330,
    'Shubman Gill': 6288,
    'Yashasvi Jaiswal': 6819
}

print("=" * 80)
print("INVESTIGATION 3: DEEP CONTEXT AUDIT FOR VIRAT, HARDIK, GILL & JAISWAL")
print("=" * 80)

for name, pid in focus_batters.items():
    b_del = df_scope[df_scope['striker_id'] == pid]
    p_del = b_del[b_del['is_high_pressure']]
    n_del = b_del[~b_del['is_high_pressure']]
    
    p_sr = (p_del['runs'].sum() / len(p_del) * 100.0) if len(p_del) > 0 else 0.0
    n_sr = (n_del['runs'].sum() / len(n_del) * 100.0) if len(n_del) > 0 else 0.0
    
    print(f"\n=======================================================")
    print(f"BATTER: {name} (ID {pid})")
    print(f"=======================================================")
    print(f"Total Matches: {b_del['match_id'].nunique()}, Total Balls: {len(b_del)}, Total Runs: {b_del['runs'].sum()}, Overall SR: {b_del['runs'].sum()/len(b_del)*100:.1f}")
    print(f"Pressure Deliveries (P >= 0.65): {len(p_del)} balls ({len(p_del)/len(b_del)*100:.1f}% of his career balls)")
    print(f"Pressure Matches: {p_del['match_id'].nunique()}, Runs: {p_del['runs'].sum()}, Pressure SR: {p_sr:.1f}")
    print(f"Normal Deliveries: {len(n_del)} balls, Normal Runs: {n_del['runs'].sum()}, Normal SR: {n_sr:.1f}")
    print(f"Pressure Dismissals: {p_del['is_wicket'].sum()}, Balls per Dismissal: {len(p_del)/max(1, p_del['is_wicket'].sum()):.1f}")
    print(f"Pressure RAE: {p_del['batter_rae'].sum():.1f} ({p_del['batter_rae'].sum()/max(1, len(p_del)):+.2f} per ball)")
    
    # Innings breakdown
    print("\n--- By Innings (Pressure Only) ---")
    if len(p_del) > 0:
        inn_grp = p_del.groupby('innings').agg(
            balls=('runs', 'count'),
            runs=('runs', 'sum'),
            wkts=('is_wicket', 'sum'),
            rae=('batter_rae', 'sum')
        )
        inn_grp['sr'] = inn_grp['runs'] / inn_grp['balls'] * 100.0
        print(inn_grp.to_string())
    
    # Phase breakdown
    print("\n--- By Match Phase (Pressure Only) ---")
    if len(p_del) > 0:
        ph_grp = p_del.groupby('match_phase').agg(
            balls=('runs', 'count'),
            runs=('runs', 'sum'),
            wkts=('is_wicket', 'sum'),
            rae=('batter_rae', 'sum')
        )
        ph_grp['sr'] = ph_grp['runs'] / ph_grp['balls'] * 100.0
        print(ph_grp.to_string())
    
    # Situational context
    rebuild = p_del[(p_del['overid'] <= 10) & (p_del['cum_wickets_pre'] >= 3)]
    accel = p_del[(p_del['innings'] == 2) & (p_del['rrr_pre'] >= 10.0)]
    finish = p_del[p_del['overid'] >= 16]
    
    reb_sr = rebuild['runs'].sum() / max(1, len(rebuild)) * 100.0 if len(rebuild) > 0 else 0.0
    acc_sr = accel['runs'].sum() / max(1, len(accel)) * 100.0 if len(accel) > 0 else 0.0
    fin_sr = finish['runs'].sum() / max(1, len(finish)) * 100.0 if len(finish) > 0 else 0.0
    
    print("\n--- Situational Execution ---")
    print(f"Rebuilding (Overs 1-10, Wkts >= 3): {len(rebuild)} balls, {rebuild['runs'].sum()} runs (SR: {reb_sr:.1f}), Wkts: {rebuild['is_wicket'].sum()}, RAE: {rebuild['batter_rae'].sum():.1f}")
    print(f"Acute Chase Acceleration (RRR >= 10): {len(accel)} balls, {accel['runs'].sum()} runs (SR: {acc_sr:.1f}), Wkts: {accel['is_wicket'].sum()}, RAE: {accel['batter_rae'].sum():.1f}")
    print(f"Death Finishing (Overs 16-20): {len(finish)} balls, {finish['runs'].sum()} runs (SR: {fin_sr:.1f}), Wkts: {finish['is_wicket'].sum()}, RAE: {finish['batter_rae'].sum():.1f}")
