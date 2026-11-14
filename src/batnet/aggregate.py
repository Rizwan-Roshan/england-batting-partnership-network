"""Stage 5 - aggregate partnership observations into node and edge tables.

One graph per format; formats are never pooled. Everything here is a pure
function of the observation table so the graphs are reconstructible from it.
"""
from __future__ import annotations

import networkx as nx
import pandas as pd

EDGE_KEYS = ["format", "player_1_id", "player_2_id"]


def build_player_table(obs: pd.DataFrame) -> pd.DataFrame:
    """Stable ID -> display name (most frequent spelling) and all name variants."""
    long = pd.concat(
        [
            obs[["player_1_id", "player_1_name"]].set_axis(["player_id", "name"], axis=1),
            obs[["player_2_id", "player_2_name"]].set_axis(["player_id", "name"], axis=1),
        ]
    )
    counts = long.value_counts().reset_index(name="n").sort_values(
        ["player_id", "n", "name"], ascending=[True, False, True]
    )
    best = counts.drop_duplicates("player_id").set_index("player_id")["name"]
    variants = counts.groupby("player_id")["name"].agg(lambda s: "|".join(sorted(set(s))))
    return pd.DataFrame({"player_name": best, "name_variants": variants}).reset_index()


def build_edge_table(obs: pd.DataFrame, players: pd.DataFrame) -> pd.DataFrame:
    """One row per (format, unordered pair). ``player_1_id < player_2_id`` always."""
    o = obs.copy()
    o["innings_key"] = o["match_id"].astype(str) + "#" + o["innings_index"].astype(str)
    g = o.groupby(EDGE_KEYS, sort=True)
    edges = g.agg(
        weight=("partnership_runs", "sum"),
        partnership_count=("partnership_runs", "size"),
        total_matches=("match_id", "nunique"),
        total_innings=("innings_key", "nunique"),
        first_date=("match_date", "min"),
        last_date=("match_date", "max"),
        mean_partnership_runs=("partnership_runs", "mean"),
        median_partnership_runs=("partnership_runs", "median"),
        min_partnership_runs=("partnership_runs", "min"),
        max_partnership_runs=("partnership_runs", "max"),
    ).reset_index()
    names = players.set_index("player_id")["player_name"]
    edges.insert(2, "player_1_name", edges["player_1_id"].map(names))
    edges.insert(4, "player_2_name", edges["player_2_id"].map(names))
    edges["pair_key"] = edges["player_1_id"] + "__" + edges["player_2_id"]
    return edges


def build_node_table(obs: pd.DataFrame, players: pd.DataFrame) -> pd.DataFrame:
    """One row per (format, player) that appears in at least one observation.

    Denominators
    ------------
    matches_batted: distinct matches in which the player has >= 1 observation.
    innings_batted: distinct innings in which the player has >= 1 observation.
    partnership_observations: observations the player took part in.
    distinct_partners: distinct other players partnered (= graph degree).
    """
    cols = ["format", "match_id", "innings_index"]
    a = obs[cols + ["player_1_id", "player_2_id"]].set_axis(cols + ["player_id", "partner_id"], axis=1)
    b = obs[cols + ["player_2_id", "player_1_id"]].set_axis(cols + ["player_id", "partner_id"], axis=1)
    long = pd.concat([a, b], ignore_index=True)
    long["innings_key"] = long["match_id"].astype(str) + "#" + long["innings_index"].astype(str)
    nodes = long.groupby(["format", "player_id"], sort=True).agg(
        matches_batted=("match_id", "nunique"),
        innings_batted=("innings_key", "nunique"),
        partnership_observations=("partner_id", "size"),
        distinct_partners=("partner_id", "nunique"),
    ).reset_index()
    nodes.insert(2, "player_name", nodes["player_id"].map(players.set_index("player_id")["player_name"]))
    return nodes


def build_graph(nodes: pd.DataFrame, edges: pd.DataFrame, fmt: str) -> nx.Graph:
    """Undirected weighted one-mode graph for one format."""
    g = nx.Graph(format=fmt)
    for r in nodes[nodes["format"] == fmt].itertuples(index=False):
        g.add_node(
            r.player_id, player_id=r.player_id, player_name=r.player_name, label=r.player_name,
            format=fmt, matches_batted=int(r.matches_batted), innings_batted=int(r.innings_batted),
            partnership_observations=int(r.partnership_observations),
            distinct_partners=int(r.distinct_partners),
        )
    for r in edges[edges["format"] == fmt].itertuples(index=False):
        g.add_edge(
            r.player_1_id, r.player_2_id,
            weight=int(r.weight), partnership_count=int(r.partnership_count),
            total_matches=int(r.total_matches), total_innings=int(r.total_innings),
            first_date=str(r.first_date), last_date=str(r.last_date), format=fmt,
            mean_partnership_runs=float(r.mean_partnership_runs),
            median_partnership_runs=float(r.median_partnership_runs),
            min_partnership_runs=int(r.min_partnership_runs),
            max_partnership_runs=int(r.max_partnership_runs),
        )
    return g


def check_invariants(obs: pd.DataFrame, nodes: pd.DataFrame, edges: pd.DataFrame, fmt: str) -> list[tuple[str, bool, str]]:
    """Aggregation checks of instructions section 7.3. Returns (check, passed, detail)."""
    o = obs[obs["format"] == fmt]
    e = edges[edges["format"] == fmt]
    n = nodes[nodes["format"] == fmt]
    g = build_graph(nodes, edges, fmt)
    pairs = o.groupby(["player_1_id", "player_2_id"])
    out: list[tuple[str, bool, str]] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        out.append((name, bool(ok), detail))

    add("no_self_loops", (e["player_1_id"] != e["player_2_id"]).all() and nx.number_of_selfloops(g) == 0)
    add("canonical_pair_order", (e["player_1_id"] < e["player_2_id"]).all())
    add("edge_count_equals_unique_pairs", len(e) == pairs.ngroups == g.number_of_edges(),
        f"{len(e)} edges / {pairs.ngroups} pairs")
    ei = e.set_index(["player_1_id", "player_2_id"])
    add("weight_equals_sum_of_observation_runs", ei["weight"].equals(pairs["partnership_runs"].sum().reindex(ei.index)))
    add("partnership_count_equals_observation_count", (ei["partnership_count"] == pairs.size().reindex(ei.index)).all())
    add("total_matches_correct", (ei["total_matches"] == pairs["match_id"].nunique().reindex(ei.index)).all())
    inn = o.assign(k=o["match_id"].astype(str) + "#" + o["innings_index"].astype(str))
    add("total_innings_correct",
        (ei["total_innings"] == inn.groupby(["player_1_id", "player_2_id"])["k"].nunique().reindex(ei.index)).all())
    add("sum_of_weights_equals_sum_of_observation_runs", int(e["weight"].sum()) == int(o["partnership_runs"].sum()),
        f"{int(e['weight'].sum())} runs")
    add("every_edge_has_observations", (e["partnership_count"] >= 1).all())
    players = set(o["player_1_id"]) | set(o["player_2_id"])
    add("node_set_equals_players_in_observations", set(n["player_id"]) == players == set(g.nodes),
        f"{len(n)} nodes")
    deg = dict(g.degree())
    add("distinct_partners_equals_degree", all(deg[r.player_id] == r.distinct_partners for r in n.itertuples()))
    add("node_observations_sum_is_twice_observations", int(n["partnership_observations"].sum()) == 2 * len(o))
    return out
