"""Figures drawn in Python (matplotlib) from the same graphs exported to Gephi.

Visual conventions, identical for every format:
* layout: ForceAtlas2 (networkx implementation) on the unweighted topology,
  fixed seed - layout distance is not a statistic;
* node area proportional to strength (partnership runs with all partners);
* edge width proportional to edge weight (partnership runs of the pair);
* node colour: Louvain community (communities of fewer than 3 players grey);
* labels only for the most prominent nodes, to keep figures readable.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from . import config

COMMUNITY_COLOURS = ["#2a78d6", "#eb6834", "#1baf7a", "#6250d6"]
OTHER_COLOUR = "#9a9993"
INK, MUTED, SURFACE = "#0b0b0b", "#52514e", "#ffffff"
MIN_COMMUNITY = 3


def layout(g: nx.Graph) -> dict:
    """Deterministic ForceAtlas2 positions computed on the unweighted topology.

    Run totals differ by orders of magnitude between pairs; using them as
    attraction collapses the heavy pairs into one point, so the layout uses
    ties only and weights are shown through edge width instead.
    """
    return nx.forceatlas2_layout(g, weight=None, seed=config.RANDOM_SEED, max_iter=2000,
                                 scaling_ratio=2.0, gravity=1.0)


def community_colours(nm: pd.DataFrame) -> tuple[dict, list[tuple[str, str]]]:
    """Colour per node and legend entries. Community 1 is the largest."""
    sizes = nm.groupby("community").size()
    colour_of, legend, k = {}, [], 0
    for c in sorted(sizes.index):
        if sizes[c] >= MIN_COMMUNITY and k < len(COMMUNITY_COLOURS):
            colour_of[c] = COMMUNITY_COLOURS[k]
            legend.append((f"Community {c} ({sizes[c]} players)", COMMUNITY_COLOURS[k]))
            k += 1
        else:
            colour_of[c] = OTHER_COLOUR
    if OTHER_COLOUR in colour_of.values():
        legend.append((f"Communities of < {MIN_COMMUNITY} players", OTHER_COLOUR))
    return {r.player_id: colour_of[r.community] for r in nm.itertuples()}, legend


def draw_network(ax, g: nx.Graph, nm: pd.DataFrame, title: str, n_labels: int = 14,
                 size_scale: float = 1.0, font: float = 8.0) -> None:
    """Draw one format network on ``ax`` with the shared conventions."""
    pos = layout(g)
    colours, legend = community_colours(nm)
    strength = nm.set_index("player_id")["strength"]
    smax = 15303.0  # fixed reference so node sizes are comparable across formats
    sizes = [size_scale * (25 + 1100 * strength[v] / smax) for v in g.nodes]
    w = np.array([d["weight"] for _, _, d in g.edges(data=True)], dtype=float)
    widths = 0.25 + 5.0 * w / 2697.0  # fixed reference: heaviest edge in any format
    nx.draw_networkx_edges(g, pos, ax=ax, width=widths, edge_color="#8a8a86", alpha=0.45)
    nx.draw_networkx_nodes(g, pos, ax=ax, node_size=sizes, node_color=[colours[v] for v in g.nodes],
                           edgecolors=SURFACE, linewidths=0.9)
    top = set(nm.nlargest(n_labels, "strength")["player_id"]) | set(nm.nlargest(4, "betweenness")["player_id"])
    labels = {v: g.nodes[v]["player_name"] for v in top}
    for v, text in labels.items():
        x, y = pos[v]
        ax.annotate(text, (x, y), xytext=(0, 6 + np.sqrt(sizes[list(g.nodes).index(v)]) / 2.4),
                    textcoords="offset points", ha="center", fontsize=font, color=INK,
                    bbox=dict(boxstyle="round,pad=0.12", fc=SURFACE, ec="none", alpha=0.75))
    ax.set_title(title, fontsize=font + 3, color=INK, loc="left")
    handles = [Line2D([], [], marker="o", ls="", ms=7, mfc=c, mec=SURFACE, label=l) for l, c in legend]
    ax.legend(handles=handles, loc="lower left", fontsize=font - 1, frameon=False, labelcolor=MUTED)
    ax.set_axis_off()
    ax.margins(0.08)


CAPTION = ("Node area: strength (total partnership runs). Edge width: partnership runs of the pair. "
           "Colour: Louvain community. Layout: ForceAtlas2 (positions are not a measure).")


def figure_single(g: nx.Graph, nm: pd.DataFrame, fmt: str, path) -> None:
    fig, ax = plt.subplots(figsize=(9, 8), facecolor=SURFACE)
    draw_network(ax, g, nm, f"England Men {fmt} batting-partnership network "
                            f"({g.number_of_nodes()} batters, {g.number_of_edges()} pairs)", size_scale=1.6, font=9)
    fig.text(0.02, 0.012, CAPTION, fontsize=7.5, color=MUTED)
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)


def figure_comparison(graphs: dict, node_tables: dict, path) -> None:
    """2 x 2 grid: one panel per format plus a key, identical scales."""
    fig, axes = plt.subplots(2, 2, figsize=(9.4, 9.6), facecolor=SURFACE)
    flat = axes.ravel()
    for ax, fmt in zip(flat, config.FORMATS):
        g = graphs[fmt]
        draw_network(ax, g, node_tables[fmt], f"{fmt}: {g.number_of_nodes()} batters, {g.number_of_edges()} pairs",
                     n_labels=9, size_scale=0.75, font=9)
    key = flat[3]
    key.set_axis_off()
    key.set_xlim(0, 1); key.set_ylim(0, 1)
    key.text(0.05, 0.93, "Key (same scales in all panels)", fontsize=11, color=INK)
    for i, runs in enumerate((500, 5000, 15000)):
        y = 0.80 - 0.11 * i
        key.scatter([0.12], [y], s=0.75 * (25 + 1100 * runs / 15303.0), color=OTHER_COLOUR, edgecolors=SURFACE)
        key.text(0.24, y, f"strength {runs:,} runs", va="center", fontsize=9, color=MUTED)
    for i, runs in enumerate((50, 500, 2500)):
        y = 0.44 - 0.07 * i
        key.plot([0.05, 0.19], [y, y], lw=0.25 + 5.0 * runs / 2697.0, color="#8a8a86", solid_capstyle="round")
        key.text(0.24, y, f"pair total {runs:,} runs", va="center", fontsize=9, color=MUTED)
    key.text(0.05, 0.16, "Colour: Louvain community, numbered by size\nwithin each format.\n"
             "Layout: ForceAtlas2 on the unweighted ties;\npositions are a drawing aid, not a measure.",
             fontsize=9, color=MUTED, va="center", linespacing=1.35)
    fig.subplots_adjust(wspace=0.02, hspace=0.06, left=0.01, right=0.99, top=0.97, bottom=0.01)
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)


def figure_degree_distribution(node_tables: dict, path) -> None:
    """Small multiples: degree histogram per format, shared axes."""
    fig, axes = plt.subplots(1, 3, figsize=(10, 2.9), sharex=True, sharey=True, facecolor=SURFACE)
    bins = np.arange(0, 42, 3)
    for ax, fmt in zip(axes, config.FORMATS):
        deg = node_tables[fmt]["degree"]
        ax.hist(deg, bins=bins, color="#2a78d6", edgecolor=SURFACE, linewidth=1.2)
        ax.axvline(deg.mean(), color=INK, lw=1, ls="--")
        ax.text(deg.mean() + 0.8, 0.93, f"mean {deg.mean():.1f}", transform=ax.get_xaxis_transform(),
                fontsize=8, color=MUTED)
        ax.set_title(fmt, fontsize=10, loc="left", color=INK)
        ax.set_xlabel("Degree (distinct partners)", fontsize=8.5, color=MUTED)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.spines["left"].set_color("#c9c8c2"); ax.spines["bottom"].set_color("#c9c8c2")
        ax.tick_params(labelsize=8, colors=MUTED, length=0)
        ax.grid(axis="y", color="#ecebe6", lw=0.8); ax.set_axisbelow(True)
    axes[0].set_ylabel("Number of batters", fontsize=8.5, color=MUTED)
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)
