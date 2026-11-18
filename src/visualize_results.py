"""
PHASE 15: Visualization Engine
Generates publication-quality charts:
1. pressure_distribution.png: Pressure score density and category breakdowns across innings and phases.
2. batter_analysis.png: Pressure SR vs Normal Baseline SR, RAE per ball, and Top 10 rankings.
3. bowler_analysis.png: Pressure Economy vs Normal Economy, RPA per ball, and Top 10 rankings.
4. reliability_analysis.png: Sample size (balls faced/bowled) vs Empirical Bayes shrinkage weight and uncertainty.
5. ranking_stability.png: Bootstrap rank distributions and confidence tiers for Top 10 Batters and Bowlers.
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Style setup
sns.set_theme(style="whitegrid", font="sans-serif")
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 14

PROJ_DIR = r"C:\rajsathan_royals"
OUT_PROC = os.path.join(PROJ_DIR, "outputs", "processed")
OUT_RANK = os.path.join(PROJ_DIR, "outputs", "rankings")
OUT_VAL = os.path.join(PROJ_DIR, "outputs", "validation")
OUT_CHARTS = os.path.join(PROJ_DIR, "outputs", "charts")

os.makedirs(OUT_CHARTS, exist_ok=True)

df = pd.read_parquet(os.path.join(OUT_PROC, "match_states.parquet"))
top10_bat = pd.read_csv(os.path.join(OUT_RANK, "batter_top10.csv"))
top10_bowl = pd.read_csv(os.path.join(OUT_RANK, "bowler_top10.csv"))
bat_stab = pd.read_csv(os.path.join(OUT_VAL, "batter_stability.csv"))
bowl_stab = pd.read_csv(os.path.join(OUT_VAL, "bowler_stability.csv"))

# 1. PRESSURE DISTRIBUTION CHART
print("Generating pressure_distribution.png...")
fig, axs = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1A: Density by Innings
sns.kdeplot(data=df[df['innings'] == 1], x='pressure_score', label='1st Innings (Setting)', color='#1f77b4', fill=True, alpha=0.3, ax=axs[0])
sns.kdeplot(data=df[df['innings'] == 2], x='pressure_score', label='2nd Innings (Chasing)', color='#d62728', fill=True, alpha=0.3, ax=axs[0])
axs[0].axvline(0.40, color='gray', linestyle='--', alpha=0.7, label='Moderate Threshold (0.40)')
axs[0].axvline(0.65, color='orange', linestyle='--', alpha=0.7, label='High Pressure Threshold (0.65)')
axs[0].axvline(0.80, color='darkred', linestyle='--', alpha=0.7, label='Extreme Pressure Threshold (0.80)')
axs[0].set_title('Continuous Situational Pressure Distribution by Innings')
axs[0].set_xlabel('Situational Pressure Score ($P_t$)')
axs[0].set_ylabel('Density')
axs[0].legend(loc='upper right')

# Plot 1B: Pressure by Phase (Stacked Bar)
phase_counts = pd.crosstab(df['match_phase'], df['pressure_category'], normalize='index')[['Low', 'Moderate', 'High', 'Extreme']] * 100.0
phase_counts.plot(kind='bar', stacked=True, color=['#2ca02c', '#ff7f0e', '#d62728', '#7b1113'], ax=axs[1])
axs[1].set_title('Pressure Tier Breakdown Across Match Phases')
axs[1].set_xlabel('Match Phase')
axs[1].set_ylabel('Percentage of Deliveries (%)')
axs[1].legend(title='Pressure Tier', loc='upper right')
axs[1].set_xticklabels(axs[1].get_xticklabels(), rotation=0)

plt.tight_layout()
plt.savefig(os.path.join(OUT_CHARTS, "pressure_distribution.png"), dpi=300)
plt.close()

# 2. BATTER PERFORMANCE ANALYSIS CHART
print("Generating batter_analysis.png...")
fig, axs = plt.subplots(1, 2, figsize=(15, 6))

# Plot 2A: Pressure SR vs Normal SR for Qualified Batters
b_qual = pd.read_parquet(os.path.join(OUT_PROC, "batter_aggregated_raw.parquet"))
b_qual = b_qual[b_qual['p_balls'] >= 100]

sns.scatterplot(data=b_qual, x='n_sr', y='p_sr', size='p_balls', sizes=(40, 250), hue='p_rae', palette='viridis', alpha=0.7, ax=axs[0])
axs[0].plot([100, 200], [100, 200], 'r--', alpha=0.7, label='Parity Line ($p\_sr = n\_sr$)')
# Highlight Top 10 Batters
for _, row in top10_bat.iterrows():
    axs[0].scatter(row['n_sr'], row['p_sr'], color='red', s=120, edgecolors='black', linewidth=1.5)
    axs[0].annotate(f"{row['player_name']} (#{row['Rank']})", (row['n_sr'] + 1, row['p_sr'] + 1), fontsize=8, weight='bold')

axs[0].set_title('Batters: Pressure Strike Rate vs. Normal Baseline')
axs[0].set_xlabel('Normal Situation Strike Rate ($n\_sr$)')
axs[0].set_ylabel('High-Pressure Strike Rate ($p\_sr$)')
axs[0].legend(loc='lower right', bbox_to_anchor=(1, 0))

# Plot 2B: Top 10 Batters BPRI Index Breakdown
top10_bat_sorted = top10_bat.sort_values('BPRI', ascending=True)
colors = ['#1f77b4' if r > 3 else '#d62728' for r in top10_bat_sorted['Rank']]
bars = axs[1].barh(top10_bat_sorted['player_name'], top10_bat_sorted['BPRI'], color=colors)
axs[1].set_xlim(55, 80)
axs[1].set_title('Official Top 10 Batters Under Pressure (BPRI)')
axs[1].set_xlabel('Batter Pressure Reliability Index (BPRI, 0-100)')
for bar in bars:
    w = bar.get_width()
    axs[1].text(w + 0.3, bar.get_y() + bar.get_height()/2, f'{w:.2f}', va='center', ha='left', fontsize=9, weight='bold')

plt.tight_layout()
plt.savefig(os.path.join(OUT_CHARTS, "batter_analysis.png"), dpi=300)
plt.close()

# 3. BOWLER PERFORMANCE ANALYSIS CHART
print("Generating bowler_analysis.png...")
fig, axs = plt.subplots(1, 2, figsize=(15, 6))

# Plot 3A: Pressure Economy vs Normal Economy
bw_qual = pd.read_parquet(os.path.join(OUT_PROC, "bowler_aggregated_raw.parquet"))
bw_qual = bw_qual[bw_qual['p_legal_balls'] >= 100]

sns.scatterplot(data=bw_qual, x='n_econ', y='p_econ', size='p_legal_balls', sizes=(40, 250), hue='p_rpa', palette='magma', alpha=0.7, ax=axs[0])
axs[0].plot([5, 12], [5, 12], 'r--', alpha=0.7, label='Parity Line ($p\_econ = n\_econ$)')
# Highlight Top 10 Bowlers
for _, row in top10_bowl.iterrows():
    axs[0].scatter(row['n_econ'], row['p_econ'], color='cyan', s=120, edgecolors='black', linewidth=1.5)
    axs[0].annotate(f"{row['player_name']} (#{row['Rank']})", (row['n_econ'] + 0.1, row['p_econ'] + 0.1), fontsize=8, weight='bold')

axs[0].set_title('Bowlers: Pressure Economy vs. Normal Baseline')
axs[0].set_xlabel('Normal Situation Economy ($n\_econ$)')
axs[0].set_ylabel('High-Pressure Economy ($p\_econ$, Lower is Better)')
axs[0].legend(loc='upper left')

# Plot 3B: Top 10 Bowlers Bowler_PRI Index
top10_bowl_sorted = top10_bowl.sort_values('Bowler_PRI', ascending=True)
colors_bw = ['#2ca02c' if r > 3 else '#0b559f' for r in top10_bowl_sorted['Rank']]
bars_bw = axs[1].barh(top10_bowl_sorted['player_name'], top10_bowl_sorted['Bowler_PRI'], color=colors_bw)
axs[1].set_xlim(55, 88)
axs[1].set_title('Official Top 10 Bowlers Under Pressure (Bowler_PRI)')
axs[1].set_xlabel('Bowler Pressure Reliability Index (Bowler_PRI, 0-100)')
for bar in bars_bw:
    w = bar.get_width()
    axs[1].text(w + 0.3, bar.get_y() + bar.get_height()/2, f'{w:.2f}', va='center', ha='left', fontsize=9, weight='bold')

plt.tight_layout()
plt.savefig(os.path.join(OUT_CHARTS, "bowler_analysis.png"), dpi=300)
plt.close()

# 4. RELIABILITY & SHRINKAGE CHART
print("Generating reliability_analysis.png...")
fig, axs = plt.subplots(1, 2, figsize=(14, 5))

balls_range = np.linspace(10, 500, 100)
w_bat = balls_range / (balls_range + 60.0)
w_bowl = balls_range / (balls_range + 60.0)

axs[0].plot(balls_range, w_bat, color='#1f77b4', lw=2.5, label='Empirical Bayes Weight ($w_i = \\frac{n_i}{n_i + 60}$)')
axs[0].axvline(100, color='red', linestyle='--', alpha=0.8, label='Minimum Qualification Cutoff (100 balls)')
axs[0].axhline(0.625, color='gray', linestyle=':', label='Weight at 100 balls ($w = 0.625$)')
axs[0].set_title('Empirical Bayes Shrinkage Curve (Credibility vs Sample Size)')
axs[0].set_xlabel('Pressure Deliveries Sample Size ($n_i$)')
axs[0].set_ylabel('Weight on Individual Sample ($w_i$)')
axs[0].legend(loc='lower right')

# Batter Sample size vs Variance
sns.scatterplot(data=b_qual, x='p_balls', y='p_rae_match_std', size='p_matches', hue='BPRI', palette='coolwarm', ax=axs[1])
axs[1].set_title('Sample Size vs Match-Level Standard Deviation (Batters)')
axs[1].set_xlabel('Pressure Balls Faced')
axs[1].set_ylabel('Match RAE Standard Deviation ($\\sigma_{match}$)')

plt.tight_layout()
plt.savefig(os.path.join(OUT_CHARTS, "reliability_analysis.png"), dpi=300)
plt.close()

# 5. RANKING STABILITY CHART
print("Generating ranking_stability.png...")
fig, axs = plt.subplots(1, 2, figsize=(14, 6))

# Batters stability
bat_stab_sorted = bat_stab.sort_values('Rank', ascending=False)
axs[0].barh(bat_stab_sorted['player_name'], bat_stab_sorted['top15_appearance_pct'], color='#3470a3')
axs[0].axvline(75, color='green', linestyle='--', label='High Confidence Cutoff (75%)')
axs[0].set_xlim(0, 105)
axs[0].set_title('Top 10 Batters: Bootstrap Top 15 Appearance Rate (%)')
axs[0].set_xlabel('Appearance Rate in 200 Resamples (%)')
axs[0].legend(loc='lower right')

# Bowlers stability
bowl_stab_sorted = bowl_stab.sort_values('Rank', ascending=False)
axs[1].barh(bowl_stab_sorted['player_name'], bowl_stab_sorted['top15_appearance_pct'], color='#2ca02c')
axs[1].axvline(75, color='green', linestyle='--', label='High Confidence Cutoff (75%)')
axs[1].set_xlim(0, 105)
axs[1].set_title('Top 10 Bowlers: Bootstrap Top 15 Appearance Rate (%)')
axs[1].set_xlabel('Appearance Rate in 200 Resamples (%)')
axs[1].legend(loc='lower right')

plt.tight_layout()
plt.savefig(os.path.join(OUT_CHARTS, "ranking_stability.png"), dpi=300)
plt.close()

print("ALL PUBLICATION VISUALIZATIONS GENERATED SUCCESSFULLY.")
