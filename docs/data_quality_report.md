# Data-quality report

This file is written by `notebooks/04_validate_observations.ipynb` every time the pipeline runs.

## Source files

- Match files in the archive: 961 (unreadable: 0)
- Matches kept: 287; left out: 674

Why files were left out (one reason per file):

| reason | files |
|---|---|
| before_window | 674 |

## Counts per format

| format | matches | matches_with_england_innings | england_innings | observations | partnership_runs | wicket_records | deliveries |
|---|---|---|---|---|---|---|---|
| Test | 81 | 81 | 151 | 1357 | 43080 | 1328 | 66829 |
| ODI | 88 | 85 | 85 | 708 | 22929 | 662 | 22766 |
| T20I | 118 | 114 | 114 | 763 | 18974 | 675 | 12878 |

Matches kept in which England did not bat (washed out or finished before England's innings): 7 (1185311, 1239536, 1276912, 1415706, 1433377, 1491719, 1496574). They have no England innings, so they add no partnerships.

## Structural checks

| check | passed | detail |
|---|---|---|
| innings_partnership_runs_equal_delivery_runs | True | 350 innings, 84983 runs |
| distinct_players_in_pair | True |  |
| canonical_pair_order | True |  |
| all_player_ids_resolved | True |  |
| runs_non_negative_integers | True |  |
| runs_equal_batter_plus_extras | True |  |
| every_observation_has_a_delivery | True |  |
| sequence_numbers_contiguous | True |  |
| innings_end_only_on_last_observation | True |  |
| observation_count_matches_innings_table | True | 2828 partnerships |
| only_england_batting | True |  |
| formats_canonical | True |  |
| dates_inside_window | True |  |

## Scorecard checks

Each innings total is added up straight from the balls in the match file, without the partnership code, and compared with the target and the winning margin in runs that Cricsheet stores in the same file. Matches decided by a rain rule are not part of this check, because their target comes from the rain rule.

| format | check | checked | passed |
|---|---|---|---|
| ODI | margin_runs | 38 | 38 |
| ODI | target | 78 | 78 |
| T20I | margin_runs | 54 | 54 |
| T20I | target | 105 | 105 |
| Test | margin_runs | 43 | 43 |

Scorecard checks that failed: 0



## Extraction warnings

None. Every change of pair is explained by a wicket, a recorded batter replacement or the end of the innings.

## Partnerships that ended in another way

Partnerships that ended with a retirement or a recorded replacement instead of a dismissal.

| match_id | format | match_date | innings_index | player_1_name | player_2_name | partnership_runs | boundary_reason |
|---|---|---|---|---|---|---|---|
| 1273750 | T20I | 2021-11-06 | 2 | JC Buttler | JJ Roy | 38 | retirement:retired hurt |
| 1448352 | Test | 2025-07-23 | 2 | JE Root | BA Stokes | 142 | replacement |
| 1496589 | ODI | 2026-09-24 | 2 | JC Buttler | WG Jacks | 51 | replacement |

## Innings with penalty runs, absent batters or super overs

| match_id | format | innings_index | penalty_runs_pre | penalty_runs_post | absent_hurt | super_over | runs_from_deliveries |
|---|---|---|---|---|---|---|---|
| 1384411 | ODI | 2 | 0 | 0 | RJW Topley | False | 170 |
| 1389401 | Test | 2 | 5 | 0 |  | False | 314 |
| 1428556 | Test | 4 | 0 | 0 | BA Stokes | False | 234 |
| 1448353 | Test | 2 | 0 | 0 | CR Woakes | False | 247 |

Penalty runs given to a whole innings are not part of any ball, so they are not given to any pair.
