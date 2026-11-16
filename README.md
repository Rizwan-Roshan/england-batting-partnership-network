# England Men's batting-partnership networks (Test, ODI, T20I), 2020-2026

Social Network Analysis course project. We build three separate undirected, weighted, one-mode networks from
Cricsheet ball-by-ball data. A node is an England batter. An edge joins two batters who shared at least one
partnership. The edge weight is the total runs the pair added together. We analyse the three formats with the
same measures and compare them.

The project definition is in [INSTRUCTIONS_England_Batting_Network.md](INSTRUCTIONS_England_Batting_Network.md).
**The run order and the purpose of every file are in [EXECUTION_SEQUENCE.md](EXECUTION_SEQUENCE.md).**

## Results at a glance

| | Test | ODI | T20I |
|---|---|---|---|
| Matches (start date 2020-01-01 to 2026-10-29) | 81 | 88 | 118 |
| England innings | 151 | 85 | 114 |
| Partnership observations | 1,357 | 708 | 763 |
| Nodes (batters) | 51 | 50 | 44 |
| Edges (pairs) | 335 | 262 | 222 |
| Density | 0.263 | 0.214 | 0.235 |

Full tables: `outputs/tables/`. Report: `report/`.

## Reproduce

```bash
pip install -r requirements.txt
./run_pipeline.sh
```

`run_pipeline.sh` runs the test notebook and then every stage notebook in order. The notebooks are executed
in place, so their saved outputs always show the latest run. You can also open any notebook in Jupyter and
run it on its own, as long as the stages before it have run once. Stages 0, 4, 5 and 7 stop with an error if
a check fails. The PDF step needs Google Chrome (macOS path set in `notebooks/library/lib_07_report_writer.ipynb`).

## Layout

```
data/raw/              Cricsheet archive (unchanged); the extracted copy is git-ignored
data/interim/          manifest and file audit
data/processed/        match table, partnership observations, node and edge tables
notebooks/             stage notebooks 00-09, run in order
notebooks/library/     shared settings and functions, loaded by the stages with %run
outputs/               tables, GraphML, figures, logs
docs/                  methods decision register, data-quality report, course template
gephi/                 Gephi workflow (workspaces to be saved here)
report/                built report (docx, md, html, pdf) and authors.json
```

## Key modelling decisions

- A match qualifies if it is a men's international Test, ODI or T20I involving England whose first day is inside the window. Settings: `notebooks/library/lib_00_settings.ipynb`.
- Partnership runs use `runs.total` of each delivery once (extras included). The wicket delivery belongs to the pair at the crease. Innings-level penalty runs are not given to any pair.
- Players are identified by Cricsheet person ID.
- Edge weights are tie strengths. Path-based measures ignore weights; strength, eigenvector centrality and Louvain modularity use them. Details: [docs/methods_decisions.md](docs/methods_decisions.md).
- Random seed 42 for Louvain, the random reference graphs and the layout.

## Validation summary

See [docs/data_quality_report.md](docs/data_quality_report.md). 29 of 29 tests pass. Partnership runs equal
delivery runs in all 350 innings; 318 of 318 independent target and margin checks agree; 5 of 5 documented
partnerships are reproduced; no extraction warnings; 36 of 36 aggregation checks hold; GraphML files survive a
round trip.

## Open items

- **Gephi:** not installed where the pipeline ran. The figures were drawn in Python from the GraphML files. Follow [gephi/README.md](gephi/README.md) to make Gephi figures and workspaces.
- **Author details:** degree programme and ID numbers in `report/authors.json` are placeholders.
- **Archive date:** the download date was not recorded; the report cites the file date (11 November 2026).

## Data source and licence

Ball-by-ball data from [Cricsheet](https://cricsheet.org/), archive `england_male_json.zip`. See the licence
file inside the archive.
