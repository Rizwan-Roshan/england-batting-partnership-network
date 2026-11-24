# England Men's batting-partnership networks (Test, ODI, T20I), 2020-2026

Our Network Analysis group project. We build three separate networks from Cricsheet ball-by-ball data, one for
each international format. A node is an England batter, an edge joins two batters who batted together in at
least one partnership, and the edge weight is the total number of runs the pair added together. The networks
are undirected, weighted and one-mode. We analyse all three with the same measures and compare them.

## Main numbers

| | Test | ODI | T20I |
|---|---|---|---|
| Matches (first day between 1 Jan 2020 and 29 Oct 2026) | 81 | 88 | 118 |
| England innings | 151 | 85 | 114 |
| Partnerships | 1,357 | 708 | 763 |
| Nodes (batters) | 51 | 50 | 44 |
| Edges (pairs) | 335 | 262 | 222 |
| Density | 0.263 | 0.214 | 0.235 |

All result tables are in `outputs/tables/` and the report is in `report/`.

## Running it

```bash
pip install -r requirements.txt
./run_pipeline.sh
```

`run_pipeline.sh` runs the test notebook first and then every stage notebook in order. The notebooks are saved
with their outputs, so you can open any of them in Jupyter and see the results of the last run. You can also
re-run a single notebook on its own once the stages before it have run. The PDF is printed with Google Chrome;
the path to Chrome is set in `notebooks/library/lib_07_report_writer.ipynb`.

## Folders

```
data/raw/              the Cricsheet zip file (never changed); the unzipped copy is not tracked by git
data/interim/          list of source files and the decision for each match
data/processed/        match table, partnership table, node and edge tables
notebooks/             stage notebooks 00 to 08, run in this order
notebooks/library/     settings and functions shared by the stages
outputs/               result tables, figures and logs
docs/                  methods notes, data-quality report and the course template
report/                the report (docx, md, html, pdf) and authors.json
```

## Main modelling choices

- A match is in the study if it is a men's international Test, ODI or T20I with England playing, and its first day is inside the study window. These settings are in `notebooks/library/lib_00_settings.ipynb`.
- Partnership runs are the sum of `runs.total` over the balls of the partnership (extras included, counted once). The runs of a wicket ball go to the pair that was batting. Penalty runs given to a whole innings are not given to any pair.
- Players are identified by their Cricsheet ID, not by name.
- Edge weights are tie strengths. Path-based measures count every tie as one step; strength, eigenvector centrality and Louvain modularity use the runs. More detail in [docs/methods_decisions.md](docs/methods_decisions.md).
- Random seed 42 for Louvain and for the random comparison graphs.

## Data checks

See [docs/data_quality_report.md](docs/data_quality_report.md). In short: 29 of 29 tests pass; the partnership
runs equal the runs of all balls in all 350 innings; our innings totals give exactly the targets and winning
margins stored in the match files (318 of 318); every change of pair is explained; and 36 of 36 checks confirm
that the networks match the partnership table.

## Data source

Ball-by-ball data from [Cricsheet](https://cricsheet.org/), file `england_male_json.zip`. The licence file is
inside the zip.
