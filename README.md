# England Men's batting-partnership networks (Test, ODI, T20I), 2020-2026

Social Network Analysis course project. Three separate undirected, weighted,
one-mode networks are built from Cricsheet ball-by-ball data: nodes are England
batters, an edge joins two batters who shared at least one partnership, and the
edge weight is the total runs the pair added together. The three formats are
analysed with the same measures and compared.

The project definition is in [INSTRUCTIONS_England_Batting_Network.md](INSTRUCTIONS_England_Batting_Network.md).

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
./run_all.sh
```

`run_all.sh` runs the tests and then every stage in order. Each stage can also
be run alone, e.g. `python3 scripts/03_extract_partnerships.py`. Stages 4, 5 and 7
exit with an error if a validation gate fails. The PDF step needs Google Chrome
(macOS path; set `CHROME=` to override).

| Stage | Script | Output |
|---|---|---|
| 1 Source manifest | `scripts/01_build_manifest.py` | `data/interim/source_manifest.csv`, `source_summary.json` |
| 2 Match filters | `scripts/02_filter_matches.py` | `data/interim/file_audit.csv`, `data/processed/match_metadata.csv` |
| 3 Partnership extraction | `scripts/03_extract_partnerships.py` | `data/processed/partnership_observations.csv`, `innings_summary.csv`, `extraction_warnings.csv` |
| 4 Validation | `scripts/04_validate_observations.py` | `docs/data_quality_report.md`, `outputs/tables/validation_*.csv` |
| 5 Networks | `scripts/05_build_networks.py` | `data/processed/nodes_<fmt>.csv`, `edges_<fmt>.csv`, `players.csv` |
| 6 Measures | `scripts/06_compute_metrics.py` | `outputs/tables/network_summary.csv`, `node_metrics_<fmt>.csv`, `communities_<fmt>.csv`, `core_sizes_<fmt>.csv` |
| 7 GraphML and figures | `scripts/07_export_graphml.py`, `scripts/08_make_figures.py` | `outputs/graphml/england_men_<fmt>.graphml`, `outputs/figures/*.png` |
| 9 Report | `scripts/09_build_report.py`, `scripts/10_export_pdf.sh` | `report/report.docx`, `report.md`, `report.html`, PDF |

## Layout

```
data/raw/            Cricsheet archive (unchanged); extracted copy is git-ignored
data/interim/        manifest and file audit
data/processed/      match table, partnership observations, node and edge tables
src/batnet/          package: config, ingest, filters, extract, validate, aggregate, metrics, export, viz
scripts/             one script per stage
tests/               synthetic-fixture tests (16 required cases and metric conventions)
outputs/             tables, GraphML, figures, logs
docs/                methods decision register, data-quality report, course template
gephi/               Gephi workflow (workspaces to be saved here)
report/              report text (content.py), authors.json, built report
```

## Key modelling decisions

- A match qualifies if it is a men's international Test, ODI or T20I involving England whose first day is inside the window. Settings: `src/batnet/config.py`.
- Partnership runs use `runs.total` of each delivery once (extras included). The wicket delivery belongs to the pair at the crease. Innings-level penalty runs are not assigned to any pair.
- Players are identified by Cricsheet person ID.
- Edge weights are tie strengths. Path-based measures ignore weights; strength, eigenvector centrality and Louvain modularity use them. Details: [docs/methods_decisions.md](docs/methods_decisions.md).
- Random seed 42 for Louvain, random reference graphs and layouts.

## Validation summary

See [docs/data_quality_report.md](docs/data_quality_report.md). Partnership runs equal
delivery runs in all 350 innings; 318 of 318 independent target and margin checks
agree; 5 of 5 documented partnerships are reproduced; no extraction warnings;
36 of 36 aggregation invariants hold; GraphML files survive a round trip.

## Open items

- **Gephi:** not installed where the pipeline ran. The figures were drawn in Python from the GraphML files. Follow [gephi/README.md](gephi/README.md) to produce Gephi figures and workspaces.
- **Author details:** degree programme and ID numbers in `report/authors.json` are placeholders.
- **Archive date:** the download date was not recorded; the report cites the file date (11 November 2026).

## Data source and licence

Ball-by-ball data from [Cricsheet](https://cricsheet.org/), archive
`england_male_json.zip`. See the licence file inside the archive.
