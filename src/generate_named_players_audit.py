"""
Named Players Comprehensive Audit & Deep Dive
Outputs: outputs/validation/named_players_audit.csv
"""
import os
import pandas as pd
import numpy as np

BASE_DIR = r"C:\rajsathan_royals"
OUT_VAL = os.path.join(BASE_DIR, "outputs", "validation")
OUT_RANK = os.path.join(BASE_DIR, "outputs", "rankings")
PROCESSED_FILE = os.path.join(BASE_DIR, "outputs", "processed", "match_states.parquet")

df = pd.read_parquet(PROCESSED_FILE)

# Named players mapping
named_batters = [
    ("Virat Kohli", 47),
    ("Hardik Pandya", 3330),
    ("Shubman Gill", 6288),
    ("Yashasvi Jaiswal", 6819),
    ("Rishabh Pant", 4703),
    ("Suryakumar Yadav", 1699),
    ("Sanju Samson", 2258),
    ("David Miller", 1077),
    ("Jos Buttler", 813),
    ("Heinrich Klaasen", 4260)
]

named_bowlers = [
    ("Jasprit Bumrah", 2933),
    ("Sunil Narine", 781),
    ("Rashid Khan", 4722),
    ("Arshdeep Singh", 6464),
    ("Varun Chakravarthy", 6256),
    ("Kuldeep Yadav", 3644),
    ("Mohammed Siraj", 5944),
    ("Patrick Cummins", 1758),
    ("Matheesha Pathirana", 8661),
    ("Mustafizur Rahman", 4373)
]

# Load rankings if available
b_v1 = pd.read_csv(os.path.join(OUT_RANK, "batter_rankings.csv")) if os.path.exists(os.path.join(OUT_RANK, "batter_rankings.csv")) else None
b_v2 = pd.read_csv(os.path.join(OUT_RANK, "batter_rankings_v2.csv")) if os.path.exists(os.path.join(OUT_RANK, "batter_rankings_v2.csv")) else None
bw_v1 = pd.read_csv(os.path.join(OUT_RANK, "bowler_rankings.csv")) if os.path.exists(os.path.join(OUT_RANK, "bowler_rankings.csv")) else None
bw_v2 = pd.read_csv(os.path.join(OUT_RANK, "bowler_rankings_v2.csv")) if os.path.exists(os.path.join(OUT_RANK, "bowler_rankings_v2.csv")) else None

results = []

# High pressure definition
hp_mask = df["pressure_score"] >= 0.65

# Audit Batters
for name, pid in named_batters:
    p_balls_df = df[(df["striker_id"] == pid) & hp_mask]
    all_balls_df = df[df["striker_id"] == pid]
    
    n_p_balls = len(p_balls_df)
    n_p_matches = p_balls_df["match_id"].nunique()
    total_career_balls = len(all_balls_df)
    
    # Calculate performance metrics under pressure
    p_runs = p_balls_df["runs"].sum()
    p_dismissals = (p_balls_df["dismissed_player_id"] == pid).sum()
    p_sr = (p_runs / n_p_balls * 100.0) if n_p_balls > 0 else 0.0
    
    # Normal metrics
    norm_balls_df = df[(df["striker_id"] == pid) & (~hp_mask)]
    n_runs = norm_balls_df["runs"].sum()
    n_sr = (n_runs / len(norm_balls_df) * 100.0) if len(norm_balls_df) > 0 else 0.0
    sr_delta = p_sr - n_sr
    
    # RAE
    p_rae = (p_runs - p_balls_df["exp_runs_final"].sum()) if n_p_balls > 0 else 0.0
    
    # Status
    eligible = n_p_balls >= 100
    status = "QUALIFIED" if eligible else "EXCLUDED (Sample < 100 balls)"
    
    # Rank lookup
    v1_rank = "N/A"
    v2_rank = "N/A"
    if eligible and b_v1 is not None:
        row1 = b_v1[b_v1["striker_id"] == pid]
        if len(row1) > 0:
            v1_rank = int(row1["Rank"].values[0])
    if eligible and b_v2 is not None:
        row2 = b_v2[b_v2["striker_id"] == pid]
        if len(row2) > 0:
            v2_rank = int(row2["Rank_v2"].values[0])
            
    reason = ""
    if not eligible:
        reason = f"Only {n_p_balls} pressure balls faced ({n_p_matches} matches) out of {total_career_balls} total career balls ({round(n_p_balls/total_career_balls*100,1)}% under crisis)."
    else:
        if v2_rank != "N/A" and v2_rank <= 10:
            reason = f"Top 10 Selection (Rank #{v2_rank}). High crisis reliability, SR {round(p_sr, 1)} (+{round(sr_delta, 1)} delta), +{round(p_rae, 1)} RAE."
        else:
            reason = f"Met sample cutoff ({n_p_balls} balls), but ranked #{v2_rank}. Performance index lagged top finishers (SR {round(p_sr, 1)}, RAE +{round(p_rae, 1)})."

    results.append({
        "Player_Name": name,
        "Player_ID": pid,
        "Player_Type": "Batter",
        "Total_Career_Balls": total_career_balls,
        "Pressure_Balls": n_p_balls,
        "Pressure_Matches": n_p_matches,
        "Pressure_SR": round(p_sr, 2),
        "Normal_SR": round(n_sr, 2),
        "SR_Delta": round(sr_delta, 2),
        "Pressure_RAE_or_RPA": round(p_rae, 2),
        "Eligibility_Status": status,
        "CRISP_v1_Rank": str(v1_rank),
        "CRISP_v2_Rank": str(v2_rank),
        "Audit_Verdict": reason
    })

# Audit Bowlers
for name, pid in named_bowlers:
    p_del_df = df[(df["bowler_id"] == pid) & hp_mask]
    all_del_df = df[df["bowler_id"] == pid]
    
    n_p_legal = p_del_df["is_legal_ball"].sum()
    n_p_del = len(p_del_df)
    n_p_matches = p_del_df["match_id"].nunique()
    total_career_del = len(all_del_df)
    
    # Conceded runs
    p_runs_conceded = p_del_df["bowler_runs_conceded"].sum()
    p_wkts = p_del_df["is_bowler_wicket"].sum()
    p_econ = (p_runs_conceded / (n_p_legal / 6.0)) if n_p_legal > 0 else 0.0
    
    # Normal metrics
    norm_del_df = df[(df["bowler_id"] == pid) & (~hp_mask)]
    n_legal = norm_del_df["is_legal_ball"].sum()
    n_runs = norm_del_df["bowler_runs_conceded"].sum()
    n_econ = (n_runs / (n_legal / 6.0)) if n_legal > 0 else 0.0
    econ_delta = n_econ - p_econ  # positive means better (lower econ in pressure)
    
    # RPA
    p_rpa = (p_del_df["exp_runs_final"].sum() - p_runs_conceded) if n_p_legal > 0 else 0.0
    
    eligible = n_p_legal >= 100
    status = "QUALIFIED" if eligible else "EXCLUDED (Sample < 100 legal balls)"
    
    v1_rank = "N/A"
    v2_rank = "N/A"
    if eligible and bw_v1 is not None:
        row1 = bw_v1[bw_v1["bowler_id"] == pid]
        if len(row1) > 0:
            v1_rank = int(row1["Rank"].values[0])
    if eligible and bw_v2 is not None:
        row2 = bw_v2[bw_v2["bowler_id"] == pid]
        if len(row2) > 0:
            v2_rank = int(row2["Rank_v2"].values[0])
            
    reason = ""
    if not eligible:
        reason = f"Only {n_p_legal} pressure legal balls bowled ({n_p_matches} matches) out of {total_career_del} total deliveries."
    else:
        if v2_rank != "N/A" and v2_rank <= 10:
            reason = f"Top 10 Selection (Rank #{v2_rank}). Canonical pressure econ {round(p_econ, 2)}, {p_wkts} wickets, +{round(p_rpa, 1)} runs prevented."
        else:
            reason = f"Met sample cutoff ({n_p_legal} balls), but ranked #{v2_rank}. Pressure econ {round(p_econ, 2)}, econ delta {round(econ_delta, 2)}."

    results.append({
        "Player_Name": name,
        "Player_ID": pid,
        "Player_Type": "Bowler",
        "Total_Career_Balls": total_career_del,
        "Pressure_Balls": n_p_legal,
        "Pressure_Matches": n_p_matches,
        "Pressure_SR": round(p_econ, 2),  # Economy stored here for bowlers
        "Normal_SR": round(n_econ, 2),
        "SR_Delta": round(econ_delta, 2),
        "Pressure_RAE_or_RPA": round(p_rpa, 2),
        "Eligibility_Status": status,
        "CRISP_v1_Rank": str(v1_rank),
        "CRISP_v2_Rank": str(v2_rank),
        "Audit_Verdict": reason
    })

audit_df = pd.DataFrame(results)
audit_path = os.path.join(OUT_VAL, "named_players_audit.csv")
audit_df.to_csv(audit_path, index=False)
print(f"Successfully generated {audit_path}")
print(audit_df[["Player_Name", "Player_Type", "Pressure_Balls", "Eligibility_Status", "CRISP_v2_Rank"]].to_string())
