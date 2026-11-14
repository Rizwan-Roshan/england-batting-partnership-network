"""Glue between stages: turns match files into the tables each stage saves."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from . import config
from .extract import extract_innings
from .filters import exclusion_reason, match_metadata
from .ingest import load_match


def audit_matches(paths: Iterable[Path]) -> pd.DataFrame:
    """Metadata for every source file plus ``included`` / ``exclusion_reason``."""
    rows = []
    for path in paths:
        try:
            meta = match_metadata(load_match(path), path.name)
            reason = exclusion_reason(meta)
        except Exception as exc:  # malformed file: logged, never skipped silently
            meta = {"match_id": path.stem, "filename": path.name}
            reason = f"unreadable:{type(exc).__name__}"
        meta["included"] = reason == ""
        meta["exclusion_reason"] = reason
        rows.append(meta)
    return pd.DataFrame(rows)


def extract_match(match: dict[str, Any], meta: dict[str, Any]) -> tuple[list[dict], list[dict], list[dict]]:
    """Extract England's partnerships from one qualifying match.

    Returns (observation rows, innings rows, warning rows). Super-over innings
    are not qualifying innings: they are listed in the innings table with
    ``qualifying = False`` and produce no observations.
    """
    registry = match["info"].get("registry", {}).get("people", {})
    obs_rows: list[dict] = []
    inn_rows: list[dict] = []
    warn_rows: list[dict] = []
    for idx, innings in enumerate(match.get("innings", []), start=1):
        if innings.get("team") != config.TEAM:
            continue
        super_over = bool(innings.get("super_over", False))
        pen = innings.get("penalty_runs", {}) or {}
        row = {
            "match_id": meta["match_id"], "format": meta["format"], "match_date": meta["start_date"],
            "innings_index": idx, "batting_team": innings.get("team"),
            "qualifying": not super_over, "super_over": super_over,
            "declared": bool(innings.get("declared", False)),
            "forfeited": bool(innings.get("forfeited", False)),
            "absent_hurt": "|".join(innings.get("absent_hurt", []) or []),
            "penalty_runs_pre": int(pen.get("pre", 0)), "penalty_runs_post": int(pen.get("post", 0)),
            "runs_from_deliveries": 0, "partnership_runs_sum": 0, "wicket_records": 0,
            "delivery_count": 0, "n_partnerships": 0,
        }
        if not super_over:
            res = extract_innings(innings, registry, meta["match_id"], idx)
            for o in res.observations:
                r = o.to_row()
                r.update(format=meta["format"], match_date=meta["start_date"],
                         source_file=meta["filename"], batting_team=innings.get("team"))
                obs_rows.append(r)
            for w in res.warnings:
                w.update(format=meta["format"], source_file=meta["filename"])
                warn_rows.append(w)
            row.update(
                runs_from_deliveries=res.runs_from_deliveries,
                partnership_runs_sum=sum(o.partnership_runs for o in res.observations),
                wicket_records=res.wicket_records, delivery_count=res.delivery_count,
                n_partnerships=len(res.observations),
            )
        inn_rows.append(row)
    return obs_rows, inn_rows, warn_rows


OBS_COLUMNS = [
    "match_id", "source_file", "match_date", "format", "innings_index", "batting_team",
    "partnership_seq", "player_1_id", "player_1_name", "player_2_id", "player_2_name",
    "partnership_runs", "batter_runs", "extras_runs", "deliveries",
    "start_delivery_id", "end_delivery_id", "boundary_reason", "quality_status",
]
WARN_COLUMNS = ["match_id", "source_file", "format", "innings_index", "delivery_id", "code", "detail"]


def extract_all(included: pd.DataFrame, json_dir: Path = config.RAW_JSON_DIR) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Run the extractor over every included match."""
    obs: list[dict] = []
    inn: list[dict] = []
    warn: list[dict] = []
    for meta in included.to_dict("records"):
        o, i, w = extract_match(load_match(json_dir / meta["filename"]), meta)
        obs += o
        inn += i
        warn += w
    return (
        pd.DataFrame(obs, columns=OBS_COLUMNS),
        pd.DataFrame(inn),
        pd.DataFrame(warn, columns=WARN_COLUMNS),
    )
