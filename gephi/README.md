# Gephi workflow

Gephi is the visualisation tool selected for the project. The GraphML files in
`outputs/graphml/` are written by `scripts/07_export_graphml.py` and are the only
input Gephi needs. Gephi is used for drawing only: every number in the report
comes from the Python tables.

**Status:** Gephi is not installed on the machine where the pipeline was run, so
no `.gephi` workspace has been saved yet. The figures in `outputs/figures/` were
rendered in Python from the same GraphML files with the conventions below. Follow
the steps to produce the Gephi versions and save the workspaces in this folder.

## Expected counts (check after import)

| File | Nodes | Edges | Total weight |
|---|---|---|---|
| england_men_test.graphml | 51 | 335 | 43080 |
| england_men_odi.graphml | 50 | 262 | 22929 |
| england_men_t20i.graphml | 44 | 222 | 18974 |

## Steps, per format

1. File > Open > the GraphML file. Graph type: **Undirected**. Edge merge strategy: Sum (there are no parallel edges). One workspace per format.
2. Data Laboratory: check node/edge counts against the table; `weight` is a number; `label` holds the player name; `Id` is the Cricsheet person ID.
3. Layout: ForceAtlas 2, same settings for the three formats. Suggested: Scaling 10, Gravity 1, Prevent Overlap on, LinLog off, Edge Weight Influence 0 (heavy pairs otherwise collapse). Then "Label Adjust". Write down the settings actually used.
4. Appearance > Nodes > Size > Ranking > `strength` (e.g. 10 to 60).
5. Appearance > Nodes > Colour > Partition > `community` (Louvain partition computed in Python, seed 42).
6. Edges: thickness follows `weight` (Preview: rescale weight on).
7. Labels: show only for the largest nodes (filter on `strength`), font size proportional to node size.
8. Preview > export PNG at 300 dpi or SVG to `outputs/figures/gephi_<format>.png`.
9. File > Save as `gephi/england_men_<format>.gephi`.
10. Record Gephi version and layout settings in the table below.

| Format | Gephi version | Layout and settings | Date |
|---|---|---|---|
| Test | | | |
| ODI | | | |
| T20I | | | |

## Node attributes available in the GraphML

`player_name`, `label`, `format`, `matches_batted`, `innings_batted`,
`partnership_observations`, `distinct_partners`, `degree`, `strength`,
`strength_per_innings`, `betweenness`, `closeness_lcc`, `eigenvector_lcc`,
`clustering`, `core_number`, `community`, `effective_size`, `constraint`.

Edge attributes: `weight`, `partnership_count`, `total_matches`, `total_innings`,
`first_date`, `last_date` (DD-MM-YYYY), `format`, `mean_/median_/min_/max_partnership_runs`.

## Reading the pictures

Node size and edge thickness are encodings of `strength` and `weight`. Colours
show the Louvain partition. Layout distance is not graph distance and is not
evidence of anything.
