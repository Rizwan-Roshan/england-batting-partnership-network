# The Partnership Effect: Batting-Partnership Networks of the England Men's Cricket Team in Test, ODI and T20I Cricket (2020-2026)

Hafiz Muhammad Mutahhir Khan, Degree Programme, ID number (matricola)  
Saidatta Nagesh Musale, Degree Programme, ID number (matricola)  
Mohamed Rizwan Roshan Raja Mohamed, Degree Programme, ID number (matricola)  
Saad Salman, Degree Programme, ID number (matricola)  

## Introduction

Network analysis describes a system through the relations among its parts instead of the attributes of each part alone. In team sport this view is natural, and passing networks in football are a standard example. Cricket is less often treated this way, although batting has a clear relational unit, the partnership. Two batters are at the crease at any time, runs are accumulated by the pair, and a wicket replaces one member of the pair with a new batter. Over many matches these pairings form a network of who has batted with whom, and how much they scored together.

This project applies social network analysis to the batting partnerships of the England Men's national team between 03 January 2020 and 29 October 2026. International cricket is played in three formats, Test matches (up to five days, two innings per side), One Day Internationals (ODI, 50 overs per side) and Twenty20 Internationals (T20I, 20 overs per side). The formats differ in length, in tactics and largely in personnel, so we build one network per format and analyse them with one common design. In each network a node is a batter and an undirected weighted edge joins two batters who shared at least one partnership; the weight is the total number of runs the pair added together.

The network captures the collaboration structure of a batting group: how widely each batter is paired, where the runs are concentrated, which groups of batters repeatedly bat together, and who links groups that otherwise rarely meet. It does not measure individual batting quality, and we do not use it for that purpose.

## Problem and Motivation

Cricket statistics are dominated by individual averages and by lists of record partnerships. Neither shows the structure that emerges when all partnerships of a team are considered together. A batting order is not a fixed set of pairs: openers meet the middle order, the middle order meets the lower order, selection changes over years, and the three formats use overlapping but different squads. Describing this structure shows how dependent the batting is on a small core, how separate the top order and the tail are, and which players connect successive generations of the squad. It is also a compact test case for the measures taught in the course, because the same design can be applied to three comparable networks.

We address seven research questions. (1) What are the structural characteristics of England's batting-partnership networks in Test, ODI and T20I cricket in the observation period? (2) Which batters occupy structurally prominent positions in each format? (3) How are partnerships grouped or clustered, and what do cohesion and redundancy reveal about the structure? (4) Which batters have the highest weighted degree, i.e. are involved in the most partnership runs? (5) Which communities of batters does a community-detection method find? (6) Which batters lie between other batters (betweenness)? (7) Is there a core-periphery structure?

The contribution is threefold: an auditable procedure that reconstructs every batting partnership from ball-by-ball data; three format-specific weighted networks built from it; and a comparative structural analysis that applies the same measures, with the same conventions, to the three networks. The study is descriptive. We do not predict results and we do not rank players by ability.

## Datasets

Source. The data come from Cricsheet (cricsheet.org), a public project that publishes ball-by-ball records of cricket matches under an open licence. We used the archive england_male_json.zip, which contains 961 matches involving England men's teams in JSON format (schema version 1.3.0). The archive file is dated 11 November 2026; it is stored unchanged in the repository together with its SHA-256 checksum and a manifest of all files. No data were digitised by hand.

Filters. A match is included when it is a men's international match, England is one of the two teams, the format is Test, ODI or T20I, and the first day of the match lies between 1 January 2020 and 29 October 2026. All 961 files were readable; 287 satisfy the filters and 674 were excluded, all because they started before the window. In 7 included limited-overs matches England never batted (abandoned or ended before England's innings); they remain in the match table but produce no partnerships. Table 1 gives the resulting counts.

**Table 1. Dataset after filtering (England batting innings only).**

|  | Test | ODI | T20I | Total |
|---|---|---|---|---|
| Matches | 81 | 88 | 118 | 287 |
| England innings | 151 | 85 | 114 | 350 |
| Deliveries | 66,829 | 22,766 | 12,878 | 102,473 |
| Partnership observations | 1,357 | 708 | 763 | 2,828 |
| Partnership runs | 43,080 | 22,929 | 18,974 | 84,983 |
| Nodes (batters) | 51 | 50 | 44 | 73 distinct |
| Edges (pairs) | 335 | 262 | 222 | - |

Fields used. From the match information we use the dates, gender, team type, match type, teams and the registry that maps every player name in the file to a stable Cricsheet person identifier. From each England innings we read the deliveries in source order. Each delivery names the batter on strike and the non-striker, gives the runs (runs.total, which already contains extras) and lists any wickets with the player dismissed.

Partnership extraction. A partnership is the period in which one unordered pair of batters shares the crease. The extractor keeps the current pair as state while it walks through the deliveries. Each delivery adds runs.total once to the current pair. A delivery with a wicket record naming one of the pair closes the partnership after that delivery, so the runs of the wicket ball belong to the old pair; no list of dismissal types is hard-coded. A change of pair without a wicket is accepted only if the file records a batter replacement, otherwise it is logged as unexplained. The open partnership is closed at the end of the innings. A pair that separates and bats together again later, for example after a retirement through injury, gives two observations. The result is a table with one row per partnership occurrence (2,828 rows) with match, date, innings, sequence number, both player identifiers, runs, deliveries, first and last delivery and the reason the partnership ended.

Network construction. For each format the observations are grouped by unordered pair. The edge weight is the sum of the partnership runs of the pair; each edge also stores the number of partnerships, of distinct matches and innings, and the first and last date. A batter becomes a node only by taking part in at least one partnership; squad members who never batted with a partner are not nodes. Across formats there are 73 distinct batters, 26 of whom appear in all three networks.

Tools. Data handling and all measures were done in Python 3.13 with pandas 3.0 and NetworkX 3.4.2. The pipeline is a sequence of scripts backed by a small package and 29 automated tests on synthetic matches with known answers. Each network is exported as a GraphML file for Gephi, the visualisation tool chosen for the project. The figures in this report were drawn in Python from those GraphML files, using the NetworkX implementation of the ForceAtlas2 layout. Code, intermediate tables and outputs are in the project repository.

## Validity and Reliability

Validity. The network is a simplified model of batting collaboration. An edge means that two players batted together at least once. It does not mean friendship, communication, tactical influence or a causal contribution of one player to the other's runs. Who bats with whom is largely decided by the batting order and by when wickets fall, so the network reflects selection and batting position as much as any chosen collaboration.

The edge weight is the accumulated score of the pair while together, including extras (wides, no-balls, byes) because these are part of runs.total; it is therefore the partnership as cricket scorecards define it, not the sum of the two batters' own runs. Weights are cumulative, so pairs and players with more matches accumulate more; a weight is a volume, not a rate. 30 edges have weight zero: the pair did share the crease but added no run. They are kept, because the tie exists, and they contribute nothing to weighted measures. One Test innings carries five penalty runs recorded at innings level; they belong to no delivery and are not assigned to any pair.

The population is defined by the filters: England men, three international formats, matches starting in the window. Cricsheet withholds seven England matches involving Afghanistan from the full archive, which may include matches in our window, and the T20I and ODI networks reflect frequent rotation of players, so some nodes rest on very few innings. Batters who came to the crease but never faced or backed up a delivery cannot be observed.

Reliability. The raw archive is never modified and is identified by a checksum. Filters, date limits, format labels and the random seed (42) are set in one configuration file. Players are identified by the Cricsheet person identifier, never by name; no player in the filtered data appears under two spellings. The boundary rules of the extractor are explicit and tested on sixteen required edge cases (strike rotation, run-out of the non-striker, extras, two wickets on one ball, reunited pairs, penalties and others).

The extraction was validated in three independent ways. First, in every one of the 350 innings the partnership runs add up to the runs of all deliveries (84,983 runs in 102,473 deliveries). Second, innings totals recomputed from the raw files without the extractor were compared with facts Cricsheet records separately, the target set for the chasing side and the winning margin in runs; all 318 comparisons agree (318 of 318; matches with rain-adjusted targets are excluded). Third, 5 well-known partnerships were looked up, among them the 454 by Root and Brook at Multan in 2024 and the unbroken 170 by Buttler and Hales in the 2022 T20 World Cup semi-final; all are reproduced exactly. The extractor raised no warning: every change of pair is explained by a wicket, by one retirement through injury, by two recorded batter replacements or by the end of the innings. After aggregation, 36 invariants (for instance that the edge weights of a format sum to its partnership runs, and that degree equals the number of distinct partners) hold, and each GraphML file was read back and compared with the graph in memory. Louvain community detection is the only stochastic step; its seed is fixed and its sensitivity to the seed is reported.

## Measures and Results

All three networks are undirected, weighted and one-mode. One rule governs the use of weights. The weight is a tie strength (more runs, stronger tie), whereas shortest-path algorithms read edge values as distances. We therefore use weights only in measures defined for strengths (node strength, eigenvector centrality, modularity) and treat every tie as one step in all path-based measures (betweenness, closeness, path length). Clustering, k-cores and redundancy use the unweighted topology. Table 2 summarises the networks and Figure 1 shows them.

**Table 2. Network-level measures. W = uses edge weights; all others unweighted.**

| Measure | Test | ODI | T20I |
|---|---|---|---|
| Nodes | 51 | 50 | 44 |
| Edges | 335 | 262 | 222 |
| Density | 0.263 | 0.214 | 0.235 |
| Connected components | 1 | 1 | 1 |
| Mean degree | 13.1 | 10.5 | 10.1 |
| Maximum degree | 38 | 24 | 27 |
| Degree centralisation | 0.518 | 0.287 | 0.412 |
| Median edge weight (W) | 42.0 | 40.0 | 30.5 |
| Maximum edge weight (W) | 2,697 | 953 | 1,397 |
| Weight share of top 10% of edges (W) | 0.627 | 0.487 | 0.502 |
| Edges with a single partnership (share) | 0.391 | 0.508 | 0.405 |
| Average local clustering | 0.616 | 0.527 | 0.549 |
| Transitivity | 0.517 | 0.467 | 0.502 |
| Average path length | 1.89 | 2.04 | 1.96 |
| Diameter | 4 | 4 | 4 |
| Clustering, random graphs | 0.262 | 0.214 | 0.236 |
| Path length, random graphs | 1.76 | 1.87 | 1.83 |
| Small-world index sigma | 2.19 | 2.25 | 2.18 |
| Degree assortativity | -0.164 | -0.057 | -0.178 |
| Largest k of k-core | 11 | 9 | 8 |
| Nodes in main core | 20 | 23 | 22 |
| Louvain communities (W) | 5 | 4 | 4 |
| Modularity Q (W) | 0.224 | 0.289 | 0.188 |
| Mean effective size | 6.29 | 5.75 | 5.14 |
| Mean constraint | 0.247 | 0.275 | 0.306 |

![Figure 1.](../outputs/figures/network_comparison.png)

*Figure 1. The three batting-partnership networks drawn with identical conventions. Node area: strength (total partnership runs). Edge width: runs of the pair. Colour: Louvain community (numbered by size within each format; grey: fewer than three players). Layout: ForceAtlas2 on the unweighted topology; positions are a drawing aid, not a measure.*

Size, density and connectedness (RQ1). Density is the share of possible pairs that are present, 2m/(n(n-1)), without self-loops. Components are sets of nodes joined by paths. These measures say how completely the batters of a format are linked. Each network has about fifty batters (51, 50 and 44) and each is connected: there is one component, so every batter can be reached from every other through chains of shared partnerships, and measures that need a connected graph are computed on the whole network. Density is 0.26 in Tests, 0.21 in ODIs and 0.23 in T20Is: between a fifth and a quarter of all possible pairs batted together. The average path length is about two steps (1.89, 2.04, 1.96) and the diameter is four in every format.

Edge weights are very unequal. The median pair added 42, 40 and 30 runs, but the heaviest tenth of the edges holds 63% of all partnership runs in Tests and about half in the limited-overs formats, and 39% to 51% of the pairs batted together only once. The heaviest edges are, in Tests, BM Duckett-Z Crawley (2,697 runs in 65 partnerships); HC Brook-JE Root (2,566 runs in 43 partnerships); in ODIs, HC Brook-JE Root (953 runs in 22 partnerships); BM Duckett-JE Root (769 runs in 17 partnerships); in T20Is, PD Salt-JC Buttler (1,397 runs in 40 partnerships); JC Buttler-DJ Malan (793 runs in 16 partnerships).

Degree and strength (RQ2, RQ4). Degree is the number of distinct partners of a batter and measures the breadth of his connections. Strength, the weighted degree, is the sum of the weights of his edges: the runs added in all partnerships he took part in. The two are kept apart because they answer different questions, how many partners versus how many runs. Table 3 lists the leading batters.

**Table 3. Leading batters per format. Betweenness, effective size: unweighted; strength, eigenvector: weighted.**

| Measure | Test | ODI | T20I |
|---|---|---|---|
| Degree | JE Root (38), BA Stokes (31), OJ Pope (30) | JE Root (24), AU Rashid (23), JC Buttler (23) | LS Livingstone (27), MM Ali (23), SM Curran (23) |
| Strength (runs) | JE Root (15,303), OJ Pope (7,568), Z Crawley (7,328) | JE Root (4,837), BM Duckett (3,716), JC Buttler (3,590) | JC Buttler (6,281), PD Salt (3,915), HC Brook (3,372) |
| Betweenness | JE Root (0.166), HC Brook (0.075), BA Stokes (0.066) | AU Rashid (0.117), BA Carse (0.116), AAP Atkinson (0.083) | LS Livingstone (0.148), AU Rashid (0.144), CJ Jordan (0.099) |
| Closeness | JE Root (0.806), OJ Pope (0.704), BA Stokes (0.694) | AU Rashid (0.645), JE Root (0.645), JC Buttler (0.628) | LS Livingstone (0.729), SM Curran (0.683), MM Ali (0.662) |
| Eigenvector | JE Root (0.545), OJ Pope (0.387), HC Brook (0.359) | JE Root (0.487), HC Brook (0.407), BM Duckett (0.371) | JC Buttler (0.567), PD Salt (0.447), HC Brook (0.349) |
| Effective size | JE Root (25.0), BA Stokes (18.7), OJ Pope (17.6) | JE Root (15.2), AU Rashid (14.5), SM Curran (14.2) | LS Livingstone (17.3), AU Rashid (14.5), MM Ali (14.0) |

In Tests JE Root leads both lists by a wide margin: he batted with 38 of the other 50 batters and his strength is about twice that of the next player. This single hub explains the high degree centralisation of the Test network (0.52, against 0.29 in ODIs and 0.41 in T20Is; the index is 0 when all degrees are equal and 1 in a star). In ODIs the highest degrees are shared by top-order and lower-order players. In T20Is degree and strength separate most clearly: LS Livingstone has the most partners but JC Buttler has by far the highest strength, more than three times Livingstone's. Buttler's runs come from a few heavy ties, Livingstone's partners are many and his ties light.

Both measures depend on opportunity. The rank correlation between degree and the number of innings batted is 0.93, 0.93 and 0.94, and between strength and innings 0.91, 0.91 and 0.94. Strength answers RQ4 in the sense of involvement in partnership runs; it is not a measure of batting quality, since it also contains the partner's runs and extras. Degree distributions (mean 13.1, 10.5, 10.1; maximum 38, 24, 27) are right-skewed, with many batters having few partners and a few having many, but networks of fifty nodes are far too small to test for a power law, so we make no claim of scale-freeness.

Betweenness, closeness and eigenvector centrality (RQ2, RQ6). Betweenness is the share of shortest paths between other pairs of batters that pass through a batter. In this network it identifies players positioned between parts of the squad that have little direct contact, not players who control anything. Closeness is the inverse of the mean distance to all others. Eigenvector centrality, computed with weights, is high for batters with heavy ties to batters who themselves have heavy ties; the iteration converged in all formats.

The three measures point to different players, most visibly in the limited-overs formats. Eigenvector centrality follows the runs: Root, Pope and Brook in Tests, Root, Brook and Duckett in ODIs, Buttler, Salt and Brook in T20Is, all from the top or middle order. Betweenness in Tests is again led by Root (0.166, more than twice the second value), but in ODIs the three highest values belong to AU Rashid, BA Carse and AAP Atkinson, and in T20Is to Livingstone, Rashid and CJ Jordan. Rashid, Carse, Atkinson and Jordan usually come in late (their median first partnership of an innings is the seventh to ninth), so they bat with whoever is left from the specialist batters and with the other bowlers, and Rashid's career spans the whole window. They connect the lower order, which changes often, to the rest. High betweenness therefore marks a bridging position between the batting core and the tail and between successive squads; it coexists with low strength.

Clustering, redundancy and small-world structure (RQ3). The local clustering coefficient of a batter is the share of pairs of his partners who are partners themselves; transitivity is the global share of connected triples that close into triangles. A triangle means three players who have each batted with the other two. Average clustering is 0.62, 0.53 and 0.55, well over twice the value in random graphs with the same numbers of nodes and edges (0.26, 0.21, 0.24; mean of 200 graphs), while paths are only 7% to 9% longer than in those random graphs. The small-world index, the clustering ratio divided by the path-length ratio, is about 2.2 in each format (2.19, 2.25, 2.18). The networks thus combine local closure with short global distances. The closure has a mechanical source: batters who play in the same matches meet each other through the fall of wickets. With fifty nodes and density above 0.2 short paths are almost guaranteed, so the index is indicative only.

Redundancy follows Burt's notion of structural holes. A partner is redundant for a batter to the extent that he is also tied to the batter's other partners. Effective size is degree minus this redundancy (for unweighted ties, degree minus twice the number of ties among the partners divided by degree); constraint is high when all of a batter's partners are tied to one another. On average only about half of a batter's partners are non-redundant (mean efficiency 0.47, 0.56, 0.54), which is the ego-level view of the high clustering. The batters with the largest effective size and lowest constraint are those whose partners belong to groups that do not meet: Root, Stokes and Pope in Tests, Root, Rashid and SM Curran in ODIs, Livingstone, Rashid and MM Ali in T20Is.

Communities (RQ5). A community is a group of nodes with more tie weight inside the group than expected by chance. We used the Louvain method, which maximises weighted modularity Q (resolution 1, seed 42). It is a computational choice and its groups are not official units of the team. Modularity is low to moderate (0.22, 0.29, 0.19), so the groups overlap heavily, and over 100 different seeds the number of communities varies between 4 and 6 in Tests, 3 and 4 in ODIs and 4 and 5 in T20Is. We interpret only the larger groups and ignore those of one or two players.

The partitions are nevertheless interpretable, because two properties computed from the data, not from prior knowledge, differ between communities: the usual point of entry (the median sequence number of a batter's first partnership in an innings, 1 for an opener) and the years of activity. In Tests the largest community (24 players, e.g. JL Smith, CR Woakes, JC Buttler, AAP Atkinson) has a median entry at partnership 8: the lower-middle order and the tail. The second (14 players: JE Root, BA Stokes, HC Brook, JM Bairstow) enters at partnership 5 and is the middle order that holds most of the runs. Two small top-order communities (median entry 1) are separated by time, not position: OJ Pope, Z Crawley, BM Duckett are the top three of the later years, and DP Sibley, RJ Burns, H Hameed, JL Denly the top order of 2020 and 2021. The ODI network splits by era as well: a top-order group most of whose members first appear in 2023 or later (JE Root, BM Duckett, HC Brook, WG Jacks), the opening group of 2020 to 2023 (JM Bairstow, PD Salt, JJ Roy, SW Billings), a middle-order group (JC Buttler, DJ Malan, LS Livingstone, SM Curran) and a large lower-order community (19 players, median entry 9). T20Is show the same three-part pattern: a current top order (JC Buttler, PD Salt, HC Brook, JG Bethell), an earlier group of top- and middle-order batters (DJ Malan, JM Bairstow, MM Ali, JJ Roy) and a lower-order group of 23 players. Communities thus reflect batting position and squad generation.

Core and periphery (RQ7). The k-core is the largest subgraph in which every node has at least k neighbours inside the subgraph; a batter's core number is the highest k for which he belongs to it. The main core is a group of mutually well-connected batters, the low shells are the periphery. The main core is the 11-core in Tests (20 of 51 batters), the 9-core in ODIs (23 of 50) and the 8-core in T20Is (22 of 44). The core holds 66%, 87% and 93% of the total node strength. Core batters have a median of 41, 29 and 32 innings against 10.0, 5.0 and 4.5 for the others, and 5, 6 and 6 batters sit in the outermost shells (core number 1 or 2). The Test core contains specialist batters and long-serving bowlers alike (Root, Stokes and Brook, but also Broad, Anderson and Leach), whereas the top-order pair Crawley and Duckett, third and sixth in strength, are outside it: openers bat mostly with each other and the number three, so they have heavy ties but too few distinct partners. Core membership measures embeddedness and length of presence, not run production.

Comparison across formats. The same definitions were applied to the three networks, and the networks are of similar size, which makes the structural indices comparable; counts and strengths are not, because a Test side bats twice and for much longer (151 innings and 66,829 deliveries against 114 innings and 12,878 deliveries in T20Is). Three differences stand out. The Test network is the densest, the most clustered and the most centralised, built around one batter present for the whole period, and its runs are the most concentrated on a few edges. The ODI network is the least dense and least centralised, has the most single-partnership edges, the highest modularity and the largest share of non-redundant ties: with fewer matches per player and a change of generation inside the window, it is the most segmented by era. The T20I network has the lowest modularity and the sharpest core-periphery divide: a core of 22 batters holds 93% of the strength and is surrounded by many players with very few innings.

## Conclusion

The three networks share a common shape. Each is a single connected component in which any two batters are about two partnership steps apart, a fifth to a quarter of all possible pairs exist, clustering is more than twice that of comparable random graphs, and roughly half of each batter's ties are redundant. This is what the mechanics of batting produce: an innings links its batters in a chain, and repeated selection of the same players closes the triangles. On top of this cohesion the runs are concentrated on few ties, so that the weighted picture is much more unequal than the unweighted one.

Prominence depends on the measure, and the differences are informative. Volume measures (strength, weighted eigenvector centrality) single out the top- and middle-order batters around whom runs accumulate: Root in Tests and ODIs, Buttler in T20Is. Breadth and brokerage measures (degree, betweenness, effective size) in the limited-overs formats single out all-rounders and lower-order players such as Rashid, Carse, Curran, Livingstone and Jordan, who bat with many different partners and tie the changing tail to the batting core. Only in Tests does one player, Root, lead on every measure, which is why that network is the most centralised.

Grouping follows two dimensions that the method recovered without being given them, batting position and time. Communities separate lower order, middle order and top order, and split the top order into successive generations of openers. The k-core analysis shows a clear core-periphery structure in all formats, with a core of about twenty batters holding two thirds of the strength in Tests and around nine tenths in the limited-overs formats; the periphery consists of players with a handful of innings. Heavy ties and core membership are different things: an established opening pair can carry the heaviest edge of a network and still lie outside its main core.

Across formats, Test cricket yields the most cohesive and most hub-centred network, ODI cricket the most segmented one, and T20I cricket the strongest contrast between a stable core and a wide, lightly connected periphery. These are statements about who batted with whom, not about ability or results.

## Critique

The project answers its descriptive questions for the population it defines. The network construction is the strongest part: every partnership is traceable to deliveries, totals agree with independent scorecard facts, and no boundary remained unresolved. The interpretation is more limited, for four reasons.

First, opportunity dominates. Degree, strength, core number and betweenness all rise with the number of innings (rank correlations above 0.9 for degree and strength), so the measures largely describe who was selected most. We reported innings alongside the results but did not normalise the networks; edges weighted by runs per partnership, or a comparison with a null model that reshuffles partners within each innings while keeping the batting order, would separate structure from exposure. Second, aggregating almost seven years into one static graph mixes squads that never met; the communities partly rediscover this. Yearly or sliding-window networks would show the change directly. Third, the model is deliberately simple: ties are undirected and ignore which batter scored the runs, extras are included in the weights, and path-based measures ignore weights altogether, so a pair with one run counts as much as a pair with two thousand. A directed network of runs scored while batting with each partner, or weighted path measures with a justified distance, are possible alternatives. Fourth, community detection is unstable in dense networks of this size: modularity is low and the number of groups changes with the seed, so only the broad pattern should be trusted.

There are also limits in the data and in the work done. Matches withheld by Cricsheet are missing, batting role and handedness are not in the source and were not added, and the small-world and degree-distribution results are weak evidence at fifty nodes. The question in our initial proposal, whether partnership structure differs between matches won and lost, was left out and remains future work, as does the same analysis for other national teams. Finally, the network figures in this report were drawn in Python from the exported GraphML files; they follow the conventions planned for Gephi but are not Gephi exports.

## References

Blondel, V. D., Guillaume, J.-L., Lambiotte, R., Lefebvre, E. (2008). Fast unfolding of communities in large networks. Journal of Statistical Mechanics, P10008.

Borgatti, S. P., Everett, M. G., Johnson, J. C. (2018). Analyzing Social Networks (2nd ed.). Sage.

Burt, R. S. (1992). Structural Holes: The Social Structure of Competition. Harvard University Press.

Cricsheet. Ball-by-ball cricket data, england_male_json.zip. https://cricsheet.org/downloads/ (archive dated 11 November 2026).

Freeman, L. C. (1978). Centrality in social networks: conceptual clarification. Social Networks, 1(3), 215-239.

Hagberg, A., Schult, D., Swart, P. (2008). Exploring network structure, dynamics, and function using NetworkX. Proceedings of SciPy 2008, 11-15.

Jacomy, M., Venturini, T., Heymann, S., Bastian, M. (2014). ForceAtlas2, a continuous graph layout algorithm for handy network visualization designed for the Gephi software. PLoS ONE, 9(6), e98679.

Newman, M. E. J. (2018). Networks (2nd ed.). Oxford University Press.

Seidman, S. B. (1983). Network structure and minimum degree. Social Networks, 5(3), 269-287.

Watts, D. J., Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. Nature, 393, 440-442.
