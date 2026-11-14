"""Stage 6: compute network- and node-level measures for each format."""
import _bootstrap  # noqa: F401

import pandas as pd

from batnet import aggregate, config, metrics, tables
from batnet.logutil import get_logger

log = get_logger("06_metrics")


def load_graph(fmt: str):
    slug = config.FORMAT_SLUG[fmt]
    nodes = tables.read_csv(config.PROCESSED_DIR / f"nodes_{slug}.csv")
    edges = tables.read_csv(config.PROCESSED_DIR / f"edges_{slug}.csv")
    return aggregate.build_graph(nodes, edges, fmt)


def main() -> None:
    summaries = {}
    for fmt in config.FORMATS:
        slug = config.FORMAT_SLUG[fmt]
        g = load_graph(fmt)
        nm = metrics.node_metrics(g)
        tables.write_csv(nm, config.TABLES_DIR / f"node_metrics_{slug}.csv")
        summaries[fmt] = metrics.network_summary(g, nm)
        core = nm.groupby("core_number").size().rename("players").reset_index()
        core.insert(0, "format", fmt)
        tables.write_csv(core, config.TABLES_DIR / f"core_sizes_{slug}.csv")
        comm = (nm.sort_values(["community", "strength"], ascending=[True, False])
                .groupby("community").agg(players=("player_id", "size"), total_node_strength=("strength", "sum"),
                                          members=("player_name", lambda s: "; ".join(s))).reset_index())
        comm.insert(0, "format", fmt)
        tables.write_csv(comm, config.TABLES_DIR / f"communities_{slug}.csv")
        log.info("%s: %s", fmt, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in summaries[fmt].items()})
    summary = pd.DataFrame(summaries).rename_axis("measure").reset_index()
    tables.write_csv(summary, config.TABLES_DIR / "network_summary.csv")


if __name__ == "__main__":
    main()
