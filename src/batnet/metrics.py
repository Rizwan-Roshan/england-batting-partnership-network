"""Stage 6 - network measures (conventions documented in docs/methods_decisions.md).

Conventions used for every format
---------------------------------
* ``weight`` (partnership runs) is a tie *strength*. It is used only by
  measures that expect strengths: node strength, eigenvector centrality and
  Louvain modularity.
* All shortest-path measures (betweenness, closeness, path length, diameter)
  ignore weights: every partnership tie has length 1.
* Clustering, k-core, redundancy / effective size and constraint use the
  unweighted topology.
* Closeness, eigenvector centrality and path statistics are computed on the
  largest connected component (LCC); its size is always reported.
"""
from __future__ import annotations

import statistics

import networkx as nx
import numpy as np
import pandas as pd

from . import config


def largest_component(g: nx.Graph) -> nx.Graph:
    """Subgraph induced by the largest connected component."""
    return g.subgraph(max(nx.connected_components(g), key=len)).copy()


def louvain_partition(g: nx.Graph, seed: int = config.RANDOM_SEED) -> list[set[str]]:
    """Weighted Louvain partition, communities ordered by size then smallest ID."""
    comms = nx.community.louvain_communities(
        g, weight="weight", resolution=config.LOUVAIN_RESOLUTION, seed=seed
    )
    return sorted(comms, key=lambda c: (-len(c), min(c)))


def degree_centralization(g: nx.Graph) -> float:
    """Freeman degree centralisation: 0 = regular graph, 1 = star."""
    n = g.number_of_nodes()
    if n < 3:
        return float("nan")
    deg = [d for _, d in g.degree()]
    return sum(max(deg) - d for d in deg) / ((n - 1) * (n - 2))


def small_world(g: nx.Graph, n_graphs: int = config.N_RANDOM_GRAPHS, seed: int = config.RANDOM_SEED) -> dict[str, float]:
    """Compare clustering and path length with G(n, m) random graphs.

    sigma = (C / C_rand) / (L / L_rand), with C the average local clustering
    and L the average shortest-path length, both on the LCC of each graph.
    Random graphs have the same number of nodes and edges as the LCC.
    """
    lcc = largest_component(g)
    n, m = lcc.number_of_nodes(), lcc.number_of_edges()
    c_obs = nx.average_clustering(lcc)
    l_obs = nx.average_shortest_path_length(lcc)
    rng = np.random.default_rng(seed)
    cs, ls = [], []
    for _ in range(n_graphs):
        r = nx.gnm_random_graph(n, m, seed=int(rng.integers(0, 2**31 - 1)))
        r = largest_component(r)
        cs.append(nx.average_clustering(r))
        ls.append(nx.average_shortest_path_length(r))
    c_rand, l_rand = float(np.mean(cs)), float(np.mean(ls))
    return {"C_random": c_rand, "L_random": l_rand, "C_ratio": c_obs / c_rand,
            "L_ratio": l_obs / l_rand, "small_world_sigma": (c_obs / c_rand) / (l_obs / l_rand)}


def louvain_stability(g: nx.Graph, n_runs: int = 100) -> dict[str, float]:
    """Spread of the Louvain result over ``n_runs`` different seeds."""
    qs, ks = [], []
    for s in range(n_runs):
        p = louvain_partition(g, seed=s)
        qs.append(nx.community.modularity(g, p, weight="weight"))
        ks.append(len(p))
    return {"louvain_Q_min": min(qs), "louvain_Q_max": max(qs),
            "louvain_k_min": min(ks), "louvain_k_max": max(ks)}


def node_metrics(g: nx.Graph) -> pd.DataFrame:
    """Node-level measures for one format graph."""
    lcc = largest_component(g)
    deg = dict(g.degree())
    strength = dict(g.degree(weight="weight"))
    betw = nx.betweenness_centrality(g, weight=None, normalized=True)
    close = nx.closeness_centrality(lcc)  # unweighted, LCC only
    eig = nx.eigenvector_centrality(lcc, weight="weight", max_iter=5000, tol=1e-10)
    clust = nx.clustering(g)  # unweighted local clustering coefficient
    core = nx.core_number(g)
    eff = nx.effective_size(g)  # Burt, binary ties: degree - mean degree of alters inside ego net
    cons = nx.constraint(g)  # Burt's constraint, binary ties
    comm = {n: i for i, c in enumerate(louvain_partition(g), start=1) for n in c}
    n = g.number_of_nodes()
    rows = []
    for v, data in g.nodes(data=True):
        rows.append({
            "format": data["format"], "player_id": v, "player_name": data["player_name"],
            "matches_batted": data["matches_batted"], "innings_batted": data["innings_batted"],
            "partnership_observations": data["partnership_observations"],
            "first_date": data.get("first_date", ""), "last_date": data.get("last_date", ""),
            "median_entry_partnership": data.get("median_entry_partnership", float("nan")),
            "degree": deg[v], "degree_centrality": deg[v] / (n - 1),
            "strength": int(strength[v]), "strength_per_innings": strength[v] / data["innings_batted"],
            "betweenness": betw[v],
            "in_lcc": v in lcc,
            "closeness_lcc": close.get(v, float("nan")),
            "eigenvector_lcc": eig.get(v, float("nan")),
            "clustering": clust[v],
            "core_number": core[v],
            "community": comm[v],
            "effective_size": eff[v],
            "redundancy": deg[v] - eff[v],
            "efficiency": eff[v] / deg[v] if deg[v] else float("nan"),
            "constraint": cons[v],
        })
    return pd.DataFrame(rows).sort_values(["strength", "player_id"], ascending=[False, True]).reset_index(drop=True)


def network_summary(g: nx.Graph, nodes: pd.DataFrame) -> dict[str, float]:
    """Network-level description for one format graph."""
    n, m = g.number_of_nodes(), g.number_of_edges()
    comps = sorted((len(c) for c in nx.connected_components(g)), reverse=True)
    lcc = largest_component(g)
    deg = [d for _, d in g.degree()]
    strength = [s for _, s in g.degree(weight="weight")]
    w = [d["weight"] for _, _, d in g.edges(data=True)]
    cnt = [d["partnership_count"] for _, _, d in g.edges(data=True)]
    part = louvain_partition(g)
    core = nx.core_number(g)
    kmax = max(core.values())
    out: dict[str, float] = {
        "nodes": n, "edges": m,
        "density": nx.density(g),  # 2m / (n (n - 1)), no self-loops
        "components": len(comps), "lcc_nodes": comps[0], "lcc_share": comps[0] / n,
        "connected": int(len(comps) == 1),
        "degree_mean": float(np.mean(deg)), "degree_median": float(np.median(deg)),
        "degree_min": min(deg), "degree_max": max(deg), "degree_sd": float(np.std(deg, ddof=1)),
        "degree_centralization": degree_centralization(g),
        "strength_mean": float(np.mean(strength)), "strength_median": float(np.median(strength)),
        "strength_max": max(strength),
        "edge_weight_total": int(sum(w)), "edge_weight_mean": float(np.mean(w)),
        "edge_weight_median": float(np.median(w)), "edge_weight_max": max(w),
        "edges_single_observation_share": sum(1 for c in cnt if c == 1) / m,
        "top10pct_edges_weight_share": float(np.sort(w)[::-1][: max(1, round(0.1 * m))].sum() / sum(w)),
        "avg_clustering": nx.average_clustering(g),  # mean local coefficient, unweighted
        "transitivity": nx.transitivity(g),
        "avg_path_length_lcc": nx.average_shortest_path_length(lcc),
        "diameter_lcc": nx.diameter(lcc),
        "degree_assortativity": nx.degree_assortativity_coefficient(g),
        "max_core_k": kmax, "max_core_nodes": sum(1 for v in core.values() if v == kmax),
        "louvain_communities": len(part),
        "louvain_modularity": nx.community.modularity(g, part, weight="weight"),
        "louvain_sizes": "|".join(str(len(c)) for c in part),
        "mean_effective_size": float(nodes["effective_size"].mean()),
        "mean_efficiency": float(nodes["efficiency"].mean()),
        "mean_constraint": float(nodes["constraint"].mean()),
        "median_innings_batted": statistics.median(nodes["innings_batted"]),
    }
    out.update(small_world(g))
    out.update(louvain_stability(g))
    return out
