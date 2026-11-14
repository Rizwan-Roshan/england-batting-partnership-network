## England Men's Batting Partnership Network Analysis



Construct and analyse **three separate weighted, undirected, one-mode player networks** from Cricsheet ball-by-ball data:

1. Test
2. One Day International (ODI)
3. Twenty20 International (T20I)

The subject is the England Men's national team. Analyse each format separately, then compare their structures where comparisons are methodologically meaningful.

## 1.4 Working research questions

1. What are the structural characteristics of England Men's batting-partnership networks in Test, ODI and T20I cricket during the observation period?
2. Which batters occupy structurally prominent positions in each format, according to appropriate network measures?
3. How are partnerships grouped or clustered, and what do cohesion and redundancy reveal about the network structure?
4. Weighted degree centrality: which players are most usefull
5. Community detection
6. Between centrality
7. Core periphery network 

These are the approved working questions. Do not silently add a prediction objective or replace them with a general player-ranking objective.

---

# 5. Exact network model

## 5.1 Network type

For each format, build one:

- undirected;
- weighted;
- monomodal / one-mode;
- player-to-player network.

The three formats are separate primary graphs. Do not pool them.

## 5.2 Nodes

A node represents an England Men's batter who participated in at least one extracted batting partnership in a qualifying England batting innings in that format.

Do not add a player merely because they were in a squad, appeared in `info.players`, fielded, bowled, played for the opponent, or was selected but never formed a partnership.

If useful, retain a separate batting-participation table for players who entered the crease but did not form a partnership. Such players do not become nodes under the approved graph definition unless they form a partnership elsewhere in that format.

## 5.3 Edges

An undirected edge connects two distinct batters if they shared at least one batting partnership in at least one qualifying England innings in that format.

The primary edge weight is:

**`weight = sum of partnership runs for that pair across all qualifying partnership observations in that format`**

A partnership observation is one pair's partnership in one innings. The same pair may have multiple observations across matches or innings. Preserve each observation before aggregation.

## 5.4 Required edge attributes

- `weight`: total partnership runs for the pair;
- `partnership_count`: number of partnership observations;
- `total_matches`: number of distinct matches in which the pair partnered;
- `total_innings`: number of distinct innings in which the pair partnered;
- `first_date`: earliest partnership date;
- `last_date`: latest partnership date;
- `format`: canonical format label.

Recommended descriptive attributes, if correctly calculated:

- `mean_partnership_runs`;
- `median_partnership_runs`;
- `min_partnership_runs`;
- `max_partnership_runs`.

Do not confuse `weight`, `partnership_count`, `total_matches` and `total_innings`.

## 5.5 Required node attributes

- `player_id`;
- `player_name`;
- `format`;
- `matches_batted`;
- `innings_batted`;
- `partnership_observations`;
- `distinct_partners`.

Define denominators precisely. Optional attributes such as batting role, batting position or handedness may only be added if reliably sourced, validated and documented. Do not guess them.

---

# 6. Partnership extraction — critical implementation rules

Incorrect partnership boundaries corrupt every graph, edge weight and downstream result. This is the highest-risk part of the project.

## 6.1 General principle

A batting partnership is the period during an innings when a particular pair of batters share the crease. The pair is unordered in this network.

Implement a stateful, auditable partnership extractor.

## 6.2 Delivery order

Process each England batting innings in the order represented in the JSON:

- innings order;
- over order;
- delivery order within each over.

Preserve the original sequence and a stable delivery identifier. Do not reorder by `actual_delivery` unless the current Cricsheet schema explicitly requires it and tests establish that this is correct.

## 

## 6.4 Partnership runs

For every delivery belonging to the current partnership, add `delivery["runs"]["total"]` exactly once.

Rules:

- `runs.total` is the delivery's total run contribution, including applicable extras represented on that delivery.
- Do **not** add the `extras` object on top of `runs.total`; that double-counts extras.
- Do not use only `runs.batter`.
- Preserve `runs.batter` and extras breakdown separately for audit/validation.
- Runs on the wicket delivery belong to the pair that was at the crease during that delivery, unless the source's documented representation establishes otherwise.
- Do not allocate innings-level penalty runs to a pair unless explicitly represented as a delivery-level contribution attributable to that delivery.

## 6.5 Partnership boundaries

A partnership begins when a pair starts sharing the crease. It ends when:

- one or both members leave the crease and the pair changes;
- a batter retires or is replaced so that the pair changes;
- the innings ends.

For a dismissal delivery:

1. Identify the pair active for that delivery.
2. Add the delivery's `runs.total` to that pair.
3. Inspect wicket records and identify whether a current partner left the crease.
4. Close the old partnership after processing the delivery.
5. Establish the next pair from subsequent source data and/or documented incoming-batter information.
6. Validate the transition.

A partnership that genuinely ends and later resumes with the same two players must be recorded as two observations, not one continuous observation.



## 6.7 Incoming batter and unusual cases

Do not invent an incoming batter. The next delivery's `batter` and `non_striker` can help establish the new pair, but the transition must be checked against the sequence and dismissal information.

Investigate pair changes without an obvious wicket. Possible causes include:

- retired hurt / retired out;
- unusual dismissal;
- innings closure;
- malformed or incomplete source data;
- parser error.

Log the reason or mark it unresolved. Do not silently carry the old pair forward.

## 6.8 Multiple wickets / events

Handle all wicket records on a delivery. Do not assume one wicket per delivery or one incoming batter after every wicket.

If multiple wickets occur on one delivery:

- assign that delivery's runs to the pair active for the delivery;
- apply the source event semantics;
- do not create a fictitious intermediate partnership that had no delivery;
- validate the next available pair;
- log any ambiguity.

Handle, where present:

- run-outs;
- retired hurt;
- retired out;
- timed out;
- obstructing the field;
- absent / absent hurt;
- innings ending without all wickets falling;
- any other event in the archive.

Do not hard-code a dismissal-kind allowlist without checking the current schema and documenting the logic.

## 6.9 Partnership observation table

Before graph aggregation, save one row per partnership occurrence, with at least:

- `match_id` or stable match key;
- source filename;
- match date;
- format;
- innings index / stable innings ID;
- batting team;
- partnership sequence number within innings;
- player 1 stable ID and display name;
- player 2 stable ID and display name;
- partnership runs;
- delivery count, if defined consistently;
- start delivery ID;
- end delivery ID;
- boundary reason (dismissal, retirement/replacement, innings end or other documented reason);
- data-quality status/warning.

This table is the audit trail. The aggregated graph must be reconstructible from it.

## 6.10 Innings-level penalty runs

If penalty runs are represented at innings level rather than on a delivery:

- record them separately;
- do not allocate them to a pair arbitrarily;
- exclude them from edge weights unless explicitly included in a delivery's `runs.total`;
- explain this modelling choice in the report.

## 6.11 Do not infer partnership count from wicket count

Do not assume partnership count equals wickets plus one or any other fixed formula. Count actual pair observations from state transitions and innings structure.

---

# 7. Data validation and quality assurance

A script running without errors is not proof that the data are correct. Build explicit validation into the pipeline.

## 

## 7.3 Aggregation checks

For each format:

- no self-loops;
- every edge corresponds to one or more observations;
- `weight` equals the sum of observation runs for that pair;
- `partnership_count` equals observation count for that pair;
- distinct match and innings counts are correct;
- edge count equals the number of unique unordered player pairs;
- sum of edge weights equals sum of all partnership observation runs;
- node partnership counts and distinct partners reconcile with the observation table;

## 7.5 Reproducibility

All scripts must run through documented commands. Avoid hidden notebook state. Fix random seeds for stochastic algorithms and record them. Store software/package versions.

---

# 9. Network analysis measures — course-aligned

The course materials cover core concepts including degree, betweenness, closeness, eigenvector centrality, density/cohesion, components/connectedness, clustering/transitivity, communities, redundancy/structural holes, small-worldness and scale-free structure. The professor's project guidance gives k-core as an example.

Select measures because they answer the research questions. Do not mechanically implement every measure mentioned in the course checklist. Verify exact definitions in the lecture materials before finalising the methods section.

## 9.1 Basic graph description

For each format report:

- node count;
- edge count;
- graph type (undirected, weighted, one-mode);
- density;
- connected-component count;
- largest-component size;
- whether the graph is connected;
- degree distribution / useful summary;
- edge-weight distribution / useful summary.

State whether each statistic is weighted or unweighted.

## 9.2 Degree

Degree = number of distinct partners a batter has.

Interpret as breadth of partnership connections, not runs or batting skill.

## 9.3 Strength / weighted degree

Strength = sum of edge weights incident to a node. Here it represents cumulative partnership runs with all recorded partners in that format.

It is a weighted extension of degree. It is affected by opportunity and is not a pure skill measure. Keep degree and strength distinct.

## 9.4 Density

Density is the proportion of possible undirected edges that are present. State the formula/convention and that self-loops are excluded.

Interpret as how extensively the observed batters are connected through partnerships. Do not call a graph “dense” without context or comparison.

## 9.5 Components and connectedness

Report component count and component sizes. A component is a set of nodes connected by paths. Do not assume the network is connected or silently omit small components.

## 9.6 Betweenness centrality

Betweenness measures how often a node lies on shortest paths between other nodes.

Interpret as structural position between parts of the collaboration network. Do not claim literal control of information, strategy or match decisions.

**Critical weight/distance distinction:** partnership `weight` is tie strength (larger means more runs), while shortest-path algorithms normally treat edge values as distances (larger means farther). Never pass strength weights to a distance-based shortest-path algorithm without a justified transformation.

Choose and document one convention:

- unweighted betweenness, explicitly ignoring tie strength; or
- a documented distance transformation, such as inverse positive strength, including treatment of zero or very small weights.

Do not mix conventions without labels.

## 9.7 Closeness centrality

Closeness concerns distances from a node to others. Disconnected graphs require care.

- Do not calculate ordinary closeness on a disconnected graph and interpret it as if all nodes can reach one another.
- Either calculate closeness on the largest connected component and label the restriction, or use harmonic centrality/harmonic distance if supported by the course material.
- Report the component size and do not silently drop disconnected nodes.

## 9.8 Eigenvector centrality

Eigenvector centrality gives greater importance to nodes connected to other important nodes.

Interpret as recursive structural prominence, not batting ability. Check convergence. State whether calculated on the whole graph or component-wise. Inspect software behaviour for disconnected graphs and document the chosen convention.

## 9.9 Clustering coefficient and transitivity

Use local clustering coefficient and/or global transitivity if relevant.

A triangle means three players have each partnered with the other two at least once. Interpret clustering as the extent to which a batter's partners are themselves connected. Do not say high clustering means better batting. State whether the measure uses unweighted topology or a weighted definition.

## 9.10 Communities / groups

Community analysis may be included because groups/communities are part of the course context.

- Verify the concept and interpretation in lecture material.
- If using an algorithm such as Louvain, identify it as the computational method; do not claim it was explicitly taught unless confirmed by slides.
- State whether weights are used.
- Record parameters and random seed.
- Explain that communities are algorithm-dependent groupings, not official teams or fixed batting units.
- Do not over-interpret tiny communities.

## 9.11 Redundancy / structural holes

If included, use the exact definition and terminology taught in the course. Examine whether a player's partners are connected to one another and explain redundancy/structural holes. Do not substitute a vaguely similar statistic without explaining it.

## 9.12 Core-periphery / k-core

Consider k-core analysis where useful. The professor's project guidance explicitly gives k-core as an example of identifying core nodes.

Explain what a k-core represents, how nodes qualify, whether the calculation uses unweighted topology, and what core membership means in this network. Do not equate high k-core membership with being the best batter.

## 

## 9.14 Methods decision register

Maintain `methods_decisions.md` documenting, for each selected measure:

- course concept/syllabus alignment;
- research question;
- node-level or network-level;
- weighted or unweighted;
- formula/software convention;
- preprocessing and component handling;
- parameter choices;
- interpretation;
- limitations.

Use the same definition across formats unless a difference is necessary and explicitly justified.

---

# 10. Cross-format comparison

Compare the same study design across Test, ODI and T20I wherever possible.

- Present network size and structure together.
- A larger graph may naturally have more nodes and edges; raw counts alone do not imply greater cohesion.
- Do not compare raw total partnership runs across formats as if opportunities were equal.
- Do not compare raw strength without explaining differences in match/innings length and player opportunity.
- Use the same centrality definitions and computational conventions across formats.
- Density depends on the number of nodes.
- For component/clustering comparisons, state graph sizes and composition.
- If a metric is calculated only on the largest component, report its size and share of all nodes for each format.
- Keep player identity consistent across formats but retain format-specific node sets and edges.

Do not create a combined Test+ODI+T20I graph as a primary result. A pooled graph, if later requested, must be supplementary and justified.

---

# 11. Software responsibilities

## 11.1 Python

Use Python for:

- archive ingestion;
- metadata filtering;
- JSON parsing;
- player ID normalisation;
- partnership extraction;
- audit logs and validation;
- partnership observation tables;
- graph construction;
- network metric computation;
- reproducible tables and intermediate outputs;
- GraphML export for Gephi.

NetworkX is suitable for graph construction and many measures. Use other libraries only when necessary and document why. Pin package versions in the environment file.

Do not rely on Gephi to clean or repair the dataset. Data cleaning and graph construction must be reproducible in Python.

## 11.2 Gephi — required visualization tool

**Gephi is the selected tool for network visualization.**

Python exports clean GraphML files with correct node and edge attributes. Import each format as a separate graph/workspace in Gephi.

Gephi is used for visualisation and visual exploration, not as the source of truth for data or the only place where metrics are calculated.

### Gephi workflow

For each format:

1. Import its GraphML file.
2. Confirm graph is undirected.
3. Verify node and edge counts against Python outputs.
4. Verify `weight` is numeric.
5. Verify player IDs and labels are preserved.
6. Choose a layout that makes the network readable. A force-directed layout such as ForceAtlas2 may be considered; record the layout and settings actually used.
7. Do not treat the layout as statistical evidence.
8. Map node size to a selected node measure (e.g. degree or strength) and label the legend.
9. Map edge thickness to partnership-run weight if it remains readable.
10. Use node colour for communities only if community analysis is included and assignments are valid.
11. Avoid excessive labels; prioritise readability.
12. Use consistent visual conventions across formats for comparison.
13. Save Gephi project/workspace files.
14. Export high-resolution figures for the report.
15. Record Gephi version, layout name and important settings.

### Visual interpretation rules

- Node size is a visual encoding, not a new metric.
- Edge thickness represents weight only when the legend says so.
- Community colours describe the selected algorithm's partition.
- Layout distance is not automatically graph distance or partnership quality.
- Visual proximity does not prove causation or batting skill.

### Minimum figures

Aim for:

- one overall network figure per format;
- one consistent comparative figure or three-panel set;
- additional focused figures only when they clarify a result.

Do not make a figure unreadable just to label every node.

---

# 12. Data contracts and exports

## 12.1 Partnership observations

Save as CSV or Parquet. Use UTF-8, ISO dates (`DD-MM-YYYY`), explicit column names and consistent types.

## 12.2 Node and edge tables

For each format, export node and edge tables, e.g.:

- `nodes_test.csv`, `edges_test.csv`;
- `nodes_odi.csv`, `edges_odi.csv`;
- `nodes_t20i.csv`, `edges_t20i.csv`.

Each edge row must represent one unique unordered pair. Pair keys must be canonical and stable.

## 12.3 GraphML

Export one graph per format:

- `england_men_test.graphml`;
- `england_men_odi.graphml`;
- `england_men_t20i.graphml`.

Requirements:

- undirected graph declaration;
- stable node IDs;
- readable node labels;
- numeric edge `weight`;
- preserve partnership count, match/innings counts, dates and useful attributes;
- avoid unsupported nested/object attributes;
- re-import and validate counts and weights.

## 12.4 Numeric and missing values

- Do not encode missing values as `"None"` or `"nan"` strings without a documented reason.
- Use consistent numeric types.
- Do not round source values; round only in report presentation.
- Preserve partnership runs as exact integers.
- Avoid locale-specific decimal separators in machine-readable files.

---

# 13. Required tests

Create synthetic fixtures with known expected outputs. Tests must assert exact values, not merely that functions return.

Minimum cases:

1. Simple partnership: two batters; all delivery runs assigned correctly.
2. Strike rotation: batter/non-striker order swaps; partnership remains unchanged.
3. Ordinary wicket: wicket-delivery runs go to old partnership; new pair starts a new observation.
4. Non-striker run-out: partnership closes even though striker is not dismissed.
5. Extras: `runs.total` used once; extras not double-counted.
6. Multiple wickets: no fictitious partnership between wicket events on the same delivery.
7. Innings end: final partnership closes exactly once.
8. Same pair reunites after a genuine break: separate observations, one aggregated edge.
9. Same pair in a different match: same format edge accumulates runs and match count.
10. Same pair in different formats: separate graphs.
11. Date boundaries: include 2020-01-01 and 2026-10-29; exclude 2019-12-31 and 2026-10-30.
12. Gender/team/format filters: exclude women's, domestic and non-target matches.
13. Player identity: aliases with same stable ID merge; different IDs remain separate.
14. Roster-only player: does not become a node.
15. Innings-level penalty: not assigned arbitrarily to a pair.
16. GraphML round trip: node/edge counts and weights preserved.

---

# 14. Report structure and academic requirements

Follow the uploaded **Network Analysis Project Template**. Its sections are:

1. Project Title and author information.
2. Introduction.
3. Problem and Motivation.
4. Datasets.
5. Validity and Reliability.
6. Measures and Results.
7. Conclusion.
8. Critique.

Write the report in English.

## 14.1 Introduction

Explain the general field (network analysis applied to sport/cricket data), the specific application (England Men's batting partnerships), what the network captures and why its structure is interesting. Avoid a long cricket history or unsupported player-quality claims.

## 14.2 Problem and Motivation

State the research questions and explain why partnership structure is worth studying. The contribution is construction and comparative structural analysis of three format-specific networks over the defined period.

## 14.3 Datasets

Explain:

- Cricsheet source;
- archive retrieval date;
- filters;
- JSON fields;
- data processing and partnership extraction;
- Python and libraries;
- Gephi visualization;
- actual counts of files, matches, innings, partnership observations, nodes and edges.

Do not insert counts until computed from the filtered data.

## 14.4 Validity and Reliability

Discuss validity:

- network is a simplified representation of batting collaboration;
- an edge means shared a batting partnership, not friendship, communication, tactical influence or causal contribution;
- edge weight is accumulated partnership runs, including delivery-level extras represented in `runs.total`;
- innings-level penalties are not arbitrarily assigned;
- filters define the population represented;
- Cricsheet coverage/schema limitations may affect representativeness.

Discuss reliability:

- reproducible filters and code;
- immutable raw data and source manifest;
- stable player IDs;
- explicit boundary logic;
- validation and spot checks;
- package versions and random seeds;
- saved intermediate tables and GraphML exports.

## 14.5 Measures and Results

For every measure:

- briefly explain how it works;
- explain why it addresses the research question;
- explain its meaning in a batter partnership network;
- state weighted/unweighted and component conventions;
- report actual results;
- avoid unsupported causal or skill interpretations.

Present format-specific results first, then compare formats carefully.

## 14.6 Conclusion

Qualitatively interpret quantitative findings and answer the research questions. Do not simply repeat every table.

## 14.7 Critique

Discuss how well the project answered its questions, data coverage/missingness, simplifications in the network model, cumulative weights/opportunity effects, unresolved boundary ambiguities, measure limitations and possible future alternatives. Do not claim limitations were solved if they were not.

## 14.8 Professor's report constraints

The professor's course page states:

- maximum **5,000 words** (approximately 30,000 characters; around 9–10 pages);
- English;
- PDF submission;
- A4, single column;
- single line spacing;
- 3 cm margins;
- 12 pt Times or equivalent;
- filename: group members' surnames in alphabetical order, separated by `and`;
- email subject prefix: `[Network Analysis]`.

The page also states:

- group size 3–5;
- an outline can be sent for feedback;
- the full report is not pre-evaluated;
- grading: 20% context/problem/motivation, 60% datasets/validity/measures/results, 20% interpretation/critique.



---

# 15. Required final deliverables

## 15.1 Data and audit

- raw archive retained unchanged or clear download procedure;
- source manifest;
- file inclusion/exclusion log;
- normalised match metadata;
- partnership observation table;
- data-quality report;
- validation/spot-check record.

## 15.2 Network outputs

For each format:

- node table;
- edge table;
- GraphML;
- network summary table;
- node-level metrics table;
- community/core assignments, if used.

## 15.3 Visualization

- Gephi project/workspace files;
- high-resolution figure per format;
- consistent comparative figure(s);
- figure captions and legends.

## 15.4 Documentation and report

- README with reproduction instructions;
- dependency/environment file;
- methods decision register;
- report source;
- final PDF;
- limitations and data-quality notes.

Never claim an output is complete unless it exists and has been checked.

---

# 16. Implementation sequence and acceptance gates

Work in small verifiable stages. Do not jump straight to full-network analysis.

### Stage 1 — Source inspection

Obtain the official archive, inspect its structure and representative files from all formats, read schema documentation and create the source manifest.

**Gate:** source and schema assumptions documented; no silent filtering.

### Stage 2 — Match filters

Parse metadata, apply gender/England/international/date/format filters, create inclusion/exclusion audit.

**Gate:** boundary-date and exclusion tests pass; counts are derived from actual files.

### Stage 3 — Partnership extraction

Implement stateful innings parser; handle strike changes, wickets, non-striker dismissals, extras, unusual events and innings termination; save observations.

**Gate:** unit tests pass; spot checks reconcile; unresolved cases logged.

### Stage 4 — Observation validation

Reconcile innings totals where possible; check identities and boundaries; create quality report.

**Gate:** no unexplained critical discrepancy remains. If one remains, stop and report it.

### Stage 5 — Graph aggregation

Aggregate observations by format and unordered player pair; create node/edge tables and graphs; verify invariants.

**Gate:** graph values reconcile exactly to observation tables.

### Stage 6 — Network measures

Calculate selected course-aligned measures with documented conventions; handle disconnected components; export results.

**Gate:** methods register complete and metric tests pass.

### Stage 7 — Gephi

Import GraphML; check counts/attributes; create consistent readable visualisations; save workspaces and figures.

**Gate:** Gephi figures match Python graph data and have readable legends/captions.

### Stage 8 — Interpretation and comparison

Analyse each format separately; compare structures carefully; show denominators and opportunity limitations.

**Gate:** every claim is supported by calculated output and correct denominator.

### Stage 9 — Report

Follow the template; check word count, figures, references, formatting and submission rules; verify every reported number against outputs.

**Gate:** report is reproducible, internally consistent and does not overstate findings.

---

# 17. working rules

1. Inspect the existing repository before changing anything. Do not overwrite user work.
2. Read this file and README before implementation.
3. Do not assume the Cricsheet archive has already been downloaded.
4. Do not invent match counts, player counts, edge counts, results or paths.
5. Do not fabricate player IDs or incoming batters.
6. Do not silently skip malformed files or innings; log and summarise exclusions.
7. Keep raw data immutable.
8. Separate ingestion, filtering, extraction, validation, aggregation, metrics and export into clear functions/modules.
9. Add type hints and docstrings to non-trivial functions.
10. Prefer deterministic scripts over manual notebook-only workflows.
11. Store date boundaries and format mappings in one configuration location.
12. Write tests for edge cases before processing the full archive.
13. Run tests after every material change.
14. Do not suppress warnings that may indicate missing or malformed data.
15. Use explicit logging and save logs.
16. Record software versions and random seeds.
17. Avoid unnecessary dependencies.
18. Do not make external requests except to obtain required public source data/documentation.
19. Do not change the project definition without asking the user.
20. If the data cannot support a requirement, stop, explain the evidence and propose the smallest defensible adjustment.
21. At the end of each stage, report what was created, tests run, pass/fail status and unresolved issues.
22. Never fabricate completion or claim validation that was not performed.

---

# **Guiding principle:**

correctness, traceability, reproducibility and defensible interpretation are more important than producing results quickly or adding more methods.
