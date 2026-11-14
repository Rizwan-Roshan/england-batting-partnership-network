"""Required extraction cases 1-8 and 15 (instructions section 13)."""
from conftest import REGISTRY, ball, innings

from batnet.extract import extract_innings

A, B, C, D, E = "A One", "B Two", "C Three", "D Four", "E Five"


def run(deliveries, **extra):
    return extract_innings(innings(deliveries, **extra), REGISTRY, "m1", 1)


def pairs(res):
    return [(o.player_1_id, o.player_2_id, o.partnership_runs) for o in res.observations]


def test_01_simple_partnership():
    res = run([ball(A, B, 1), ball(B, A, 4), ball(B, A, 0), ball(B, A, 2)])
    assert pairs(res) == [("id_a", "id_b", 7)]
    o = res.observations[0]
    assert (o.deliveries, o.start_delivery_id, o.end_delivery_id) == (4, "1.0.1", "1.0.4")
    assert o.boundary_reason == "innings_end" and res.warnings == []


def test_02_strike_rotation_keeps_partnership():
    res = run([ball(A, B, 1), ball(B, A, 1), ball(A, B, 3), ball(B, A, 1), ball(A, B, 0)])
    assert pairs(res) == [("id_a", "id_b", 6)]
    assert len(res.observations) == 1


def test_03_ordinary_wicket_runs_go_to_old_pair():
    # A is caught on a delivery worth 1 run (e.g. a run completed off a no-ball).
    res = run([ball(A, B, 4), ball(A, B, 1, wickets=[(A, "caught")]), ball(C, B, 2), ball(B, C, 3)])
    assert pairs(res) == [("id_a", "id_b", 5), ("id_b", "id_c", 5)]
    assert res.observations[0].boundary_reason == "dismissal:caught"
    assert res.observations[0].end_delivery_id == "1.0.2"
    assert res.observations[1].start_delivery_id == "1.0.3"
    assert res.observations[1].partnership_seq == 2 and res.warnings == []


def test_04_non_striker_run_out_closes_partnership():
    res = run([ball(A, B, 2), ball(A, B, 1, wickets=[(B, "run out")]), ball(A, C, 6)])
    assert pairs(res) == [("id_a", "id_b", 3), ("id_a", "id_c", 6)]
    assert res.observations[0].boundary_reason == "dismissal:run out"


def test_05_extras_counted_once():
    # wide: total 1 (extras 1); no-ball hit for four: total 5 (batter 4, extras 1)
    res = run([ball(A, B, 1, extras=1, extras_detail={"wides": 1}),
               ball(A, B, 5, batter_runs=4, extras=1), ball(A, B, 2)])
    o = res.observations[0]
    assert o.partnership_runs == 8  # not 10
    assert (o.batter_runs, o.extras_runs) == (6, 2)
    assert res.runs_from_deliveries == 8


def test_06_multiple_wickets_no_fictitious_partnership():
    res = run([ball(A, B, 3),
               ball(A, B, 0, wickets=[(A, "retired hurt"), (B, "run out")]),
               ball(C, D, 4)])
    assert pairs(res) == [("id_a", "id_b", 3), ("id_c", "id_d", 4)]
    assert res.observations[0].boundary_reason == "dismissal:retired hurt+run out"
    assert res.wicket_records == 2 and res.warnings == []


def test_07_innings_end_closes_final_partnership_once():
    res = run([ball(A, B, 1), ball(A, B, 0, wickets=[(A, "bowled")]), ball(C, B, 2)])
    assert [o.boundary_reason for o in res.observations] == ["dismissal:bowled", "innings_end"]
    # innings ending on a wicket: no extra empty observation
    res2 = run([ball(A, B, 1), ball(A, B, 0, wickets=[(A, "bowled")])])
    assert len(res2.observations) == 1
    assert res2.observations[0].boundary_reason == "dismissal:bowled"


def test_08_same_pair_reunites_as_separate_observations():
    res = run([ball(A, B, 5),
               ball(A, B, 0, wickets=[(A, "retired hurt")]),
               ball(C, B, 2),
               ball(C, B, 0, wickets=[(C, "lbw")]),
               ball(A, B, 7)])
    assert pairs(res) == [("id_a", "id_b", 5), ("id_b", "id_c", 2), ("id_a", "id_b", 7)]
    assert res.observations[0].boundary_reason == "retirement:retired hurt"
    assert res.warnings == []


def test_15_innings_level_penalty_not_assigned():
    res = run([ball(A, B, 2), ball(A, B, 1)], penalty_runs={"pre": 5})
    assert pairs(res) == [("id_a", "id_b", 3)]
    assert res.runs_from_deliveries == 3


def test_unexplained_pair_change_is_logged_not_carried():
    res = run([ball(A, B, 2), ball(C, B, 1)])
    assert pairs(res) == [("id_a", "id_b", 2), ("id_b", "id_c", 1)]
    assert res.observations[0].boundary_reason == "unexplained_pair_change"
    assert res.observations[0].quality_status == "warning"
    assert [w["code"] for w in res.warnings] == ["unexplained_pair_change"]


def test_batter_replacement_is_documented_boundary():
    repl = {"role": [{"in": C, "out": A, "reason": "injury", "role": "batter"}]}
    res = run([ball(A, B, 2), ball(C, B, 1, replacements=repl)])
    assert res.observations[0].boundary_reason == "replacement" and res.warnings == []


def test_dismissed_player_reappearing_is_flagged():
    res = run([ball(A, B, 0, wickets=[(A, "bowled")]), ball(A, B, 1)])
    assert [w["code"] for w in res.warnings] == ["player_out_still_at_crease"]
    assert len(res.observations) == 2
