# Methods decision register

One entry per measure. The same definition is used for Test, ODI and T20I.
Software: NetworkX 3.4.2 (see `requirements.txt`). Code: `notebooks/library/lib_05_network_measures.ipynb`.
Random seed for every stochastic step: 42 (`notebooks/library/lib_00_settings.ipynb`).

Research questions (RQ): 1 structural characteristics; 2 structurally prominent
batters; 3 grouping, cohesion and redundancy; 4 weighted degree; 5 communities;
6 betweenness; 7 core-periphery.

## Global conventions

| Topic | Decision | Reason |
|---|---|---|
| Graphs | Three separate undirected, weighted, one-mode graphs. No pooled graph. | Project definition. |
| Edge weight | `weight` = sum of `runs.total` over all deliveries of all partnership observations of the pair. A tie *strength*. | Instructions 5.3, 6.4. |
| Weights in path measures | Ignored. Every tie has length 1 in betweenness, closeness, path length and diameter. | Runs are strengths, not distances; one convention only, no inverse-weight transform. |
| Zero-weight edges | Kept as edges (30 across formats: 14 Test, 7 ODI, 9 T20I). The pair did share the crease; it scored 0. | An edge means "shared a partnership". Weighted measures treat such a tie as contributing nothing. |
| Components | All three graphs are connected (1 component), so the largest connected component (LCC) is the whole graph. The code still restricts closeness, eigenvector and path statistics to the LCC and reports its size. | Instructions 9.5, 9.7. |
| Missing values | Not written as text. A node outside the LCC has no closeness/eigenvector attribute in GraphML. | Instructions 12.4. |

## Measures

| Measure | Course concept | RQ | Level | Weighted? | Definition / software convention | Interpretation here | Limitations |
|---|---|---|---|---|---|---|---|
| Nodes, edges | Network description | 1 | Network | No | Counts of batters and of unordered pairs with at least one partnership. | Size of the batting group and number of distinct pairings. | Grows with matches played; not comparable as cohesion. |
| Density | Cohesion | 1 | Network | No | 2m / (n(n-1)), no self-loops (`nx.density`). | Share of possible pairs that batted together. | Depends on n and on squad turnover. |
| Components | Connectedness | 1 | Network | No | `nx.connected_components`; count and sizes. | Whether every batter is linked to every other through chains of partnerships. | - |
| Degree | Degree centrality | 2 | Node | No | Number of distinct partners; normalised by n-1 as `degree_centrality`. | Breadth of partnership connections. | Driven by innings batted and batting position; not skill. |
| Degree centralisation | Centralisation | 1, 2 | Network | No | Freeman: sum(max_deg - deg_i) / ((n-1)(n-2)). | How far the network is organised around one batter. | Sensitive to a single hub. |
| Strength | Weighted degree | 2, 4 | Node | Yes | Sum of incident edge weights (`G.degree(weight="weight")`). Each partnership run is counted for both partners. | Cumulative partnership runs with all partners. | Opportunity-driven; includes extras; counts the partner's runs too. `strength_per_innings` (strength / innings batted) is given as a descriptive companion, not a skill rate. |
| Betweenness | Betweenness centrality | 2, 6 | Node | No | Share of shortest paths between other pairs passing through the node, normalised (`nx.betweenness_centrality(weight=None)`). | Position between otherwise weakly linked parts of the squad (e.g. eras, top order vs tail). | Says nothing about control or decisions; in dense graphs most values are small. |
| Closeness | Closeness centrality | 2 | Node | No | (n-1) / sum of shortest-path distances, on the LCC (`nx.closeness_centrality`). | How few partnership steps separate a batter from all others. | Small range in graphs of diameter 4. |
| Eigenvector | Eigenvector centrality | 2 | Node | Yes | Leading eigenvector of the weighted adjacency matrix on the LCC, power iteration, tol 1e-10, max 5000 iterations (converged for all formats). | Recursive prominence: heavy ties to batters who themselves have heavy ties. | Concentrates on the heaviest cluster; not batting ability. |
| Local clustering, average clustering | Clustering | 3 | Node / network | No | Share of a node's partner pairs that are themselves partners (`nx.clustering`); mean over nodes (degree-1 nodes count 0). | Whether a batter's partners also batted with each other. | Mechanically high: batters of the same innings form chains. |
| Transitivity | Clustering / cohesion | 3 | Network | No | 3 x triangles / connected triples (`nx.transitivity`). | Global tendency for triads to close. | As above. |
| Average path length, diameter | Compactness | 1 | Network | No | Mean and maximum shortest-path length on the LCC. | How many partnership steps separate batters. | Unweighted. |
| Small-worldness | Small-worldness | 1, 3 | Network | No | sigma = (C/C_rand)/(L/L_rand); C average clustering, L average path length; reference = mean of 200 G(n,m) random graphs with the same n and m (seeded). | Clustered locally yet short paths globally. | n about 50 and density above 0.2: paths are short in any such graph, so sigma is indicative only. |
| Degree distribution / scale-freeness | Scale freedom | 1 | Network | No | Histogram, mean, median, SD, max. No power-law fit. | Heterogeneity of partner counts. | 44-51 nodes cannot support a power-law test; reported descriptively. |
| Degree assortativity | Homophily by degree | 1 | Network | No | Pearson correlation of degrees at the two ends of edges. | Whether well-connected batters partner each other or less-connected ones. | Descriptive. |
| k-core | Core-periphery | 7 | Node / network | No | Maximal subgraph in which every node has at least k neighbours inside the subgraph; `core_number` = largest such k (`nx.core_number`). | Core = batters embedded in a mutually connected group; periphery = batters with few partners. | Membership reflects length of career in the window, not quality. |
| Communities | Groups / communities | 3, 5 | Node / network | Yes | Louvain modularity optimisation (`nx.community.louvain_communities`, weight = runs, resolution 1.0, seed 42). Louvain is the computational method; modularity Q reported. Stability: range of Q and of the number of communities over seeds 0-99. | Groups of batters who accumulated more runs with each other than expected. | Algorithm- and seed-dependent; not official units. Communities of 1-2 players are not interpreted. |
| Effective size, redundancy, efficiency | Redundancy / structural holes | 3 | Node | No | Burt's effective size for binary ties (Borgatti's form): degree - 2t/degree, t = ties among the ego's partners (`nx.effective_size`). Redundancy = degree - effective size. Efficiency = effective size / degree. | How many of a batter's partners are non-redundant, i.e. not also partners of each other. | Ego-network measure; correlated with degree. |
| Constraint | Structural holes | 3 | Node | No | Burt's constraint on binary ties (`nx.constraint`). | Low constraint = partners spread over parts of the squad that are not interlinked. | High for low-degree nodes by construction. |

## Measures considered and not used

- **Weighted betweenness / closeness with inverse runs as distance**: not used; it would mix two conventions and zero-weight edges would need an arbitrary distance.
- **Triad census, equivalence, attribute homophily**: no directed ties and no validated node attributes (batting role, handedness are not in the source data and were not guessed).
- **Win/loss comparison of network structure** (in the original proposal): not part of the approved research questions; listed as future work.
