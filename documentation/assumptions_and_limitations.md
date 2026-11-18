# Assumptions, Boundary Conditions, and Methodological Limitations
**Project:** Rajasthan Royals IPL 2027 Auction Analytics  
**Framework:** CRISP (Context-aware Robust Index for Situational Pressure)  
**Date:** November 2026

This document records all explicit assumptions, boundary condition choices, and known limitations of the CRISP framework.

---

## 1. Cricket Scoring & Match State Assumptions

1. **Delivery Legality Definition:**
   - Deliveries where `extras_type` is `'wide'`, `'Overstep'`, or `'other'` are treated as illegal balls and do not count towards the 120 completed legal deliveries in a T20 innings.
   - Deliveries with byes or leg-byes on legal deliveries are treated as legal deliveries.
2. **Bowler-Credited Wickets:**
   - Only `Bowled`, `Caught`, `LBW`, `Stump`, and `Hit Wicket` are credited as bowler wickets.
   - `RunOut`, `Retire Out`, and `Obstructing the field` dismissals terminate the batter's innings but are strictly excluded from bowler wicket credit.
3. **Bowler Conceded Runs:**
   - Wides, oversteps, and other no-balls are debited to the bowler's runs conceded.
   - Byes and leg-byes are debited to team total runs but are excluded from the bowler's runs conceded, per standard cricket scoring laws.
4. **Target Scores in Rain-Affected Chases:**
   - In Innings 2, if an official `revised_target` is provided in `matches.csv` (DLS revised), that value is used as the target.
   - Otherwise, target score is derived as $\text{Innings 1 Total Runs} + 1$.

---

## 2. Pressure Modelling Assumptions

1. **Continuous Situational Pressure ($P_t$):**
   - Pressure is strictly constructed from pre-delivery match variables ($S_t$) with zero future leakage.
   - For Innings 2 (Chasing), par Required Run Rate (RRR) is benchmarked at 8.5 runs per over based on historical IPL/T20I averages from 2022 to 2026.
   - For Innings 1 (Setting), pressure combines collapse depth (wickets lost relative to over) and death-over maximization urgency.
2. **Pressure Tier Thresholds:**
   - Low Pressure: $P_t < 0.40$
   - Moderate Pressure: $0.40 \le P_t < 0.65$
   - High Pressure: $0.65 \le P_t < 0.80$
   - Extreme Pressure: $P_t \ge 0.80$
   - High-pressure analysis evaluates deliveries with $P_t \ge 0.65$.

---

## 3. Reliability & Sample-Size Assumptions

1. **Eligibility Thresholds:**
   - Batters: Minimum 100 pressure balls faced and at least 10 pressure matches.
   - Bowlers: Minimum 100 pressure legal balls bowled (16.4 overs) and at least 10 pressure matches.
   - Thresholds prevent short-run variance and ensure players evaluated possess multi-match reliability.
2. **Empirical Bayes Shrinkage:**
   - Prior shrinkage parameter $K = 60$ deliveries for both batters and bowlers.
   - Shrinks strike rate, economy rate, RAE, and RPA towards population baselines inversely proportional to observed sample size.

---

## 4. Limitations & Scope for Future Enhancement

1. **Lack of Ball-Tracking Trajectory Data:**
   - The competition dataset provides ball release speed and broad style categories, but does not provide Hawk-Eye pitch coordinates, swing/seam deviation, or wagon-wheel coordinates.
2. **Match Importance Weighting:**
   - While knockout matches are flagged via `knock_out == 1`, all deliveries in the primary scope receive equal analytical weight to avoid over-penalizing players from non-qualifying teams.
3. **Head-to-Head Batter-Bowler Priors:**
   - The current baseline conditions on match state $(\text{Innings}, \text{Over}, W_{\text{lost}}, \text{Competition})$. Future versions could incorporate batter-bowler match-up ratings using hierarchical Bayes.
