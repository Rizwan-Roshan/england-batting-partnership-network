"""Stage 7b: render the report figures from the exported GraphML files."""
import _bootstrap  # noqa: F401

import networkx as nx

from batnet import config, tables, viz
from batnet.logutil import get_logger

log = get_logger("08_figures")


def main() -> None:
    graphs, node_tables = {}, {}
    for fmt in config.FORMATS:
        slug = config.FORMAT_SLUG[fmt]
        graphs[fmt] = nx.read_graphml(config.GRAPHML_DIR / f"england_men_{slug}.graphml")
        node_tables[fmt] = tables.read_csv(config.TABLES_DIR / f"node_metrics_{slug}.csv")
        viz.figure_single(graphs[fmt], node_tables[fmt], fmt, config.FIGURES_DIR / f"network_{slug}.png")
        log.info("wrote network_%s.png", slug)
    viz.figure_comparison(graphs, node_tables, config.FIGURES_DIR / "network_comparison.png")
    viz.figure_degree_distribution(node_tables, config.FIGURES_DIR / "degree_distributions.png")
    log.info("wrote network_comparison.png, degree_distributions.png")


if __name__ == "__main__":
    main()
