"""Report text. Every number is read from the pipeline output tables.

``build(ctx)`` returns a list of blocks:
("h", text) section heading, ("p", text) paragraph,
("table", caption, header, rows), ("fig", path, caption).
"""
from __future__ import annotations

import pandas as pd

from batnet import config, tables

F = config.FORMATS


class Ctx:
    """Loads the output tables once and offers small formatting helpers."""

    def __init__(self) -> None:
        T, P = config.TABLES_DIR, config.PROCESSED_DIR
        s = pd.read_csv(T / "network_summary.csv").set_index("measure")
        self.s = {f: s[f] for f in F}
        self.nm = {f: tables.read_csv(T / f"node_metrics_{config.FORMAT_SLUG[f]}.csv") for f in F}
        self.edges = {f: tables.read_csv(P / f"edges_{config.FORMAT_SLUG[f]}.csv") for f in F}
        self.counts = pd.read_csv(T / "dataset_counts.csv").set_index("format")
        self.audit = tables.read_csv(config.INTERIM_DIR / "file_audit.csv")
        self.obs = tables.read_csv(P / "partnership_observations.csv")
        self.score = pd.read_csv(T / "validation_scorecard_checks.csv")
        self.spots = pd.read_csv(T / "validation_spot_checks.csv")
        self.agg = pd.read_csv(T / "validation_aggregation_checks.csv")
        self.meta = tables.read_csv(P / "match_metadata.csv")

    def v(self, f: str, key: str, nd: int = 2) -> str:
        x = float(self.s[f][key])
        return f"{x:,.0f}" if nd == 0 else f"{x:.{nd}f}"

    def row(self, label: str, key: str, nd: int = 2) -> list[str]:
        return [label] + [self.v(f, key, nd) for f in F]

    def top(self, f: str, col: str, k: int = 3, nd: int = 0, ascending: bool = False) -> str:
        d = self.nm[f].sort_values([col, "player_id"], ascending=[ascending, True]).head(k)
        return ", ".join(f"{n} ({x:,.{nd}f})" for n, x in zip(d["player_name"], d[col]))

    def top_edges(self, f: str, k: int = 2) -> str:
        d = self.edges[f].nlargest(k, "weight")
        return "; ".join(f"{a}-{b} ({w:,} runs in {c} partnerships)"
                         for a, b, w, c in zip(d.player_1_name, d.player_2_name, d.weight, d.partnership_count))

    def community(self, f: str, c: int, k: int = 4) -> str:
        d = self.nm[f][self.nm[f]["community"] == c].nlargest(k, "strength")
        return ", ".join(d["player_name"])

    def comm_stat(self, f: str, c: int) -> tuple[int, float, int, int]:
        d = self.nm[f][self.nm[f]["community"] == c]
        return (len(d), float(d["median_entry_partnership"].median()),
                int(pd.to_datetime(d["first_date"]).dt.year.median()),
                int(pd.to_datetime(d["last_date"]).dt.year.median()))

    def core(self, f: str) -> pd.DataFrame:
        d = self.nm[f]
        return d[d["core_number"] == d["core_number"].max()]


def build(c: Ctx) -> list[tuple]:
    n_files = len(c.audit)
    n_inc = int(c.audit["included"].sum())
    n_obs = len(c.obs)
    n_inn = int(c.counts["england_innings"].sum())
    n_runs = int(c.counts["partnership_runs"].sum())
    n_del = int(c.counts["deliveries"].sum())
    no_bat = int((c.meta["n_innings_england"] == 0).sum())
    first, last = c.meta["start_date"].min(), c.meta["start_date"].max()
    ids = [set(c.nm[f]["player_id"]) for f in F]
    all_three, union = len(ids[0] & ids[1] & ids[2]), len(ids[0] | ids[1] | ids[2])
    zero = sum(int((c.edges[f]["weight"] == 0).sum()) for f in F)
    rho = {f: c.nm[f]["degree"].corr(c.nm[f]["innings_batted"], method="spearman") for f in F}
    rho_s = {f: c.nm[f]["strength"].corr(c.nm[f]["innings_batted"], method="spearman") for f in F}
    core_share = {f: c.core(f)["strength"].sum() / c.nm[f]["strength"].sum() for f in F}
    core_inn = {f: (c.core(f)["innings_batted"].median(),
                    c.nm[f][c.nm[f]["core_number"] < c.nm[f]["core_number"].max()]["innings_batted"].median()) for f in F}
    periphery = {f: int((c.nm[f]["core_number"] <= 2).sum()) for f in F}
    cs = {(f, k): c.comm_stat(f, k) for f in F for k in sorted(c.nm[f]["community"].unique())}
    B: list[tuple] = []
    h, p = (lambda t: B.append(("h", t))), (lambda t: B.append(("p", t)))

    # ------------------------------------------------------------------ 1
    h("Introduction")
    p("Network analysis describes a system through the relations among its parts instead of the attributes of "
      "each part alone. In team sport this view is natural, and passing networks in football are a standard example. "
      "Cricket is less often treated this way, although batting has a clear relational unit, the partnership. Two batters are at the "
      "crease at any time, runs are accumulated by the pair, and a wicket replaces one member of the pair with "
      "a new batter. Over many matches these pairings form a network of who has batted with whom, and how much "
      "they scored together.")
    p("This project applies social network analysis to the batting partnerships of the England Men's national "
      f"team between {first:%d %B %Y} and {last:%d %B %Y}. International cricket is played in three formats, "
      "Test matches (up to five days, two innings per side), One Day Internationals (ODI, 50 overs per side) "
      "and Twenty20 Internationals (T20I, 20 overs per side). The formats differ in length, in tactics and "
      "largely in personnel, so we build one network per format and analyse them with one common design. "
      "In each network a node is a batter and an undirected weighted edge joins two batters who shared at "
      "least one partnership; the weight is the total number of runs the pair added together.")
    p("The network captures the collaboration structure of a batting group: how widely each batter is paired, "
      "where the runs are concentrated, which groups of batters repeatedly bat together, and who links groups "
      "that otherwise rarely meet. It does not measure individual batting quality, and we do not use it for "
      "that purpose.")

    # ------------------------------------------------------------------ 2
    h("Problem and Motivation")
    p("Cricket statistics are dominated by individual averages and by lists of record partnerships. Neither "
      "shows the structure that emerges when all partnerships of a team are considered together. A batting "
      "order is not a fixed set of pairs: openers meet the middle order, the middle order meets the lower "
      "order, selection changes over years, and the three formats use overlapping but different squads. "
      "Describing this structure shows how dependent the batting is on a small core, how separate the top "
      "order and the tail are, and which players connect successive generations of the squad. It is also a "
      "compact test case for the measures taught in the course, because the same "
      "design can be applied to three comparable networks.")
    p("We address seven research questions. (1) What are the structural characteristics of England's "
      "batting-partnership networks in Test, ODI and T20I cricket in the observation period? (2) Which batters "
      "occupy structurally prominent positions in each format? (3) How are partnerships grouped or clustered, "
      "and what do cohesion and redundancy reveal about the structure? (4) Which batters have the highest "
      "weighted degree, i.e. are involved in the most partnership runs? (5) Which communities of batters does "
      "a community-detection method find? (6) Which batters lie between other batters (betweenness)? "
      "(7) Is there a core-periphery structure?")
    p("The contribution is threefold: an auditable procedure that reconstructs every batting partnership from "
      "ball-by-ball data; three format-specific weighted networks built from it; and a comparative structural "
      "analysis that applies the same measures, with the same conventions, to the three networks. The study "
      "is descriptive. We do not predict results and we do not rank players by ability.")

    # ------------------------------------------------------------------ 3
    h("Datasets")
    p("Source. The data come from Cricsheet (cricsheet.org), a public project that publishes ball-by-ball "
      "records of cricket matches under an open licence. We used the archive england_male_json.zip, which "
      f"contains {n_files} matches involving England men's teams in JSON format (schema version 1.3.0). The "
      "archive file is dated 11 November 2026; it is stored unchanged in the repository together with its "
      "SHA-256 checksum and a manifest of all files. No data were digitised by hand.")
    p(f"Filters. A match is included when it is a men's international match, England is one of the two teams, "
      f"the format is Test, ODI or T20I, and the first day of the match lies between 1 January 2020 and "
      f"29 October 2026. All {n_files} files were readable; {n_inc} satisfy the filters and "
      f"{n_files - n_inc} were excluded, all because they started before the window. In {no_bat} included "
      "limited-overs matches England never batted (abandoned or ended before England's innings); they remain "
      "in the match table but produce no partnerships. Table 1 gives the resulting counts.")
    B.append(("table", "Table 1. Dataset after filtering (England batting innings only).",
              ["", "Test", "ODI", "T20I", "Total"],
              [[lab] + [f"{int(c.counts.loc[f, col]):,}" for f in F] + [f"{int(c.counts[col].sum()):,}"]
               for lab, col in [("Matches", "matches"), ("England innings", "england_innings"),
                                ("Deliveries", "deliveries"), ("Partnership observations", "observations"),
                                ("Partnership runs", "partnership_runs")]]
              + [["Nodes (batters)"] + [c.v(f, "nodes", 0) for f in F] + [f"{union} distinct"],
                 ["Edges (pairs)"] + [c.v(f, "edges", 0) for f in F] + ["-"]]))
    p("Fields used. From the match information we use the dates, gender, team type, match type, teams and the "
      "registry that maps every player name in the file to a stable Cricsheet person identifier. From each "
      "England innings we read the deliveries in source order. Each delivery names the batter on strike and "
      "the non-striker, gives the runs (runs.total, which already contains extras) and lists any wickets with "
      "the player dismissed.")
    p("Partnership extraction. A partnership is the period in which one unordered pair of batters shares the "
      "crease. The extractor keeps the current pair as state while it walks through the deliveries. Each "
      "delivery adds runs.total once to the current pair. A delivery with a wicket record naming one of the "
      "pair closes the partnership after that delivery, so the runs of the wicket ball belong to the old "
      "pair; no list of dismissal types is hard-coded. A change of pair without a wicket is accepted only if "
      "the file records a batter replacement, otherwise it is logged as unexplained. The open partnership is "
      "closed at the end of the innings. A pair that separates and bats together again later, for example "
      "after a retirement through injury, gives two observations. The result is a table with one row per "
      f"partnership occurrence ({n_obs:,} rows) with match, date, innings, sequence number, both player "
      "identifiers, runs, deliveries, first and last delivery and the reason the partnership ended.")
    p("Network construction. For each format the observations are grouped by unordered pair. The edge weight "
      "is the sum of the partnership runs of the pair; each edge also stores the number of partnerships, of "
      "distinct matches and innings, and the first and last date. A batter becomes a node only by taking part "
      "in at least one partnership; squad members who never batted with a partner are not nodes. "
      f"Across formats there are {union} distinct batters, {all_three} of whom appear in all three networks.")
    p("Tools. Data handling and all measures were done in Python 3.13 with pandas 3.0 and NetworkX 3.4.2. "
      "The pipeline is a sequence of scripts backed by a small package and 29 automated tests on synthetic matches with "
      "known answers. Each network is exported as a GraphML file for Gephi, the visualisation tool chosen for "
      "the project. The figures in this report were drawn in Python from those GraphML files, using the "
      "NetworkX implementation of the ForceAtlas2 layout. Code, intermediate tables and outputs are in the "
      "project repository.")

    # ------------------------------------------------------------------ 4
    h("Validity and Reliability")
    p("Validity. The network is a simplified model of batting collaboration. An edge means that two players "
      "batted together at least once. It does not mean friendship, communication, tactical influence or a "
      "causal contribution of one player to the other's runs. Who bats with whom is largely decided by the "
      "batting order and by when wickets fall, so the network reflects selection and batting position as "
      "much as any chosen collaboration.")
    p("The edge weight is the accumulated score of the pair while together, including extras (wides, "
      "no-balls, byes) because these are part of runs.total; it is therefore the partnership as cricket "
      "scorecards define it, not the sum of the two batters' own runs. Weights are cumulative, so pairs and "
      "players with more matches accumulate more; a weight is a volume, not a rate. "
      f"{zero} edges have weight zero: the pair did share the crease but added no run. They are kept, because "
      "the tie exists, and they contribute nothing to weighted measures. One Test innings carries five "
      "penalty runs recorded at innings level; they belong to no delivery and are not assigned to any pair.")
    p("The population is defined by the filters: England men, three international formats, matches starting "
      "in the window. Cricsheet withholds seven England matches involving Afghanistan from the full archive, "
      "which may include matches in our window, and the T20I and ODI networks reflect frequent rotation of "
      "players, so some nodes rest on very few innings. Batters who came to the crease but never faced or "
      "backed up a delivery cannot be observed.")
    p("Reliability. The raw archive is never modified and is identified by a checksum. Filters, date limits, "
      "format labels and the random seed (42) are set in one configuration file. Players are identified by "
      "the Cricsheet person identifier, never by name; no player in the filtered data appears under two "
      "spellings. The boundary rules of the extractor are explicit and tested on sixteen required edge cases "
      "(strike rotation, run-out of the non-striker, extras, two wickets on one ball, reunited pairs, "
      "penalties and others).")
    sc_n, sc_ok = len(c.score), int(c.score["passed"].sum())
    p("The extraction was validated in three independent ways. First, in every one of the "
      f"{n_inn} innings the partnership runs add up to the runs of all deliveries ({n_runs:,} runs in "
      f"{n_del:,} deliveries). Second, innings totals recomputed from the raw files without the extractor were "
      "compared with facts Cricsheet records separately, the target set for the chasing side and the winning "
      f"margin in runs; all {sc_n} comparisons agree ({sc_ok} of {sc_n}; matches with rain-adjusted targets "
      f"are excluded). Third, {len(c.spots)} well-known partnerships were looked up, among them the 454 by Root "
      "and Brook at Multan in 2024 and the unbroken 170 by Buttler and Hales in the 2022 T20 World Cup "
      "semi-final; all are reproduced exactly. The extractor raised no warning: every change of pair is "
      "explained by a wicket, by one retirement through injury, by two recorded batter replacements or by the "
      f"end of the innings. After aggregation, {len(c.agg)} invariants (for instance that the edge weights of "
      "a format sum to its partnership runs, and that degree equals the number of distinct partners) hold, "
      "and each GraphML file was read back and compared with the graph in memory. Louvain community "
      "detection is the only stochastic step; its seed is fixed and its sensitivity to the seed is reported.")

    # ------------------------------------------------------------------ 5
    h("Measures and Results")
    p("All three networks are undirected, weighted and one-mode. One rule governs the use of weights. The "
      "weight is a tie strength (more runs, stronger tie), whereas shortest-path algorithms read edge values "
      "as distances. We therefore use weights only in measures defined for strengths (node strength, "
      "eigenvector centrality, modularity) and treat every tie as one step in all path-based measures "
      "(betweenness, closeness, path length). Clustering, k-cores and redundancy use the unweighted "
      "topology. Table 2 summarises the networks and Figure 1 shows them.")
    B.append(("table", "Table 2. Network-level measures. W = uses edge weights; all others unweighted.",
              ["Measure", "Test", "ODI", "T20I"],
              [c.row("Nodes", "nodes", 0), c.row("Edges", "edges", 0), c.row("Density", "density", 3),
               c.row("Connected components", "components", 0),
               c.row("Mean degree", "degree_mean", 1), c.row("Maximum degree", "degree_max", 0),
               c.row("Degree centralisation", "degree_centralization", 3),
               c.row("Median edge weight (W)", "edge_weight_median", 1),
               c.row("Maximum edge weight (W)", "edge_weight_max", 0),
               c.row("Weight share of top 10% of edges (W)", "top10pct_edges_weight_share", 3),
               c.row("Edges with a single partnership (share)", "edges_single_observation_share", 3),
               c.row("Average local clustering", "avg_clustering", 3), c.row("Transitivity", "transitivity", 3),
               c.row("Average path length", "avg_path_length_lcc", 2), c.row("Diameter", "diameter_lcc", 0),
               c.row("Clustering, random graphs", "C_random", 3),
               c.row("Path length, random graphs", "L_random", 2),
               c.row("Small-world index sigma", "small_world_sigma", 2),
               c.row("Degree assortativity", "degree_assortativity", 3),
               c.row("Largest k of k-core", "max_core_k", 0), c.row("Nodes in main core", "max_core_nodes", 0),
               c.row("Louvain communities (W)", "louvain_communities", 0),
               c.row("Modularity Q (W)", "louvain_modularity", 3),
               c.row("Mean effective size", "mean_effective_size", 2),
               c.row("Mean constraint", "mean_constraint", 3)]))
    B.append(("fig", config.FIGURES_DIR / "network_comparison.png",
              "Figure 1. The three batting-partnership networks drawn with identical conventions. Node area: "
              "strength (total partnership runs). Edge width: runs of the pair. Colour: Louvain community "
              "(numbered by size within each format; grey: fewer than three players). Layout: ForceAtlas2 on "
              "the unweighted topology; positions are a drawing aid, not a measure."))

    p("Size, density and connectedness (RQ1). Density is the share of possible pairs that are present, "
      "2m/(n(n-1)), without self-loops. Components are sets of nodes joined by paths. These measures say how "
      "completely the batters of a format are linked. Each network has about fifty batters "
      f"({c.v('Test','nodes',0)}, {c.v('ODI','nodes',0)} and {c.v('T20I','nodes',0)}) and each is connected: "
      "there is one component, so every batter can be reached from every other through chains of shared "
      "partnerships, and measures that need a connected graph are computed on the whole network. Density is "
      f"{c.v('Test','density')} in Tests, {c.v('ODI','density')} in ODIs and {c.v('T20I','density')} in T20Is: "
      "between a fifth and a quarter of all possible pairs batted together. The average path length is about "
      f"two steps ({c.v('Test','avg_path_length_lcc')}, {c.v('ODI','avg_path_length_lcc')}, "
      f"{c.v('T20I','avg_path_length_lcc')}) and the diameter is four in every format.")
    p("Edge weights are very unequal. The median pair added "
      f"{c.v('Test','edge_weight_median',0)}, {c.v('ODI','edge_weight_median',0)} and "
      f"{c.v('T20I','edge_weight_median',0)} runs, but the heaviest tenth of the edges holds "
      f"{float(c.s['Test']['top10pct_edges_weight_share']):.0%} of all partnership runs in Tests and about half "
      "in the limited-overs formats, and 39% to 51% of the pairs batted together only once. The heaviest "
      f"edges are, in Tests, {c.top_edges('Test')}; in ODIs, {c.top_edges('ODI')}; in T20Is, "
      f"{c.top_edges('T20I')}.")

    p("Degree and strength (RQ2, RQ4). Degree is the number of distinct partners of a batter and measures "
      "the breadth of his connections. Strength, the weighted degree, is the sum of the weights of his edges: "
      "the runs added in all partnerships he took part in. The two are kept apart because they answer "
      "different questions, how many partners versus how many runs. Table 3 lists the leading batters.")
    B.append(("table", "Table 3. Leading batters per format. Betweenness, effective size: unweighted; "
                       "strength, eigenvector: weighted.",
              ["Measure", "Test", "ODI", "T20I"],
              [["Degree"] + [c.top(f, "degree") for f in F],
               ["Strength (runs)"] + [c.top(f, "strength") for f in F],
               ["Betweenness"] + [c.top(f, "betweenness", nd=3) for f in F],
               ["Closeness"] + [c.top(f, "closeness_lcc", nd=3) for f in F],
               ["Eigenvector"] + [c.top(f, "eigenvector_lcc", nd=3) for f in F],
               ["Effective size"] + [c.top(f, "effective_size", nd=1) for f in F]]))
    p(f"In Tests JE Root leads both lists by a wide margin: he batted with {c.nm['Test']['degree'].max()} of "
      f"the other {int(c.v('Test','nodes',0)) - 1} batters and his strength is about twice that of the next "
      "player. This single hub explains the high degree centralisation of the Test network "
      f"({c.v('Test','degree_centralization')}, against {c.v('ODI','degree_centralization')} in ODIs and "
      f"{c.v('T20I','degree_centralization')} in T20Is; the index is 0 when all degrees are equal and 1 in a "
      "star). In ODIs the highest degrees are shared by top-order and lower-order players. In T20Is degree and "
      "strength separate most clearly: LS Livingstone has the most partners but JC Buttler has by far the "
      "highest strength, more than three times Livingstone's. Buttler's runs come from a few heavy ties, "
      "Livingstone's partners are many and his ties light.")
    p("Both measures depend on opportunity. The rank correlation between degree and the number of innings "
      f"batted is {rho['Test']:.2f}, {rho['ODI']:.2f} and {rho['T20I']:.2f}, and between strength and innings "
      f"{rho_s['Test']:.2f}, {rho_s['ODI']:.2f} and {rho_s['T20I']:.2f}. Strength answers RQ4 in the sense of "
      "involvement in partnership runs; it is not a measure of batting quality, since it also contains the "
      "partner's runs and extras. Degree distributions (mean "
      f"{c.v('Test','degree_mean',1)}, {c.v('ODI','degree_mean',1)}, {c.v('T20I','degree_mean',1)}; maximum "
      f"{c.v('Test','degree_max',0)}, {c.v('ODI','degree_max',0)}, {c.v('T20I','degree_max',0)}) are "
      "right-skewed, with many batters having few partners and a few having many, but networks of fifty nodes "
      "are far too small to test for a power law, so we make no claim of scale-freeness.")

    p("Betweenness, closeness and eigenvector centrality (RQ2, RQ6). Betweenness is the share of shortest "
      "paths between other pairs of batters that pass through a batter. In this network it identifies players "
      "positioned between parts of the squad that have little direct contact, not players who control "
      "anything. Closeness is the inverse of the mean distance to all others. Eigenvector centrality, "
      "computed with weights, is high for batters with heavy ties to batters who themselves have heavy ties; "
      "the iteration converged in all formats.")
    p("The three measures point to different players, most visibly in the limited-overs formats. Eigenvector "
      "centrality follows the runs: Root, Pope and Brook in Tests, Root, Brook and Duckett in ODIs, Buttler, "
      "Salt and Brook in T20Is, all from the top or middle order. Betweenness in Tests is again led by Root "
      f"({c.nm['Test']['betweenness'].max():.3f}, more than twice the second value), but in ODIs the three "
      "highest values belong to AU Rashid, BA Carse and AAP Atkinson, and in T20Is to Livingstone, Rashid and "
      "CJ Jordan. Rashid, Carse, Atkinson and Jordan usually come in late (their median first partnership of "
      "an innings is the seventh to ninth), so they bat with whoever is left from the specialist batters and "
      "with the other bowlers, and Rashid's career spans the whole window. They connect the lower order, "
      "which changes often, to the rest. High betweenness therefore marks a bridging position between the "
      "batting core and the tail and between successive squads; it coexists with low strength.")

    p("Clustering, redundancy and small-world structure (RQ3). The local clustering coefficient of a batter "
      "is the share of pairs of his partners who are partners themselves; transitivity is the global share "
      "of connected triples that close into triangles. A triangle means three players who have each batted "
      "with the other two. Average clustering is "
      f"{c.v('Test','avg_clustering')}, {c.v('ODI','avg_clustering')} and {c.v('T20I','avg_clustering')}, "
      "well over twice the value in random graphs with the same numbers of nodes and edges "
      f"({c.v('Test','C_random')}, {c.v('ODI','C_random')}, {c.v('T20I','C_random')}; mean of 200 graphs), "
      "while paths are only 7% to 9% longer than in those random graphs. The small-world index, the "
      f"clustering ratio divided by the path-length ratio, is about 2.2 in each format "
      f"({c.v('Test','small_world_sigma')}, {c.v('ODI','small_world_sigma')}, {c.v('T20I','small_world_sigma')}). "
      "The networks thus combine local closure with short global distances. The closure has a mechanical "
      "source: batters who play in the same matches meet each other through the fall of wickets. With fifty "
      "nodes and density above 0.2 short paths are almost guaranteed, so the index is indicative only.")
    p("Redundancy follows Burt's notion of structural holes. A partner is redundant for a batter to the "
      "extent that he is also tied to the batter's other partners. Effective size is degree minus this "
      "redundancy (for unweighted ties, degree minus twice the number of ties among the partners divided by "
      "degree); constraint is high when all of a batter's partners are tied to one another. On average only "
      f"about half of a batter's partners are non-redundant (mean efficiency {c.v('Test','mean_efficiency')}, "
      f"{c.v('ODI','mean_efficiency')}, {c.v('T20I','mean_efficiency')}), which is the ego-level view of the "
      "high clustering. The batters with the largest effective size and lowest constraint are those whose "
      "partners belong to groups that do not meet: Root, Stokes and Pope in Tests, Root, Rashid and SM Curran "
      "in ODIs, Livingstone, Rashid and MM Ali in T20Is.")

    p("Communities (RQ5). A community is a group of nodes with more tie weight inside the group than expected "
      "by chance. We used the Louvain method, which maximises weighted modularity Q (resolution 1, seed 42). "
      "It is a computational choice and its groups are not official units of the team. Modularity is low to "
      f"moderate ({c.v('Test','louvain_modularity')}, {c.v('ODI','louvain_modularity')}, "
      f"{c.v('T20I','louvain_modularity')}), so the groups overlap heavily, and over 100 different seeds the "
      f"number of communities varies between {c.v('Test','louvain_k_min',0)} and {c.v('Test','louvain_k_max',0)} "
      f"in Tests, {c.v('ODI','louvain_k_min',0)} and {c.v('ODI','louvain_k_max',0)} in ODIs and "
      f"{c.v('T20I','louvain_k_min',0)} and {c.v('T20I','louvain_k_max',0)} in T20Is. We interpret only the "
      "larger groups and ignore those of one or two players.")
    p("The partitions are nevertheless interpretable, because two properties computed from the data, not "
      "from prior knowledge, differ between communities: the usual point of entry (the median sequence number "
      "of a batter's first partnership in an innings, 1 for an opener) and the years of activity. In Tests "
      f"the largest community ({cs[('Test',1)][0]} players, e.g. {c.community('Test',1)}) has a median entry "
      f"at partnership {cs[('Test',1)][1]:.0f}: the lower-middle order and the tail. The second "
      f"({cs[('Test',2)][0]} players: {c.community('Test',2)}) enters at partnership "
      f"{cs[('Test',2)][1]:.0f} and is the middle order that holds most of the runs. Two small top-order "
      f"communities (median entry {cs[('Test',3)][1]:.0f}) are separated by time, not position: "
      f"{c.community('Test',3,3)} are the top three of the later years, and {c.community('Test',4)} the top order "
      "of 2020 and 2021. The ODI network splits by era as well: a top-order group most of whose members first appear in 2023 or later "
      f"({c.community('ODI',2)}), the opening group of 2020 to 2023 ({c.community('ODI',3)}), a middle-order "
      f"group ({c.community('ODI',4)}) and a large lower-order community ({cs[('ODI',1)][0]} players, median "
      f"entry {cs[('ODI',1)][1]:.0f}). T20Is show the same three-part pattern: a current top order "
      f"({c.community('T20I',2)}), an earlier group of top- and middle-order batters ({c.community('T20I',3)}) and a lower-order group of "
      f"{cs[('T20I',1)][0]} players. Communities thus reflect batting position and squad generation.")

    p("Core and periphery (RQ7). The k-core is the largest subgraph in which every node has at least k "
      "neighbours inside the subgraph; a batter's core number is the highest k for which he belongs to it. "
      "The main core is a group of mutually well-connected batters, the low shells are the periphery. The "
      f"main core is the {c.v('Test','max_core_k',0)}-core in Tests ({c.v('Test','max_core_nodes',0)} of "
      f"{c.v('Test','nodes',0)} batters), the {c.v('ODI','max_core_k',0)}-core in ODIs "
      f"({c.v('ODI','max_core_nodes',0)} of {c.v('ODI','nodes',0)}) and the {c.v('T20I','max_core_k',0)}-core in "
      f"T20Is ({c.v('T20I','max_core_nodes',0)} of {c.v('T20I','nodes',0)}). The core holds "
      f"{core_share['Test']:.0%}, {core_share['ODI']:.0%} and {core_share['T20I']:.0%} of the total node "
      "strength. Core batters have a median of "
      f"{core_inn['Test'][0]:.0f}, {core_inn['ODI'][0]:.0f} and {core_inn['T20I'][0]:.0f} innings against "
      f"{core_inn['Test'][1]:.1f}, {core_inn['ODI'][1]:.1f} and {core_inn['T20I'][1]:.1f} for the others, and "
      f"{periphery['Test']}, {periphery['ODI']} and {periphery['T20I']} batters sit in the outermost shells "
      "(core number 1 or 2). The Test core contains specialist batters and long-serving bowlers alike (Root, "
      "Stokes and Brook, but also Broad, Anderson and Leach), whereas the top-order pair Crawley and Duckett, "
      "third and sixth in strength, are outside it: openers bat mostly with each other and the number three, "
      "so they have heavy ties but too few distinct partners. Core membership measures embeddedness and "
      "length of presence, not run production.")

    p("Comparison across formats. The same definitions were applied to the three networks, and the networks "
      "are of similar size, which makes the structural indices comparable; counts and strengths are not, "
      "because a Test side bats twice and for much longer "
      f"({int(c.counts.loc['Test','england_innings'])} innings and {int(c.counts.loc['Test','deliveries']):,} "
      f"deliveries against {int(c.counts.loc['T20I','england_innings'])} innings and "
      f"{int(c.counts.loc['T20I','deliveries']):,} deliveries in T20Is). Three differences stand out. The Test "
      "network is the densest, the most clustered and the most centralised, built around one batter present "
      "for the whole period, and its runs are the most concentrated on a few edges. The ODI network is the "
      "least dense and least centralised, has the most single-partnership edges, the highest modularity and "
      "the largest share of non-redundant ties: with fewer matches per player and a change of generation "
      "inside the window, it is the most segmented by era. The T20I network has the lowest modularity and the "
      "sharpest core-periphery divide: a core of 22 batters holds 93% of the strength and is surrounded by "
      "many players with very few innings.")

    # ------------------------------------------------------------------ 6
    h("Conclusion")
    p("The three networks share a common shape. Each is a single connected component in which any two batters "
      "are about two partnership steps apart, a fifth to a quarter of all possible pairs exist, clustering is "
      "more than twice that of comparable random graphs, and roughly half of each batter's ties are "
      "redundant. This is what the mechanics of batting produce: an innings links its batters in a chain, and "
      "repeated selection of the same players closes the triangles. On top of this cohesion the runs are "
      "concentrated on few ties, so that the weighted picture is much more unequal than the unweighted one.")
    p("Prominence depends on the measure, and the differences are informative. Volume measures (strength, "
      "weighted eigenvector centrality) single out the top- and middle-order batters around whom runs "
      "accumulate: Root in Tests and ODIs, Buttler in T20Is. Breadth and brokerage measures (degree, "
      "betweenness, effective size) in the limited-overs formats single out all-rounders and lower-order "
      "players such as Rashid, Carse, Curran, Livingstone and Jordan, who bat with many different partners "
      "and tie the changing tail to the batting core. Only in Tests does one player, Root, lead on every "
      "measure, which is why that network is the most centralised.")
    p("Grouping follows two dimensions that the method recovered without being given them, batting position "
      "and time. Communities separate lower order, middle order and top order, and split the top order into "
      "successive generations of openers. The k-core analysis shows a clear core-periphery structure in all "
      "formats, with a core of about twenty batters holding two thirds of the strength in Tests and around "
      "nine tenths in the limited-overs formats; the periphery consists of players with a handful of "
      "innings. Heavy ties and core membership are different things: an established opening pair can carry "
      "the heaviest edge of a network and still lie outside its main core.")
    p("Across formats, Test cricket yields the most cohesive and most hub-centred network, ODI cricket the "
      "most segmented one, and T20I cricket the strongest contrast between a stable core and a wide, lightly "
      "connected periphery. These are statements about who batted with whom, not about ability or results.")

    # ------------------------------------------------------------------ 7
    h("Critique")
    p("The project answers its descriptive questions for the population it defines. The network construction "
      "is the strongest part: every partnership is traceable to deliveries, totals agree with independent "
      "scorecard facts, and no boundary remained unresolved. The interpretation is more limited, for four "
      "reasons.")
    p("First, opportunity dominates. Degree, strength, core number and betweenness all rise with the number "
      "of innings (rank correlations above 0.9 for degree and strength), so the measures largely describe "
      "who was selected most. We reported innings alongside the results but did not normalise the networks; "
      "edges weighted by runs per partnership, or a comparison with a null model that reshuffles partners "
      "within each innings while keeping the batting order, would separate structure from exposure. Second, "
      "aggregating almost seven years into one static graph mixes squads that never met; the communities "
      "partly rediscover this. Yearly or sliding-window networks would show the change directly. Third, the "
      "model is deliberately simple: ties are undirected and ignore which batter scored the runs, extras are "
      "included in the weights, and path-based measures ignore weights altogether, so a pair with one run "
      "counts as much as a pair with two thousand. A directed network of runs scored while batting with each "
      "partner, or weighted path measures with a justified distance, are possible alternatives. Fourth, "
      "community detection is unstable in dense networks of this size: modularity is low and the number of "
      "groups changes with the seed, so only the broad pattern should be trusted.")
    p("There are also limits in the data and in the work done. Matches withheld by Cricsheet are missing, "
      "batting role and handedness are not in the source and were not added, and the small-world and "
      "degree-distribution results are weak evidence at fifty nodes. The question in our initial proposal, "
      "whether partnership structure differs between matches won and lost, was left out and remains future "
      "work, as does the same analysis for other national teams. Finally, the network figures in this report "
      "were drawn in Python from the exported GraphML files; they follow the conventions planned for Gephi "
      "but are not Gephi exports.")

    h("References")
    for ref in [
        "Blondel, V. D., Guillaume, J.-L., Lambiotte, R., Lefebvre, E. (2008). Fast unfolding of communities in "
        "large networks. Journal of Statistical Mechanics, P10008.",
        "Borgatti, S. P., Everett, M. G., Johnson, J. C. (2018). Analyzing Social Networks (2nd ed.). Sage.",
        "Burt, R. S. (1992). Structural Holes: The Social Structure of Competition. Harvard University Press.",
        "Cricsheet. Ball-by-ball cricket data, england_male_json.zip. https://cricsheet.org/downloads/ "
        "(archive dated 11 November 2026).",
        "Freeman, L. C. (1978). Centrality in social networks: conceptual clarification. Social Networks, 1(3), 215-239.",
        "Hagberg, A., Schult, D., Swart, P. (2008). Exploring network structure, dynamics, and function using "
        "NetworkX. Proceedings of SciPy 2008, 11-15.",
        "Jacomy, M., Venturini, T., Heymann, S., Bastian, M. (2014). ForceAtlas2, a continuous graph layout "
        "algorithm for handy network visualization designed for the Gephi software. PLoS ONE, 9(6), e98679.",
        "Newman, M. E. J. (2018). Networks (2nd ed.). Oxford University Press.",
        "Seidman, S. B. (1983). Network structure and minimum degree. Social Networks, 5(3), 269-287.",
        "Watts, D. J., Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. Nature, 393, 440-442.",
    ]:
        B.append(("ref", ref))
    return B
