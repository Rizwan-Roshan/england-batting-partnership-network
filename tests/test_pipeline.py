"""Required cases 9-14 and 16: filters, identity, aggregation, GraphML."""
import json
from datetime import date

import pandas as pd
from conftest import ball, innings, match

from batnet import aggregate, export, pipeline
from batnet.filters import exclusion_reason, match_metadata

A, B, C = "A One", "B Two", "C Three"


def reason(**kw):
    return exclusion_reason(match_metadata(match([], **kw), "1.json"))


def build(matches):
    """matches: list of (match_id, match dict) -> observations/nodes/edges."""
    obs = []
    for mid, m in matches:
        meta = match_metadata(m, f"{mid}.json")
        assert exclusion_reason(meta) == ""
        obs += pipeline.extract_match(m, meta)[0]
    obs = pd.DataFrame(obs, columns=pipeline.OBS_COLUMNS)
    players = aggregate.build_player_table(obs)
    return obs, aggregate.build_node_table(obs, players), aggregate.build_edge_table(obs, players), players


def test_11_date_boundaries():
    assert reason(date="2020-01-01") == ""
    assert reason(date="2026-10-29") == ""
    assert reason(date="2019-12-31") == "before_window"
    assert reason(date="2026-10-30") == "after_window"


def test_12_gender_team_format_filters():
    assert reason(gender="female") == "gender_not_male"
    assert reason(team_type="club", match_type="T20") == "not_international"
    assert reason(teams=("Australia", "India")) == "england_not_playing"
    assert reason(match_type="MDM") == "format_not_target"
    assert reason(match_type="T20") == "" and reason(match_type="Test") == ""
    assert match_metadata(match([], match_type="T20"), "1.json")["format"] == "T20I"


def test_09_same_pair_different_matches_accumulates():
    m1 = match([innings([ball(A, B, 10), ball(A, B, 5)])], date="2021-05-01")
    m2 = match([innings([ball(B, A, 20)])], date="2023-07-09")
    obs, nodes, edges, _ = build([("m1", m1), ("m2", m2)])
    assert len(edges) == 1
    e = edges.iloc[0]
    assert (e.weight, e.partnership_count, e.total_matches, e.total_innings) == (35, 2, 2, 2)
    assert (e.first_date, e.last_date) == (date(2021, 5, 1), date(2023, 7, 9))
    assert (e.min_partnership_runs, e.max_partnership_runs, e.mean_partnership_runs) == (15, 20, 17.5)
    assert all(ok for _, ok, _ in aggregate.check_invariants(obs, nodes, edges, "ODI"))


def test_08b_reunited_pair_one_edge_two_observations():
    m = match([innings([ball(A, B, 5), ball(A, B, 0, wickets=[(A, "retired hurt")]),
                        ball(C, B, 2), ball(C, B, 0, wickets=[(C, "lbw")]), ball(A, B, 7)])])
    obs, nodes, edges, _ = build([("m1", m)])
    ab = edges[(edges.player_1_id == "id_a") & (edges.player_2_id == "id_b")].iloc[0]
    assert (ab.weight, ab.partnership_count, ab.total_matches, ab.total_innings) == (12, 2, 1, 1)
    b = nodes[nodes.player_id == "id_b"].iloc[0]
    assert (b.matches_batted, b.innings_batted, b.partnership_observations, b.distinct_partners) == (1, 1, 3, 2)


def test_10_same_pair_different_formats_separate_graphs():
    m1 = match([innings([ball(A, B, 10)])], match_type="Test")
    m2 = match([innings([ball(A, B, 3)])], match_type="T20")
    obs, nodes, edges, _ = build([("m1", m1), ("m2", m2)])
    assert sorted(edges["format"]) == ["T20I", "Test"]
    gt = aggregate.build_graph(nodes, edges, "Test")
    g20 = aggregate.build_graph(nodes, edges, "T20I")
    assert gt["id_a"]["id_b"]["weight"] == 10 and g20["id_a"]["id_b"]["weight"] == 3
    assert aggregate.build_graph(nodes, edges, "ODI").number_of_nodes() == 0


def test_13_player_identity():
    # "A One" and "A. One" share id_a -> merge; "A One Jr" (id_a2) stays separate.
    m1 = match([innings([ball("A One", B, 4), ball("A One", B, 4)])])
    m2 = match([innings([ball("A. One", B, 6)])], date="2022-06-02")
    m3 = match([innings([ball("A One Jr", B, 1)])], date="2022-06-03")
    obs, nodes, edges, players = build([("m1", m1), ("m2", m2), ("m3", m3)])
    assert sorted(nodes.player_id) == ["id_a", "id_a2", "id_b"]
    assert edges.set_index("pair_key").loc["id_a__id_b", "weight"] == 14
    p = players.set_index("player_id")
    assert p.loc["id_a", "name_variants"] == "A One|A. One"
    assert p.loc["id_a", "player_name"] == "A One"


def test_14_roster_only_player_not_a_node():
    m = match([innings([ball(A, B, 1)])], players={"England": [A, B, "R Roster"]})
    _, nodes, _, _ = build([("m1", m)])
    assert "id_r" not in set(nodes.player_id) and len(nodes) == 2


def test_opponent_and_super_over_innings_ignored():
    m = match([innings([ball(A, B, 9)], team="Australia"), innings([ball(A, B, 4)]),
               innings([ball(A, C, 12)], super_over=True)])
    meta = match_metadata(m, "m1.json")
    obs, inn, _ = pipeline.extract_match(m, meta)
    assert [(o["innings_index"], o["partnership_runs"]) for o in obs] == [(2, 4)]
    assert [(i["innings_index"], i["qualifying"]) for i in inn] == [(2, True), (3, False)]


def test_15b_penalty_recorded_separately():
    m = match([innings([ball(A, B, 2)], penalty_runs={"pre": 5})])
    obs, inn, _ = pipeline.extract_match(m, match_metadata(m, "m1.json"))
    assert obs[0]["partnership_runs"] == 2
    assert (inn[0]["penalty_runs_pre"], inn[0]["partnership_runs_sum"]) == (5, 2)


def test_16_graphml_round_trip(tmp_path):
    m = match([innings([ball(A, B, 5), ball(A, B, 0, wickets=[(A, "bowled")]), ball(C, B, 8)])])
    obs, nodes, edges, _ = build([("m1", m)])
    g = aggregate.build_graph(nodes, edges, "ODI")
    path = tmp_path / "g.graphml"
    export.write_graphml(g, path)
    checks = export.roundtrip_check(g, path)
    assert all(checks.values()), checks
    assert 'edgedefault="undirected"' in path.read_text()
    assert (g.number_of_nodes(), g.number_of_edges()) == (3, 2)


def test_audit_logs_unreadable_file(tmp_path):
    good, bad = tmp_path / "1.json", tmp_path / "2.json"
    good.write_text(json.dumps(match([])))
    bad.write_text("{not json")
    audit = pipeline.audit_matches([good, bad]).set_index("filename")
    assert bool(audit.loc["1.json", "included"]) is True
    assert audit.loc["2.json", "exclusion_reason"].startswith("unreadable")
