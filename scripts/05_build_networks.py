"""Stage 5: aggregate observations into per-format node and edge tables."""
import _bootstrap  # noqa: F401
import sys

import pandas as pd

from batnet import aggregate, config, tables
from batnet.logutil import get_logger

log = get_logger("05_networks")


def main() -> int:
    obs = tables.read_csv(config.PROCESSED_DIR / "partnership_observations.csv")
    players = aggregate.build_player_table(obs)
    nodes = aggregate.build_node_table(obs, players)
    edges = aggregate.build_edge_table(obs, players)
    tables.write_csv(players, config.PROCESSED_DIR / "players.csv")

    results = []
    for fmt in config.FORMATS:
        slug = config.FORMAT_SLUG[fmt]
        tables.write_csv(nodes[nodes["format"] == fmt], config.PROCESSED_DIR / f"nodes_{slug}.csv")
        tables.write_csv(edges[edges["format"] == fmt], config.PROCESSED_DIR / f"edges_{slug}.csv")
        for name, ok, detail in aggregate.check_invariants(obs, nodes, edges, fmt):
            results.append({"format": fmt, "check": name, "passed": ok, "detail": detail})
        g = aggregate.build_graph(nodes, edges, fmt)
        log.info("%s: %d nodes, %d edges, total weight %d", fmt, g.number_of_nodes(),
                 g.number_of_edges(), int(g.size(weight="weight")))
    checks = pd.DataFrame(results)
    tables.write_csv(checks, config.TABLES_DIR / "validation_aggregation_checks.csv")
    multi = players[players["name_variants"].str.contains("|", regex=False)]
    log.info("players with more than one name spelling: %d", len(multi))
    ok = bool(checks["passed"].all())
    log.info("aggregation checks passed: %d/%d - GATE %s", checks["passed"].sum(), len(checks),
             "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
