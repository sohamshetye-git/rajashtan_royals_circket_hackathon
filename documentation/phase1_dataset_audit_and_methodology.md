# Comprehensive Dataset Audit & Project Architecture Proposal
**Project:** SupeRR Selector Season 2 — Rajasthan Royals IPL 2027 Auction Pressure Analytics  
**Date:** November 2026  
**Analytical Architecture:** CRISP (Context-aware Robust Index for Situational Pressure)

---

## 1. Executive Summary & Objective

The objective of Round 1 of the SupeRR Selector competition is to build a statistically rigorous, reproducible, and evidence-based cricket analytics system to identify the **Top 10 Batters** and **Top 10 Bowlers** who perform most reliably under high pressure in T20 cricket (IPL and T20 Internationals from 2022 onwards).

This audit documents the complete dataset structure, data governance rules, data quality findings, cricket rule validations, and the detailed mathematical architecture for the proposed **CRISP** framework.

---

## 2. Dataset Inventory & Governance

All source datasets are located in `C:\rajsathan_royals\data\Data Pack` and are treated as strictly **read-only**. All processed datasets, models, validation outputs, and charts are generated separately in `C:\rajsathan_royals\outputs\`.

### File Summary Table
| File Name | File Size | Row Count | Column Count | Primary Key / Entity | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `competitions.csv` | 7.6 KB | 141 | 4 | `comp_id` | Metadata of T20 & T20I competitions (2022–2026) |
| `teams.csv` | 6.9 KB | 353 | 3 | `(comp_id, team_id)` | Teams participating in each competition |
| `matches.csv` | 123.9 KB | 883 | 22 | `match_id` | Match-level metadata, dates, venues, results |
| `playing_eleven.csv` | 966.3 KB | 28,381 | 9 | `(match_id, player_id)` | Lineups, batting order, captain, WK, impact subs |
| `competition_team_player_mapping.csv` | 463.0 KB | 6,413 | 6 | `(comp_id, team_id, player_id)` | Master player dictionary mapping ID to official name |
| `ball_by_ball.csv` | 41.1 MB | 200,999 | 33 | `(match_id, innings, innings_ball_num)` | Granular ball-by-ball delivery event stream |

---

## 3. Data Integrity & Cricket Domain Validation

### 3.1 Relational Integrity
1. **Match Consistency:**
   - Total matches in `matches.csv`: 883.
   - Matches with ball-by-ball data: 867.
   - 16 matches have 0 deliveries in `ball_by_ball.csv`. Every single one of these 16 matches has `result == 'Match Abandoned'` (e.g. rain washouts without a ball bowled). Zero orphan match IDs exist in `ball_by_ball.csv`.
2. **Player Identification:**
   - 958 unique players (batters + bowlers) appear in `ball_by_ball.csv`.
   - **100% of ball-by-ball players (958/958) exist in `competition_team_player_mapping.csv`**.
   - Player identity is anchored on stable numeric `player_id`. Only 1 player has a slight display name variant (`player_id=4458`: "AHT Donald" vs "Aneurin Donald").

### 3.2 Cricket Mechanics & Scoring Reconstruction
1. **Runs vs. Extras:**
   - `runs`: Represents runs scored off the bat.
   - `extras_type`: Categorical (`wide`, `Overstep`, `other`, `legbyes`, `byes`, `Penalty`, or `NaN`).
   - `extras1_runs`: Primary extra runs for the delivery.
   - `extras_2_runs`: Secondary extra runs (e.g. overthrows or secondary extras on a no-ball).
   - **Total Runs Conceded / Scored on Delivery:**
     $$\text{Delivery Total Runs} = \text{runs} + \text{extras1\_runs} + \text{extras\_2\_runs}$$
2. **Legal Deliveries:**
   - Deliveries where `extras_type` is in `['wide', 'Overstep', 'other']` are illegal deliveries (wides and no-balls).
   - Deliveries where `extras_type` is `NaN`, `'legbyes'`, or `'byes'` are legal deliveries (count towards completed balls).
   - Verification against official scorecards confirmed exact match totals (e.g., Match 13511: WI 104/1 in 17.1 ov beat ENG 103 all out in 19.4 ov).
3. **Bowler-Credited Wickets:**
   - `is_wicket == True` occurred 10,881 times across 200,999 deliveries.
   - **Bowler-credited wickets:** `Bowled` (1,775), `Caught` (7,557), `LBW` (709), `Stump` (214), `Hit Wicket` (17). Total = 10,272 wickets.
   - **Non-bowler dismissals:** `RunOut` (600), `Retire Out` (6), `Obstructing the field` (3). These are credited to team wickets and batter dismissals, but excluded from bowler wickets.
4. **Bowler Conceded Runs:**
   $$\text{Bowler Runs Conceded} = \text{runs} + (\text{extras1\_runs} + \text{extras\_2\_runs} \text{ if } \text{extras\_type} \in [\text{'wide'}, \text{'Overstep'}, \text{'other'}], \text{ else } 0)$$
   Byes and leg-byes are not debited to the bowler's bowling analysis.

### 3.3 Competition Filtering Scope
- The competition scope focuses on **IPL** and **T20 Internationals (T20I)**.
- `competitions.csv` contains:
  - 5 IPL seasons: IPL 2022 (comp 1358), IPL 2023 (comp 1715), IPL 2024 (comp 2193), IPL 2025 (comp 2725), IPL 2026 (comp 3298), totaling 371 matches.
  - 134 T20I bilateral and tournament series, totaling 482 matches with deliveries.
  - 2 regional Asian development competitions (`Mens T20 Emerging Teams Asia Cup 2024` and `Asia Cup Rising Stars 2025`), totaling 30 matches. Per competition guidelines, the primary evaluation focuses on IPL and T20I senior matches.

---

## 4. Methodological Framework: CRISP (Context-aware Robust Index for Situational Pressure)

### 4.1 Match State Reconstruction Engine (Pre-Delivery)
For each delivery $t$, the state $S_t$ is computed using **strictly pre-delivery information**:
- Innings number (1 or 2).
- Legal balls bowled in innings $B_{\text{done}}$, balls remaining $B_{\text{rem}} = 120 - B_{\text{done}}$.
- Current score $R_{\text{curr}}$, wickets lost $W_{\text{lost}}$, wickets in hand $W_{\text{rem}} = 10 - W_{\text{lost}}$.
- Match phase: Powerplay (overs 1–6), Middle (overs 7–15), Death (overs 16–20).
- For Innings 2: Target $T$, runs required $R_{\text{req}} = T - R_{\text{curr}}$, Required Run Rate $\text{RRR} = \frac{R_{\text{req}}}{B_{\text{rem}} / 6}$.

### 4.2 Pressure Quantification Engine
Pressure is multi-dimensional. Rather than an arbitrary over-cutoff, we formulate:

#### A. Chasing Pressure ($P_{\text{chase}} \in [0, 1]$):
Defined as a joint function of:
1. **Urgency (Required Run Rate vs Historical Benchmark):**
   $$U = \frac{\text{RRR} - \text{Baseline RRR}}{\sigma_{\text{RRR}}}$$
2. **Resource Scarcity (Wicket Scarcity & Time Scarcity):**
   $$S_W = \frac{10 - W_{\text{rem}}}{10}, \quad S_B = \frac{120 - B_{\text{rem}}}{120}$$
3. **Closeness to Victory / Defeat:**
   Evaluated using a baseline Win Probability model $WP(S_t)$, where highest tension occurs when $WP \in [0.20, 0.80]$ in late stages or when required runs require high boundary frequencies with few wickets remaining.

#### B. First-Innings Pressure ($P_{\text{defend}} \in [0, 1]$):
Defined by:
1. **Collapse & Resource Depletion:** Loss of wickets early relative to par scoring rate ($W_{\text{lost}} \ge 3$ in Powerplay, or $\ge 5$ before Over 12).
2. **Death-Over Acceleration Urgency:** Overs 16–20 where team must maximize total without getting bowled out.

### 4.3 Expected Performance Baselines (RAE & RPA)
- **Batters:** Runs Above Expected (RAE) and Strike Rate Improvement over context-specific par.
- **Bowlers:** Runs Prevented Above Expected (RPA) and Pressure Wicket Delta over context-specific par.
- Baseline models conditioned on (Innings, Phase, Over, Wickets in Hand).

### 4.4 Statistical Reliability & Sample-Size Governance
To prevent small-sample anomalies:
1. Minimum eligibility thresholds (e.g. minimum 60 pressure balls faced for batters, 60 pressure legal balls bowled for bowlers across $\ge 5$ distinct matches).
2. **Empirical Bayes / Bayesian Shrinkage:** Shrinking observed pressure differentials towards population means inversely proportional to delivery sample variance:
   $$\hat{\theta}_i = w_i \cdot \bar{x}_i + (1 - w_i) \cdot \mu_{\text{pop}}, \quad w_i = \frac{n_i}{n_i + K}$$
3. **Match-Level Consistency:** Measuring standard deviation across matches and percentage of high-leverage matches where positive value was delivered.

---

## 5. Implementation Roadmap

- **Phase 2 & 3:** Build `clean_deliveries` and the pre-delivery `match_state_engine.py`.
- **Phase 4:** Formalize and calibrate the continuous Pressure Metric $P_t \in [0, 1]$ and categorize into [Low, Moderate, High, Extreme].
- **Phase 5 & 6:** Build Batter & Bowler Performance Analytics Pipelines.
- **Phase 7:** Expected-runs / Expected-wickets baseline models.
- **Phase 8 & 9:** Empirical Bayes Shrinkage, Reliability Index, and Top 10 Rankings.
- **Phase 10 & 11:** Predictive validation, bootstrap stability analysis, and format sensitivity.
- **Phase 12–16:** Automated test suites, publication-grade visualization generation, and final submission report.
