# The Partnership Effect: Batting-Partnership Networks of the England Men's Cricket Team in Test, ODI and T20I Cricket (2020-2026)

Hafiz Muhammad Mutahhir Khan, Degree Programme, ID number (matricola)  
Saidatta Nagesh Musale, Degree Programme, ID number (matricola)  
Mohamed Rizwan Roshan Raja Mohamed, Degree Programme, ID number (matricola)  
Saad Salman, Degree Programme, ID number (matricola)  

## Introduction

Network analysis studies a system through the links between its parts. In team sport this idea fits well. Football passing networks are a common example. Cricket gets less attention, but batting has a natural link: the partnership. Two batters are always at the crease together. They build the score as a pair. When a wicket falls, one of them is replaced. Over many matches, these pairs form a network of who batted with whom and how many runs they added.

In this project we study the batting partnerships of the England men's team from 03 January 2020 to 29 October 2026. England play three international formats. Test matches last up to five days and each side bats twice. One Day Internationals (ODIs) have 50 overs per side. Twenty20 Internationals (T20Is) have 20 overs per side. The formats differ in length, in tactics and often in players. So we build one network for each format and study all three with the same method.

In each network, a node is a batter. An edge joins two batters who shared at least one partnership. The edge weight is the total number of runs the pair added together. The network shows how widely each batter is paired, where the runs are concentrated, which groups bat together often and who links groups that rarely meet. It does not measure how good a batter is, and we do not use it for that.

## Problem and Motivation

Cricket statistics usually focus on single players, such as batting averages, or on lists of record partnerships. Neither shows the bigger picture of how a whole batting group is connected. A batting order is not a fixed set of pairs. Openers meet the middle order. The middle order meets the tail. Players come and go over the years. The three formats use different but overlapping squads. Looking at this structure tells us how much the batting depends on a small core, how far apart the top order and the tail are, and which players link one generation of the squad to the next. It is also a good test case for the measures we learned in the course, because we can apply the same design to three similar networks.

We ask seven research questions (RQ). RQ1: What are the main structural features of the Test, ODI and T20I networks? RQ2: Which batters hold the most prominent positions in each format? RQ3: How are partnerships grouped, and what do cohesion and redundancy tell us? RQ4: Which batters have the highest weighted degree, that is, the most partnership runs? RQ5: Which communities of batters does a community-detection method find? RQ6: Which batters sit between other batters (betweenness)? RQ7: Is there a core-periphery structure?

Our work adds three things. First, a checked and repeatable way to rebuild every partnership from ball-by-ball data. Second, three weighted networks, one per format. Third, a side-by-side comparison of the three networks using the same measures and the same settings. The study is descriptive. We do not predict results and we do not rank players by ability.

## Datasets

Source. Our data come from Cricsheet (cricsheet.org). Cricsheet is a free, public collection of ball-by-ball cricket data. We used the file england_male_json.zip. It holds 961 matches of England men's teams in JSON format (schema version 1.3.0). The file is dated 11 November 2026. We keep it unchanged in our project folder, together with its checksum and a list of every file it contains. We did not type in any data by hand.

Filters. We kept a match if it was a men's international match, England was playing, the format was Test, ODI or T20I, and the first day fell between 1 January 2020 and 29 October 2026. All 961 files could be read. 287 matches passed the filters. The other 674 were left out because they started before 2020. In 7 limited-overs matches England never batted, because the game was abandoned or ended early. These matches give no partnerships. Table 1 shows the final counts.

**Table 1. The data after filtering (England batting innings only).**

|  | Test | ODI | T20I | Total |
|---|---|---|---|---|
| Matches | 81 | 88 | 118 | 287 |
| England innings | 151 | 85 | 114 | 350 |
| Deliveries | 66,829 | 22,766 | 12,878 | 102,473 |
| Partnerships | 1,357 | 708 | 763 | 2,828 |
| Partnership runs | 43,080 | 22,929 | 18,974 | 84,983 |
| Nodes (batters) | 51 | 50 | 44 | 73 different |
| Edges (pairs) | 335 | 262 | 222 | - |

Fields used. From each match we use the dates, gender, team type, match type and teams. We also use the player registry, which gives every player a fixed Cricsheet ID. From each England innings we read the deliveries in order. Each delivery names the striker and the non-striker. It gives the runs, where runs.total already includes extras, and it lists any wickets.

Finding the partnerships. A partnership is the time two batters spend at the crease together. Our code reads the deliveries one by one and remembers the current pair. Each delivery adds its runs.total to that pair, once. When a wicket record names one of the two batters, the partnership ends after that ball. So the runs scored on the wicket ball still count for the old pair. We do not use a fixed list of dismissal types. If the pair changes without a wicket, we accept it only if the file records a batter replacement. Otherwise we log it as a problem. The last partnership closes at the end of the innings. If a pair splits up and later bats together again, for example after a retired-hurt batter comes back, we count two partnerships. The result is a table with one row per partnership (2,828 rows). Each row has the match, date, innings, order in the innings, both player IDs, runs, number of balls, first and last ball and the reason the partnership ended.

Building the networks. For each format we group the partnerships by pair. The edge weight is the sum of the pair's partnership runs. Each edge also stores the number of partnerships, matches and innings, and the first and last date. A player becomes a node only by taking part in a partnership. Squad members who never batted with a partner are not nodes. Across the three formats there are 73 different batters, and 26 of them appear in all three networks.

Tools. We did all data work and all measures in Python 3.13 with pandas 3.0 and NetworkX 3.4.2. The code is a set of Jupyter notebooks that run in a fixed order. Shared functions sit in library notebooks, and a test notebook checks them on small made-up matches with known answers. Each network is saved as a GraphML file for Gephi, the visualisation tool chosen for the project. The figures in this report were drawn in Python from the same GraphML files, using the ForceAtlas2 layout from NetworkX.

## Validity and Reliability

Validity. Our network is a simple model of batting teamwork. An edge only means that two players batted together at least once. It does not mean friendship, talking to each other or helping each other score. Who bats with whom depends mostly on the batting order and on when wickets fall. So the network shows selection and batting position as much as real teamwork.

The edge weight is the score the pair added while together. It includes extras such as wides, no-balls and byes, because these are part of runs.total. This is how cricket scorecards define a partnership. It is not the sum of the two batters' own runs. Weights add up over time, so players with more matches collect more. A weight shows volume, not a scoring rate. 30 edges have a weight of zero: the pair batted together but added no runs. We keep them, because the link is real. One Test innings has five penalty runs that belong to the whole innings, not to any ball. We do not give them to any pair.

Our filters define who is in the study: England men, three international formats and matches that started inside the time window. Cricsheet holds back seven England matches involving Afghanistan. Some of them may fall inside our window. In ODIs and T20Is many players were rotated, so some nodes rest on very few innings.

Reliability. We never change the raw archive, and a checksum identifies it. The filters, dates, format names and the random seed (42) are set in one settings notebook. Players are identified by their Cricsheet ID, never by name. No player in our data appears under two spellings. The partnership rules are written down and tested on sixteen tricky cases, such as strike rotation, a run-out of the non-striker, extras, two wickets on one ball, a pair that bats together again, and penalty runs.

We checked the partnership data in three separate ways. First, in all 350 innings the partnership runs add up to the runs of all deliveries (84,983 runs from 102,473 deliveries). Second, we added up each innings straight from the raw files, without our partnership code, and compared the totals with two facts Cricsheet records separately: the target for the chasing side and the winning margin in runs. All 318 of 318 comparisons agree. Matches decided by a rain rule were not checked. Third, we looked up 5 famous partnerships, such as Root and Brook's 454 at Multan in 2024 and Buttler and Hales' unbeaten 170 in the 2022 T20 World Cup semi-final. Our data match all of them exactly. The code raised no warnings: every change of pair is explained by a wicket, one retired-hurt batter, two recorded batter replacements or the end of the innings. After building the networks, 36 further checks hold. For example, the edge weights of each format add up to its partnership runs. Each GraphML file was also read back and compared with the original. The only random step is Louvain community detection. Its seed is fixed, and we report how much the result changes with other seeds.

## Measures and Results

All three networks are undirected, weighted and one-mode. We follow one rule for weights. The weight is a tie strength: more runs means a stronger link. Shortest-path methods, however, read edge values as distances. So we use weights only in measures made for strengths: node strength, eigenvector centrality and modularity. In all path-based measures (betweenness, closeness and path length) every link counts as one step. Clustering, k-cores and redundancy also ignore weights. Table 2 sums up the networks. Figure 1 shows them.

**Table 2. Network-level measures. W = uses edge weights; all others ignore weights.**

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

*Figure 1. The three batting-partnership networks, drawn the same way. Node size: strength (total partnership runs). Edge width: runs of the pair. Colour: Louvain community (numbered by size within each format; grey: fewer than three players). Layout: ForceAtlas2 on the unweighted links; positions only help the drawing and are not a measure.*

Size, density and connectedness (RQ1). Density is the share of all possible pairs that actually batted together, 2m/(n(n-1)). A component is a group of nodes linked by paths. These measures show how fully the batters of a format are connected. Each network has about fifty batters (51, 50 and 44). Each one is a single connected component. So any batter can reach any other through a chain of partnerships, and all measures use the whole network. Density is 0.26 in Tests, 0.21 in ODIs and 0.23 in T20Is. In other words, between a fifth and a quarter of all possible pairs batted together. On average, two batters are about two steps apart (1.89, 2.04 and 1.96). The diameter, the longest of these shortest paths, is four in every format.

Edge weights are very uneven. The typical (median) pair added 42, 40 and 30 runs. But the heaviest tenth of the edges holds 63% of all partnership runs in Tests and about half in ODIs and T20Is. Between 39% and 51% of the pairs batted together only once. The heaviest pairs are, in Tests, BM Duckett–Z Crawley (2,697 runs in 65 partnerships); HC Brook–JE Root (2,566 runs in 43 partnerships); in ODIs, HC Brook–JE Root (953 runs in 22 partnerships); BM Duckett–JE Root (769 runs in 17 partnerships); in T20Is, PD Salt–JC Buttler (1,397 runs in 40 partnerships); JC Buttler–DJ Malan (793 runs in 16 partnerships).

Degree and strength (RQ2, RQ4). Degree is the number of different partners a batter had. It shows the breadth of a batter's links. Strength, or weighted degree, is the sum of the weights of a batter's edges. It is the total runs added in all the partnerships the batter took part in. We keep the two apart because they answer different questions: how many partners, and how many runs. Table 3 lists the leading batters.

**Table 3. Leading batters in each format. Betweenness and effective size ignore weights; strength and eigenvector use them.**

| Measure | Test | ODI | T20I |
|---|---|---|---|
| Degree | JE Root (38), BA Stokes (31), OJ Pope (30) | JE Root (24), AU Rashid (23), JC Buttler (23) | LS Livingstone (27), MM Ali (23), SM Curran (23) |
| Strength (runs) | JE Root (15,303), OJ Pope (7,568), Z Crawley (7,328) | JE Root (4,837), BM Duckett (3,716), JC Buttler (3,590) | JC Buttler (6,281), PD Salt (3,915), HC Brook (3,372) |
| Betweenness | JE Root (0.166), HC Brook (0.075), BA Stokes (0.066) | AU Rashid (0.117), BA Carse (0.116), AAP Atkinson (0.083) | LS Livingstone (0.148), AU Rashid (0.144), CJ Jordan (0.099) |
| Closeness | JE Root (0.806), OJ Pope (0.704), BA Stokes (0.694) | AU Rashid (0.645), JE Root (0.645), JC Buttler (0.628) | LS Livingstone (0.729), SM Curran (0.683), MM Ali (0.662) |
| Eigenvector | JE Root (0.545), OJ Pope (0.387), HC Brook (0.359) | JE Root (0.487), HC Brook (0.407), BM Duckett (0.371) | JC Buttler (0.567), PD Salt (0.447), HC Brook (0.349) |
| Effective size | JE Root (25.0), BA Stokes (18.7), OJ Pope (17.6) | JE Root (15.2), AU Rashid (14.5), SM Curran (14.2) | LS Livingstone (17.3), AU Rashid (14.5), MM Ali (14.0) |

In Tests, JE Root leads both lists by a wide margin. He batted with 38 of the other 50 batters. His strength is about twice that of the next player. This one hub explains why the Test network has the highest degree centralisation (0.52, against 0.29 in ODIs and 0.41 in T20Is). The index is 0 when all degrees are equal and 1 for a star. In ODIs, the highest degrees are shared by top-order and lower-order players. In T20Is, degree and strength split most clearly. LS Livingstone has the most partners, but JC Buttler has by far the highest strength, more than three times Livingstone's. Buttler's runs come from a few strong links. Livingstone has many partners, but each link is light.

Both measures depend on opportunity. The rank correlation between degree and innings batted is 0.93, 0.93 and 0.94. For strength it is 0.91, 0.91 and 0.94. So strength answers RQ4 in terms of involvement in partnership runs. It is not a measure of batting quality, since it also includes the partner's runs and extras. The degree distributions (mean 13.1, 10.5 and 10.1; maximum 38, 24 and 27) are skewed: many batters have few partners and a few have many. With only fifty nodes, however, we cannot test for a power law, so we make no claim that the networks are scale-free.

Betweenness, closeness and eigenvector centrality (RQ2, RQ6). Betweenness is the share of shortest paths between other batters that pass through a given batter. Here it points to players who sit between parts of the squad that rarely meet. It does not mean those players control anything. Closeness is based on the average distance from a batter to everyone else. Eigenvector centrality, computed with weights, is high for batters with strong links to other well-linked batters. It converged in all formats.

The three measures point to different players, most clearly in ODIs and T20Is. Eigenvector centrality follows the runs: Root, Pope and Brook in Tests; Root, Brook and Duckett in ODIs; Buttler, Salt and Brook in T20Is. All of them bat in the top or middle order. In Tests, Root also leads on betweenness (0.166, more than twice the next value). In ODIs, however, the three highest betweenness values belong to AU Rashid, BA Carse and AAP Atkinson. In T20Is they belong to Livingstone, Rashid and CJ Jordan. Rashid, Carse, Atkinson and Jordan usually come in late (typically in the seventh to ninth partnership of an innings). They bat with whoever is left of the specialist batters and with the other bowlers. Rashid also played through the whole period. These players connect the lower order, which changes often, to the rest of the team. So high betweenness marks a bridge between the batting core and the tail, and between older and newer squads. It goes together with low strength.

Clustering, redundancy and small-world structure (RQ3). A batter's local clustering coefficient is the share of the batter's partners who also batted with each other. Transitivity is the same idea for the whole network. A triangle means three players who have each batted with the other two. Average clustering is 0.616, 0.527 and 0.549. This is more than twice the value in random graphs with the same number of nodes and edges (0.262, 0.214 and 0.236; average of 200 random graphs). At the same time, paths are only 7% to 9% longer than in those random graphs. The small-world index, the clustering ratio divided by the path-length ratio, is about 2.2 in every format (2.19, 2.25 and 2.18). So the networks are tightly knit locally and still have short paths overall. Part of this is built into cricket: players in the same matches meet each other as wickets fall. With fifty nodes and a density above 0.2, short paths are almost certain anyway, so we treat this index as a rough guide only.

Redundancy comes from Burt's idea of structural holes. A partner is redundant if that partner also batted with the batter's other partners. Effective size is degree minus this redundancy. Constraint is high when all of a batter's partners are linked to each other. On average, only about half of a batter's partners are non-redundant (mean efficiency 0.47, 0.56 and 0.54). This is the same high clustering seen from each batter's point of view. The batters with the largest effective size and lowest constraint have partners in groups that do not meet each other: Root, Stokes and Pope in Tests; Root, Rashid and SM Curran in ODIs; Livingstone, Rashid and MM Ali in T20Is.

Communities (RQ5). A community is a group of nodes with more link weight inside the group than we would expect by chance. We used the Louvain method, which maximises weighted modularity Q (resolution 1, seed 42). This is a computer method, and its groups are not official units of the team. Modularity is low to moderate (0.224, 0.289 and 0.188), so the groups overlap a lot. Over 100 different seeds, the number of communities ranges from 4 to 6 in Tests, 3 to 4 in ODIs and 4 to 5 in T20Is. We only discuss the larger groups and ignore groups of one or two players.

Even so, the groups make sense. We describe them with two facts taken from the data: when a batter usually comes in (the number of the first partnership the batter joins in an innings, where 1 means opener) and the years the batter played. In Tests, the largest community (24 players, such as JL Smith, CR Woakes, JC Buttler, AAP Atkinson) usually comes in at partnership 8. This is the lower-middle order and the tail. The second (14 players: JE Root, BA Stokes, HC Brook, JM Bairstow) comes in at partnership 5. It is the middle order, which holds most of the runs. Two small top-order groups (both coming in at partnership 1) are split by time, not by position. OJ Pope, Z Crawley, BM Duckett are the top three of the later years. DP Sibley, RJ Burns, H Hameed, JL Denly were the top order of 2020 and 2021. The ODI network also splits by era. There is a top-order group most of whose members first appear in 2023 or later (JE Root, BM Duckett, HC Brook, WG Jacks), the opening group of 2020 to 2023 (JM Bairstow, PD Salt, JJ Roy, SW Billings), a middle-order group (JC Buttler, DJ Malan, LS Livingstone, SM Curran) and a large lower-order group (19 players, usually coming in at partnership 9). T20Is show the same three-way pattern: a current top order (JC Buttler, PD Salt, HC Brook, JG Bethell), an earlier group of top- and middle-order batters (DJ Malan, JM Bairstow, MM Ali, JJ Roy) and a lower-order group of 23 players. So the communities reflect batting position and squad generation.

Core and periphery (RQ7). A k-core is the largest part of the network in which every node has at least k neighbours inside that part. A batter's core number is the highest k for which the batter is still inside. The main core is a group of batters who are all well linked to each other. The low shells form the periphery. The main core is the 11-core in Tests (20 of 51 batters), the 9-core in ODIs (23 of 50) and the 8-core in T20Is (22 of 44). The core holds 66%, 87% and 93% of all node strength. Core batters played a median of 41, 29 and 32 innings, against 10.0, 5.0 and 4.5 for the rest. 5, 6 and 6 batters sit in the outer shells (core number 1 or 2). The Test core holds both specialist batters and long-serving bowlers: Root, Stokes and Brook, but also Broad, Anderson and Leach. On the other hand, the opening pair Crawley and Duckett, third and sixth in strength, are outside it. Openers bat mostly with each other and the number three. So they have heavy links but too few different partners. Core membership measures how embedded and long-serving a batter is, not how many runs the batter makes.

Comparing the formats. We used the same definitions for all three networks, and they are of similar size. This makes the structural measures comparable. Raw counts and strengths are not comparable, because a Test side bats twice and for much longer (151 innings and 66,829 deliveries, against 114 innings and 12,878 deliveries in T20Is). Three differences stand out. The Test network is the densest, the most clustered and the most centralised. It is built around one batter who played through the whole period, and its runs sit on the fewest edges. The ODI network is the least dense and least centralised. It has the most one-off pairs, the highest modularity and the most non-redundant links. With fewer matches per player and a change of generation during the period, it is the most split by era. The T20I network has the lowest modularity and the sharpest core-periphery divide: a core of 22 batters holds 93% of the strength, surrounded by many players with very few innings.

## Conclusion

The three networks share a common shape. Each is one connected component. Any two batters are about two partnership steps apart. Between a fifth and a quarter of all possible pairs exist. Clustering is more than twice that of similar random graphs, and about half of each batter's links are redundant. This is what the mechanics of batting produce. An innings links its batters in a chain, and picking the same players again and again closes the triangles. On top of this, runs sit on a small number of links. So the weighted picture is much more uneven than the unweighted one.

Who looks important depends on the measure, and the differences tell a story. Volume measures (strength and weighted eigenvector centrality) pick out the top-order and middle-order batters who pile up runs: Root in Tests and ODIs, and Buttler in T20Is. Breadth and bridging measures (degree, betweenness and effective size) pick out all-rounders and lower-order players in ODIs and T20Is, such as Rashid, Carse, Curran, Livingstone and Jordan. They bat with many different partners and link the changing tail to the batting core. Only in Tests does one player, Root, lead on every measure. That is why the Test network is the most centralised.

The groups follow two things the method was never told about: batting position and time. Communities separate the lower, middle and top order, and they split the top order into different generations of openers. The k-core analysis shows a clear core and periphery in all formats. A core of about twenty batters holds two thirds of the strength in Tests and around nine tenths in ODIs and T20Is. The periphery is made of players with only a few innings. Heavy links and core membership are not the same thing. An established opening pair can have the heaviest edge in the network and still sit outside the main core.

Across formats, Test cricket gives the most tightly knit and most hub-centred network. ODI cricket gives the most divided one. T20I cricket shows the biggest gap between a steady core and a wide, loosely linked periphery. These are statements about who batted with whom, not about ability or results.

## Critique

We think the project answers its descriptive questions for the group of matches it covers. The strongest part is how the networks were built. Every partnership can be traced back to single deliveries. Innings totals match separate scorecard facts. No partnership boundary was left unexplained. Our interpretation has more limits, for four reasons.

First, opportunity drives most measures. Degree, strength, core number and betweenness all rise with the number of innings played (rank correlations above 0.9 for degree and strength). So the measures largely show who was picked most often. We reported innings next to the results, but we did not adjust the networks for it. Using runs per partnership as the weight, or comparing with random networks that shuffle partners inside each innings while keeping the batting order, would separate structure from playing time. Second, we put almost seven years into one static network. This mixes squads that never met, and the communities partly pick this up. Networks per year, or for a moving time window, would show the change directly. Third, the model is kept simple on purpose. Links have no direction and do not show which batter scored the runs. Extras are included in the weights. Path-based measures ignore weights, so a pair with one run counts the same as a pair with two thousand. A directed network of runs scored with each partner, or weighted path measures with a sound distance, could be tried instead. Fourth, community detection is unstable in dense networks of this size. Modularity is low and the number of groups changes with the seed, so only the broad pattern should be trusted.

There are also limits in the data and in what we did. Matches held back by Cricsheet are missing. Batting role and handedness are not in the source, and we did not add them. The small-world and degree-distribution results are weak evidence with only fifty nodes. Our first proposal also asked whether the partnership structure differs between matches won and lost. We left that question out, and it remains future work, as does the same study for other national teams. Finally, the network figures in this report were drawn in Python from the exported GraphML files. They follow the style planned for Gephi, but they are not Gephi exports.

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
