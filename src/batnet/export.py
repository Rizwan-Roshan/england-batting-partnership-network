"""GraphML export for Gephi, with a re-import check."""
from __future__ import annotations

from pathlib import Path

import networkx as nx


def write_graphml(g: nx.Graph, path: Path) -> None:
    """Write an undirected GraphML file with flat, typed attributes only."""
    if g.is_directed():
        raise ValueError("graph must be undirected")
    for _, data in g.nodes(data=True):
        for k, v in data.items():
            if not isinstance(v, (str, int, float, bool)):
                raise TypeError(f"node attribute {k} has unsupported type {type(v)}")
    for _, _, data in g.edges(data=True):
        for k, v in data.items():
            if not isinstance(v, (str, int, float, bool)):
                raise TypeError(f"edge attribute {k} has unsupported type {type(v)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    nx.write_graphml(g, path, encoding="utf-8", infer_numeric_types=False)


def roundtrip_check(g: nx.Graph, path: Path) -> dict[str, bool]:
    """Re-read the GraphML file and compare it with the in-memory graph."""
    h = nx.read_graphml(path)
    same_weights = all(
        h.has_edge(u, v) and h[u][v]["weight"] == d["weight"] for u, v, d in g.edges(data=True)
    )
    return {
        "undirected": not h.is_directed(),
        "node_count": h.number_of_nodes() == g.number_of_nodes(),
        "edge_count": h.number_of_edges() == g.number_of_edges(),
        "node_ids": set(h.nodes) == set(g.nodes),
        "labels": all(h.nodes[n].get("label") == g.nodes[n].get("label") for n in g.nodes),
        "weights_numeric_and_equal": same_weights
        and all(isinstance(d["weight"], (int, float)) for _, _, d in h.edges(data=True)),
        "total_weight": sum(d["weight"] for _, _, d in h.edges(data=True))
        == sum(d["weight"] for _, _, d in g.edges(data=True)),
    }
