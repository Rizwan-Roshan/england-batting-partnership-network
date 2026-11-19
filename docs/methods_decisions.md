# Methods notes

For every measure we wrote down which question it answers, how it is computed and how we read it. The same
definitions are used for Test, ODI and T20I. All measures are computed in
`notebooks/library/lib_05_network_measures.ipynb`; the random seed (42) is set in
`notebooks/library/lib_00_settings.ipynb`.

Research questions: RQ1 overall shape and cohesion; RQ2 central batters; RQ3 clustering and redundancy;
RQ4 weighted degree; RQ5 communities; RQ6 bridges (betweenness); RQ7 core and periphery.

## General choices

| Topic | What we did | Why |
|---|---|---|
| Networks | Three separate undirected, weighted, one-mode networks, one per format. | The formats are played differently and partly by different players. |
| Edge weight | `weight` = sum of `runs.total` over every ball of every partnership of the pair. | This is what a cricket scorecard calls a partnership. |
| Weights and paths | Path-based measures (geodesic distance, betweenness, closeness, compactness, diameter) count every tie as one step. | A weight here means a stronger tie, while path algorithms would read it as a longer distance. |
| Pairs with 0 runs | Kept as edges (30 over the three formats). | The two batters did share the crease; they simply added no runs. |
| Components | Closeness and eigenvector centrality are computed on the main component. | All three networks are one single component, so this is the whole network. |

## Measures

| Measure | RQ | Level | Uses runs? | How it is computed | How we read it |
|---|---|---|---|---|---|
| Nodes, edges | 1 | network | no | Number of batters and of pairs who batted together. | Size of the batting group. |
| Density | 1 | network | no | Ties divided by possible ties, n(n-1)/2. | Share of all possible pairs that batted together. |
| Average degree | 1 | network | no | Mean number of partners. | Cohesion measure that is easier to compare across networks of different size. |
| Components, component ratio | 1 | network | no | Number of components; (c-1)/(n-1). | Whether the network falls apart into pieces. |
| Connectedness | 1 | network | no | Share of pairs of batters that can reach each other. | 1 means everyone is linked through some chain of partnerships. |
| Compactness | 1 | network | no | Mean of 1/geodesic distance over all pairs (0 if no path). | Rewards short chains as well as reachability. |
| Mean geodesic distance, diameter | 1, 3 | network | no | Mean and largest shortest-path length. | How many partnerships separate two batters. |
| Degree distribution | 1 | network | no | Histogram of degrees (Figure 2 of the report). | Shows the hubs. |
| Degree centralisation | 1 | network | no | Freeman: sum(max degree - degree) / ((n-1)(n-2)). | How much one batter dominates the network (1 = star). |
| Degree centrality | 2 | node | no | Number of different partners (also divided by n-1). | Breadth of a batter's ties. |
| Strength (weighted degree) | 4 | node | yes | Sum of the batter's edge weights. | All runs added in the batter's partnerships. |
| Closeness centrality | 2 | node | no | (n-1) / sum of distances to all others. | How close a batter is to everyone else. |
| Eigenvector centrality | 2 | node | yes | Leading eigenvector of the weighted adjacency matrix (power iteration, tolerance 1e-10). | Strong ties to batters who are themselves well connected. |
| Betweenness centrality | 6 | node | no | Share of shortest paths between other pairs that pass through the batter (normalised). | Batters who link parts of the squad that rarely bat together. |
| Local clustering coefficient, average clustering | 3 | node / network | no | Share of a batter's pairs of partners who are tied; 0 for batters with fewer than 2 partners. | Low values point to structural holes around a batter. |
| Transitivity | 3 | network | no | 3 x triangles / connected triples. | Clustering of the network as a whole. |
| Redundancy | 3 | node / network | no | Average number of ties from a partner to the batter's other partners, 2t/d. | How much a batter's partners overlap with each other. |
| Small-world index | 1, 3 | network | no | sigma = (C / C_random) / (L / L_random), with 200 seeded random graphs of the same size. | Above 1: more clustered than chance with similarly short distances. |
| k-cores | 7 | node / network | no | Core number of each batter (highest k-core it belongs to). | The highest k-core is the core; the rest is the periphery. |
| Louvain communities, modularity Q | 5 | node / network | yes | Louvain method on the weighted network, resolution 1, seed 42. We also ran seeds 0 to 99 and kept the range of Q and of the number of communities. | Groups of batters with more runs together than expected by chance. |
