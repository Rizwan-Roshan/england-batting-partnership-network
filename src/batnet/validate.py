"""Stage 4 - validation of the partnership observations.

The innings totals used here are recomputed straight from the raw JSON by a
code path that does not use the extractor, and are compared with match-level
facts recorded independently by Cricsheet (targets and winning margins).
"""
from __future__ import annotations

from typing import Any

import pandas as pd

from . import config


def raw_innings_totals(match: dict[str, Any]) -> list[dict[str, Any]]:
    """Per innings: team, delivery runs, penalty runs, wickets (no extractor)."""
    out = []
    for idx, inn in enumerate(match.get("innings", []), start=1):
        runs = sum(d["runs"]["total"] for o in inn.get("overs", []) for d in o["deliveries"])
        pen = inn.get("penalty_runs", {}) or {}
        out.append({
            "innings_index": idx, "team": inn.get("team"), "delivery_runs": runs,
            "penalty": int(pen.get("pre", 0)) + int(pen.get("post", 0)),
            "super_over": bool(inn.get("super_over", False)),
            "target": (inn.get("target") or {}).get("runs"),
        })
    return out


def scorecard_checks(match: dict[str, Any], match_id: str, fmt: str) -> list[dict[str, Any]]:
    """Compare recomputed innings totals with the recorded target / margin.

    Only matches without a rain-adjustment method are checked, because an
    adjusted target is not a function of the first-innings total.
    """
    info = match["info"]
    outcome = info.get("outcome", {})
    inns = [i for i in raw_innings_totals(match) if not i["super_over"]]
    checks: list[dict[str, Any]] = []
    if not inns or outcome.get("method"):
        return checks
    total = {t: 0 for t in info["teams"]}
    for k, inn in enumerate(inns):
        # Target recorded on this innings = opponents' aggregate lead + 1.
        if inn["target"] is not None and k == len(inns) - 1:
            other = next(t for t in info["teams"] if t != inn["team"])
            expected = total[other] - total[inn["team"]] + 1
            checks.append({"match_id": match_id, "format": fmt, "check": "target",
                           "recorded": int(inn["target"]), "recomputed": int(expected),
                           "passed": int(inn["target"]) == int(expected)})
        total[inn["team"]] += inn["delivery_runs"] + inn["penalty"]
    by = outcome.get("by", {})
    winner = outcome.get("winner")
    if winner and "runs" in by:
        loser = next(t for t in info["teams"] if t != winner)
        margin = total[winner] - total[loser]
        checks.append({"match_id": match_id, "format": fmt, "check": "margin_runs",
                       "recorded": int(by["runs"]), "recomputed": int(margin),
                       "passed": int(by["runs"]) == int(margin)})
    return checks


def observation_checks(obs: pd.DataFrame, innings: pd.DataFrame) -> list[tuple[str, bool, str]]:
    """Structural checks on the observation and innings tables."""
    out: list[tuple[str, bool, str]] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        out.append((name, bool(ok), detail))

    q = innings[innings["qualifying"]]
    add("innings_partnership_runs_equal_delivery_runs",
        (q["partnership_runs_sum"] == q["runs_from_deliveries"]).all(),
        f"{len(q)} qualifying innings, {int(q['runs_from_deliveries'].sum())} runs")
    add("distinct_players_in_pair", (obs["player_1_id"] != obs["player_2_id"]).all())
    add("canonical_pair_order", (obs["player_1_id"] < obs["player_2_id"]).all())
    add("all_player_ids_resolved",
        not (obs["player_1_id"].str.startswith("unresolved") | obs["player_2_id"].str.startswith("unresolved")).any())
    add("runs_non_negative_integers", (obs["partnership_runs"] >= 0).all()
        and pd.api.types.is_integer_dtype(obs["partnership_runs"]))
    add("runs_equal_batter_plus_extras", (obs["partnership_runs"] == obs["batter_runs"] + obs["extras_runs"]).all())
    add("every_observation_has_a_delivery", (obs["deliveries"] >= 1).all())
    g = obs.groupby(["match_id", "innings_index"])
    add("sequence_numbers_contiguous", (g["partnership_seq"].max() == g.size()).all()
        and (g["partnership_seq"].min() == 1).all())
    last = obs["partnership_seq"] == g["partnership_seq"].transform("max")
    add("innings_end_only_on_last_observation", not (obs.loc[~last, "boundary_reason"] == "innings_end").any())
    add("observation_count_matches_innings_table", int(q["n_partnerships"].sum()) == len(obs),
        f"{len(obs)} observations")
    add("only_england_batting", (obs["batting_team"] == config.TEAM).all())
    add("formats_canonical", set(obs["format"]) <= set(config.FORMATS))
    add("dates_inside_window", (obs["match_date"] >= config.DATE_START).all()
        and (obs["match_date"] <= config.DATE_END).all())
    return out


# Partnerships documented in public scorecards / record lists; used as spot
# checks of the extractor against a source that is independent of the code.
SPOT_CHECKS = [
    # (format, ISO start date of match, name fragment 1, name fragment 2, runs)
    ("Test", "2020-08-21", "Crawley", "Buttler", 359),
    ("Test", "2022-07-01", "Root", "Bairstow", 269),
    ("Test", "2022-12-01", "Crawley", "Duckett", 233),
    ("Test", "2024-10-07", "Root", "Brook", 454),
    ("T20I", "2022-11-10", "Buttler", "Hales", 170),
]


def spot_checks(obs: pd.DataFrame) -> pd.DataFrame:
    """Look up each documented partnership in the observation table."""
    rows = []
    for fmt, iso, n1, n2, runs in SPOT_CHECKS:
        day = pd.Timestamp(iso).date()
        o = obs[(obs["format"] == fmt) & (obs["match_date"] == day)]
        both = o["player_1_name"] + "|" + o["player_2_name"]
        hit = o[both.str.contains(n1) & both.str.contains(n2)]
        found = int(hit["partnership_runs"].max()) if len(hit) else None
        rows.append({"format": fmt, "match_date": day, "pair": f"{n1} / {n2}",
                     "documented_runs": runs, "extracted_runs": found, "passed": found == runs})
    return pd.DataFrame(rows)
