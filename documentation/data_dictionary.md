# Data Dictionary — SupeRR Selector Season 2
**Project:** Rajasthan Royals IPL 2027 Auction Pressure Analytics  
**Date:** November 2026

This document provides a precise specification of all tables, fields, types, descriptions, domain rules, and roles within the analytical system.

---

## 1. `competitions.csv`
- `comp_id` (Integer, Primary Key): Unique competition identifier.
- `comp_name` (String): Official competition title (e.g., 'IPL 2024', 'India in England T20I Series 2022').
- `match_format` (Categorical: `T20` | `T20I`): Match format classification.
- `season` (String): Competition season (e.g., '2022', '2023', '2024', '2025', '2026', '2022/23', etc.).

---

## 2. `teams.csv`
- `comp_id` (Integer, Foreign Key -> `competitions.comp_id`): Competition identifier.
- `team_id` (Integer, Foreign Key): Unique team identifier (38 distinct teams across international and franchise cricket).
- `team_name` (String): Official team name.

---

## 3. `matches.csv`
- `match_id` (Integer, Primary Key): Unique match identifier.
- `comp_id` (Integer, Foreign Key -> `competitions.comp_id`): Competition identifier.
- `match_number` (Integer): Match number within the tournament / series.
- `match_date` (Date, YYYY-MM-DD): Date of the match.
- `stage` (Categorical): Tournament stage (League, Qualifier, Eliminator, Final, Semi Final, etc.).
- `venue_id` (Integer): Ground identifier.
- `venue_country` (String): Country where match was played.
- `home_team_id` / `away_team_id` (Integer, Foreign Key -> `teams.team_id`): Competing team IDs.
- `home_team` / `away_team` (String): Team names.
- `home_team_captain_id` / `away_team_captain_id` (Float/Integer): Captain player IDs.
- `toss_win_team_id` (Float/Integer): Team that won the toss.
- `toss_opted` (Categorical: `Fielding` | `Batting`): Toss decision.
- `man_of_the_match` (Integer): Player ID awarded Player of the Match.
- `first_inn_revised_overs` / `second_inn_revised_overs` (Float): Revised innings lengths (DLS/rain rules).
- `revised_target` (Float): DLS adjusted target score for Innings 2.
- `knock_out` (Binary: 0 | 1): 1 if match is a playoff/knockout game; 0 if league/group stage.
- `win_team_id` (Float/Integer): Winning team ID (NaN for ties/abandonments).
- `result` (String): Official text result (e.g., 'Rajasthan Royals Won by 7 Wickets', 'Match Abandoned').

---

## 4. `playing_eleven.csv`
- `match_id` (Integer, Foreign Key -> `matches.match_id`): Match ID.
- `team_id` (Integer, Foreign Key -> `teams.team_id`): Team ID.
- `player_id` (Integer, Foreign Key -> Player Master): Player ID.
- `batting_order` (Float): Scheduled or actual batting order position.
- `is_played` (Boolean): True if player took part on the field.
- `is_captain` (Boolean): True if player captained the team.
- `is_wk` (Boolean): True if designated wicketkeeper.
- `is_impact` (Binary: 0 | 1): True if player came on as an Impact Player.
- `is_impact_off` (Binary: 0 | 1): True if player was substituted off as Impact Player.

---

## 5. `competition_team_player_mapping.csv`
- `comp_id` (Integer): Competition ID.
- `comp_name` (String): Competition title.
- `team_id` (Integer): Team ID.
- `team_name` (String): Team name.
- `player_id` (Integer, Primary Key for player identity): Master player identifier.
- `player_name` (String): Master player name.

---

## 6. `ball_by_ball.csv`
- `match_id` (Integer, Foreign Key -> `matches.match_id`): Match identifier.
- `innings` (Integer: 1, 2, 3, 4): Innings number (1 = 1st inn, 2 = 2nd inn, 3/4 = Super Overs).
- `overid` (Integer: 1–20): Over number (1-indexed: 1 = 1st over, 20 = 20th over).
- `over_ball_num` (Integer: 1–13): Sequential delivery counter within the over (including illegal balls).
- `innings_ball_num` (Integer: 1–136): Sequential delivery counter within the innings.
- `batting_team_id` / `bowling_team_id` (Integer): Team IDs.
- `striker_id` / `striker_name` (Integer / String): Facing batter ID and name.
- `non_striker_id` / `non_striker_name` (Integer / String): Non-striker ID and name.
- `bowler_id` / `bowler_name` (Integer / String): Bowler ID and name.
- `batting_type` / `bowling_type` (Categorical): Batting handedness and bowling style.
- `batting_order` (Integer): Batting position of striker.
- `runs` (Integer: 0, 1, 2, 3, 4, 5, 6): Runs scored off the bat.
- `is_four` / `is_six` (Boolean): Boundary flags off the bat.
- `is_wicket` (Boolean): True if dismissal occurred on delivery.
- `dismissal_type_id` / `dismissal_type` (Float / String): Dismissal category:
  - Bowler wickets: `Bowled`, `Caught`, `LBW`, `Stump`, `Hit Wicket`.
  - Non-bowler dismissals: `RunOut`, `Retire Out`, `Obstructing the field`.
- `dismissed_player_id` (Float): Player ID of dismissed batter.
- `extras_type` (String: `wide`, `Overstep`, `other`, `legbyes`, `byes`, `Penalty`, or `NaN`): Extras category.
  - Illegal deliveries: `wide`, `Overstep`, `other`.
  - Legal deliveries with extras: `legbyes`, `byes`.
- `extras1_runs` (Integer): Primary extras credited.
- `extras_2_runs` (Integer): Secondary extras credited.
- `pace_or_spin` (Categorical: `Pace`, `Spin`): Bowling discipline.
- `bowl_speed` (Float): Ball release speed in km/h.
- `stroke` / `delivery_style` / `over_or_around` / `on_or_off` (String): Tracking and biomechanical trajectory tags.
- `delivery_ist_time` (String): Delivery timestamp.
