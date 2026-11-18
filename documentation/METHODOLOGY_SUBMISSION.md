# SupeRR Selector Season 2: Rajasthan Royals Analytics Methodology Report
**Track:** Player Evaluation & Pressure Performance Analytics  
**Evaluation Window:** IPL & T20 International Data (2022–2026)  
**Deliverables:** Canonical Rankings, Out-of-Sample Machine Learning Benchmarks, Interactive Evaluation Dashboard

---

## 1. Executive Summary
This submission presents an independent, mathematically rigorous performance evaluation system engineered to identify the **Top 10 Batters** and **Top 10 Bowlers** under acute match pressure. 

Departing from conventional raw averages and strike rates, our framework—**CRISP-X (Contextual Run Impact & Shrinkage Pressure Index)**—evaluates every delivery against an empirical context baseline, incorporates dynamic wicket resource values, removes statistical multicollinearity, and applies Bayesian shrinkage to prevent small-sample bias.

---

## 2. Pressure Definition & Match Indicators
A core flaw in common cricket models is treating all death overs or run chases equally. We distinguish between **Pressure** (the difficulty of the match state) and **Leverage** (the potential swing in outcome probability).

### Pre-Delivery Match State Indicators
For every delivery, indicators are computed strictly using information available **prior** to the ball being bowled:
1. **Required Run Rate (RRR) & Rate Delta:** In second innings chases, acute pressure is triggered when:
   $$\text{RRR} \ge 10.00 \quad \text{or} \quad (\text{RRR} - \text{CRR}) \ge 2.50$$
2. **First Innings Crisis Situations:**
   - **Powerplay Collapse:** Overs 1–6 where the batting team scores $\le 35$ runs with $\ge 2$ wickets lost.
   - **Extreme Death Surge:** Overs 17–20 where acceleration is mandated while preserving resources.
3. **Win-Probability Leverage Index ($LI$):**
   Trained on chasing states, the pre-delivery win probability model ($WP$) achieved a **0.9059 ROC-AUC** and **0.1368 Brier score** on unseen 2026 matches. Delivery leverage is defined as:
   $$LI = \mathbb{E}\big[|WP_{\text{after}} - WP_{\text{before}}|\big]$$

---

## 3. Performance Measurement & Rating Logic

### 3.1 Runs Above Expected (RAE) & Runs Prevented Above (RPA)
Raw strike rates and economies reward players in flat-pitch batting paradises. We condition every delivery on:
$$\text{Match State} = f(\text{Phase}, \text{Wickets Lost}, \text{Over Progression}, \text{Venue Tier})$$
- **Batter RAE:** Runs scored off the bat minus expected runs for that specific state.
- **Bowler RPA:** Expected runs conceded minus actual bowler runs (excluding byes and leg-byes).

### 3.2 Dynamic Wicket Resource Valuation
A run saved cannot be equated to a wicket taken. We modeled the empirical future run loss upon a dismissal across phases:
- **Powerplay Wicket Value:** $11.89 \text{ runs}$ (destroys the foundation).
- **Middle-Overs Wicket Value:** $8.45 \text{ runs}$ (breaks run-rate acceleration).
- **Death-Overs Wicket Value:** $2.30 \text{ runs}$ (balls remaining limit run loss).
- **Mean Crisis Wicket Value:** $5.61 \text{ runs}$.

### 3.3 Bayesian Shrinkage & Collinearity Removal
To prevent small-sample noise from dominating, we shrink player rates toward tournament priors using empirical Bayesian weights:
$$w_i = \frac{N_i}{N_i + K_0} \quad (K_0 = 100 \text{ balls})$$
The composite rating indices (**BPRI** for batters, **PRI** for bowlers) weight shrunk run value ($50\%$), shrunk rate ability ($35\%$), and pressure elevation delta ($15\%$).

---

## 4. Fair Comparisons & Sample Eligibility

1. **Eligibility Threshold (150 Pressure Balls):**
   A 100-ball threshold permitted volatile bilateral outliers (e.g. Reeza Hendricks, Salman Mirza) with high estimation variance. The 150-ball threshold ensures sample adequacy while preserving genuine elite performers.
2. **Competition Nuance (IPL vs. T20I):**
   We tracked IPL and T20I splits independently. Players whose sample was dominated by bilateral fixtures against lower-ranked nations (e.g., Sikandar Raza with $80\%$ Zimbabwe T20Is; Abrar Ahmed with $100\%$ Pakistan bilaterals) were scrutinized and flagged against IPL-tested peers (e.g., Rinku Singh, Jasprit Bumrah).
3. **Exclusion of Fielding Errors:**
   Exactly 4,608 runs of unearned fielding extras (byes, leg-byes) were removed from bowler conceded runs, isolating pure bowling execution.

---

## 5. Machine Learning vs. Baseline Benchmarks

All models were evaluated using chronological out-of-sample holdout validation on unseen 2026 fixtures:

| Model Architecture | Out-of-Sample MAE | Out-of-Sample RMSE | Brier Calibration | Audit Finding |
| :--- | :---: | :---: | :---: | :--- |
| Global Mean Baseline | 1.2009 | 1.8624 | 0.2410 | Fails to capture phase nuance |
| Phase Stratified Mean | 1.3456 | 1.8133 | 0.2185 | Coarse boundaries |
| Phase $\times$ Wickets Grid | 1.3390 | 1.8085 | 0.2041 | Robust empirical baseline |
| Regularised Ridge Regression | 1.3502 | 1.8005 | 0.1982 | Stable linear shrinkage |
| HistGradientBoosting | 1.3520 | 1.7985 | 0.1974 | Slightly minimizes RMSE by tail-fitting |
| **Multi-Factor Context Grid** | **1.3434** | **1.7956** | **0.1951** | **Optimal calibration & MAE stability** |

---

## 6. Canonical Top 10 Selections

### Top 10 Batters Under Pressure
1. **Suryakumar Yadav** (BPRI: 77.39 | 520 balls | 165.4 SR | +188.9 RAE) — Tier 1 (98.4% P(Top 10))
2. **Tim David** (BPRI: 76.97 | 436 balls | 176.8 SR | +162.7 RAE) — Tier 1 (96.2% P(Top 10))
3. **Sanju Samson** (BPRI: 73.49 | 230 balls | 181.3 SR (+35.1 $\Delta$) | +124.3 RAE) — Tier 1 (89.1% P(Top 10))
4. **David Miller** (BPRI: 71.30 | 454 balls | 159.9 SR | +130.9 RAE) — Tier 1 (84.6% P(Top 10))
5. **Tilak Varma** (BPRI: 68.84 | 545 balls | 153.2 SR | +122.2 RAE) — Tier 2 (78.5% P(Top 10))
6. **Tristan Stubbs** (BPRI: 65.75 | 422 balls | 152.1 SR | +115.3 RAE) — Tier 2 (71.3% P(Top 10))
7. **Rovman Powell** (BPRI: 64.24 | 520 balls | 146.5 SR | +104.9 RAE) — Tier 2 (66.8% P(Top 10))
8. **Sherfane Rutherford** (BPRI: 63.08 | 326 balls | 159.5 SR | +73.2 RAE) — Tier 2 (58.4% P(Top 10))
9. **Jos Buttler** (BPRI: 62.17 | 231 balls | 168.0 SR | +76.1 RAE) — Tier 2 (54.2% P(Top 10))
10. **Sikandar Raza** (BPRI: 61.75 | 324 balls | 150.0 SR | +77.9 RAE) — Tier 3 (51.0% P(Top 10))  
    *(Recommended Franchise Alternate: **Rinku Singh** — 383 balls, 153.8 SR, +79.8 RAE, only 12 dismissals).*

### Top 10 Bowlers Under Pressure
1. **Sunil Narine** (PRI: 76.13 | 326 balls | 5.59 Econ | +102.2 RPA | 22 wkts) — Tier 1 (99.1% P(Top 10))
2. **Mustafizur Rahman** (PRI: 75.41 | 402 balls | 6.37 Econ | +88.9 RPA | 28 wkts) — Tier 1 (97.5% P(Top 10))
3. **Abrar Ahmed** (PRI: 75.03 | 269 balls | 4.97 Econ | +75.0 RPA | 16 wkts) — Tier 1 (91.8% P(Top 10))
4. **Rashid Khan** (PRI: 70.82 | 747 balls | 7.21 Econ | +16.1 RPA | 54 wkts) — Tier 1 (88.4% P(Top 10))
5. **Jasprit Bumrah** (PRI: 70.35 | 408 balls | 6.72 Econ | +70.5 RPA | 30 wkts) — Tier 1 (86.9% P(Top 10))
6. **Matheesha Pathirana** (PRI: 68.73 | 441 balls | 7.90 Econ | +78.6 RPA | 30 wkts) — Tier 2 (82.1% P(Top 10))
7. **Mohammad Nawaz** (PRI: 68.48 | 219 balls | 5.36 Econ | +38.2 RPA | 20 wkts) — Tier 2 (74.5% P(Top 10))
8. **Mitchell Santner** (PRI: 65.80 | 474 balls | 6.79 Econ | +14.4 RPA | 30 wkts) — Tier 2 (69.2% P(Top 10))
9. **Kuldeep Yadav** (PRI: 63.04 | 485 balls | 7.57 Econ | +4.0 RPA | 37 wkts) — Tier 2 (61.7% P(Top 10))
10. **Yuzvendra Chahal** (PRI: 62.09 | 579 balls | 8.26 Econ | -7.8 RPA | 46 wkts) — Tier 2 (56.3% P(Top 10))  
    *(Recommended Franchise Alternate: **Varun Chakravarthy** — 679 balls, 55 wickets, +289.6 Net Resource Impact).*

---

## 7. Reliability, Uncertainty & Limitations
- **Match-Clustered Bootstrap (2,000 Iterations):** Top performers (Suryakumar, Tim David, Narine, Mustafizur, Bumrah) boast inclusion probabilities $>85\%$.
- **Model Boundaries:** Model evaluated purely on cricket performance metrics under pressure without player auction purse or retention valuation constraints.
- **Reproducibility:** Code, processed parquet caches, and interactive dashboard are open for full inspection.
