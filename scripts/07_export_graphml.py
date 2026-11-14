"""Stage 7a: export one GraphML per format (with metrics as node attributes)."""
import _bootstrap  # noqa: F401
import sys

import pandas as pd

from batnet import aggregate, config, export, tables
from batnet.logutil import get_logger

log = get_logger("07_graphml")

NODE_METRICS = ["degree", "strength", "strength_per_innings", "betweenness", "closeness_lcc",
                "eigenvector_lcc", "clustering", "core_number", "community", "effective_size", "constraint"]


def graph_with_metrics(fmt: str):
    slug = config.FORMAT_SLUG[fmt]
    nodes = tables.read_csv(config.PROCESSED_DIR / f"nodes_{slug}.csv")
    edges = tables.read_csv(config.PROCESSED_DIR / f"edges_{slug}.csv")
    # GraphML dates use the same DD-MM-YYYY text as the CSV tables.
    for df in (nodes, edges):
        for col in ("first_date", "last_date"):
            df[col] = pd.to_datetime(df[col]).dt.strftime(config.DATE_FMT)
    g = aggregate.build_graph(nodes, edges, fmt)
    nm = tables.read_csv(config.TABLES_DIR / f"node_metrics_{slug}.csv").set_index("player_id")
    for v in g.nodes:
        for col in NODE_METRICS:
            val = nm.loc[v, col]
            if pd.isna(val):
                continue  # missing values are omitted, never written as "nan"
            g.nodes[v][col] = int(val) if col in ("degree", "strength", "core_number", "community") else float(val)
    return g


def main() -> int:
    rows = []
    for fmt in config.FORMATS:
        g = graph_with_metrics(fmt)
        path = config.GRAPHML_DIR / f"england_men_{config.FORMAT_SLUG[fmt]}.graphml"
        export.write_graphml(g, path)
        checks = export.roundtrip_check(g, path)
        rows += [{"format": fmt, "check": k, "passed": v} for k, v in checks.items()]
        log.info("%s -> %s: %d nodes, %d edges, round trip %s", fmt, path.name, g.number_of_nodes(),
                 g.number_of_edges(), "OK" if all(checks.values()) else f"FAILED {checks}")
    df = pd.DataFrame(rows)
    tables.write_csv(df, config.TABLES_DIR / "validation_graphml_roundtrip.csv")
    return 0 if df["passed"].all() else 1


if __name__ == "__main__":
    sys.exit(main())
