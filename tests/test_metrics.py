"""Metric conventions checked on small graphs with hand-computed values."""
import networkx as nx
import pytest

from batnet import metrics


def toy() -> nx.Graph:
    """Triangle a-b-c plus pendant d attached to a. Weights are strengths."""
    g = nx.Graph(format="ODI")
    for n in "abcd":
        g.add_node(n, format="ODI", player_name=n.upper(), matches_batted=2, innings_batted=2,
                   partnership_observations=3)
    g.add_edge("a", "b", weight=100, partnership_count=2)
    g.add_edge("a", "c", weight=10, partnership_count=1)
    g.add_edge("b", "c", weight=1, partnership_count=1)
    g.add_edge("a", "d", weight=50, partnership_count=1)
    return g


def test_node_metrics_values():
    nm = metrics.node_metrics(toy()).set_index("player_id")
    assert nm.loc["a", "degree"] == 3 and nm.loc["a", "strength"] == 160
    assert nm.loc["a", "strength_per_innings"] == 80
    assert nm.loc["a", "degree_centrality"] == 1.0
    # Unweighted betweenness: a lies on b-d and c-d shortest paths -> 2 of 3 pairs.
    assert nm.loc["a", "betweenness"] == pytest.approx(2 / 3)
    assert nm.loc["b", "betweenness"] == 0
    assert nm.loc["a", "closeness_lcc"] == 1.0
    assert nm.loc["d", "closeness_lcc"] == pytest.approx(3 / 5)
    assert nm.loc["a", "clustering"] == pytest.approx(1 / 3)
    assert nm.loc["b", "clustering"] == 1.0
    assert nm.loc["a", "core_number"] == 2 and nm.loc["d", "core_number"] == 1
    # Effective size (binary): degree - 2t/degree, t = ties among alters.
    assert nm.loc["a", "effective_size"] == pytest.approx(3 - 2 / 3)
    assert nm.loc["a", "redundancy"] == pytest.approx(2 / 3)
    assert nm.loc["b", "effective_size"] == pytest.approx(1.0)
    assert nm["eigenvector_lcc"].idxmax() == "a"
    assert nm.index[0] == "a"  # sorted by strength


def test_weights_do_not_change_path_measures():
    g = toy()
    h = toy()
    for _, _, d in h.edges(data=True):
        d["weight"] = 1
    a, b = metrics.node_metrics(g).set_index("player_id"), metrics.node_metrics(h).set_index("player_id")
    for col in ("betweenness", "closeness_lcc", "clustering", "core_number", "effective_size", "constraint"):
        assert a[col].equals(b[col].reindex(a.index)), col


def test_network_summary_values():
    g = toy()
    s = metrics.network_summary(g, metrics.node_metrics(g))
    assert (s["nodes"], s["edges"], s["components"], s["lcc_nodes"]) == (4, 4, 1, 4)
    assert s["density"] == pytest.approx(4 / 6)
    assert s["transitivity"] == pytest.approx(3 / 5)  # 3 * 1 triangle / 5 connected triples
    assert s["avg_path_length_lcc"] == pytest.approx(8 / 6)
    assert s["diameter_lcc"] == 2 and s["edge_weight_total"] == 161
    assert s["max_core_k"] == 2 and s["max_core_nodes"] == 3


def test_degree_centralization_extremes():
    assert metrics.degree_centralization(nx.star_graph(5)) == pytest.approx(1.0)
    assert metrics.degree_centralization(nx.cycle_graph(6)) == 0


def test_disconnected_graph_restricts_closeness_to_lcc():
    g = toy()
    for n in "xy":
        g.add_node(n, format="ODI", player_name=n, matches_batted=1, innings_batted=1, partnership_observations=1)
    g.add_edge("x", "y", weight=5, partnership_count=1)
    nm = metrics.node_metrics(g).set_index("player_id")
    assert not nm.loc["x", "in_lcc"] and nm.loc["x", "closeness_lcc"] != nm.loc["x", "closeness_lcc"]  # NaN
    s = metrics.network_summary(g, nm.reset_index())
    assert (s["components"], s["lcc_nodes"], s["connected"]) == (2, 4, 0)


def test_louvain_is_deterministic_for_fixed_seed():
    g = nx.karate_club_graph()
    assert metrics.louvain_partition(g, seed=42) == metrics.louvain_partition(g, seed=42)
