"""Stage 2 - match filters with a full inclusion/exclusion audit."""
from __future__ import annotations

from datetime import date
from typing import Any

from . import config


def parse_date(value: Any) -> date:
    """Parse a Cricsheet date (ISO string, or a date object from YAML-like input)."""
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def match_metadata(match: dict[str, Any], filename: str) -> dict[str, Any]:
    """Normalise the metadata of one match into a flat record."""
    info = match["info"]
    dates = [parse_date(d) for d in info.get("dates", [])]
    teams = list(info.get("teams", []))
    outcome = info.get("outcome", {})
    event = info.get("event", {}) or {}
    return {
        "match_id": filename.rsplit(".", 1)[0],
        "filename": filename,
        "start_date": min(dates) if dates else None,
        "end_date": max(dates) if dates else None,
        "gender": info.get("gender"),
        "team_type": info.get("team_type"),
        "match_type": info.get("match_type"),
        "format": config.FORMAT_MAP.get(info.get("match_type", ""), ""),
        "team_1": teams[0] if len(teams) > 0 else "",
        "team_2": teams[1] if len(teams) > 1 else "",
        "opponent": next((t for t in teams if t != config.TEAM), ""),
        "event": event.get("name", ""),
        "venue": info.get("venue", ""),
        "outcome_winner": outcome.get("winner", ""),
        "outcome_result": outcome.get("result", ""),
        "outcome_method": outcome.get("method", ""),
        "n_innings_total": len(match.get("innings", [])),
        "n_innings_england": sum(1 for i in match.get("innings", []) if i.get("team") == config.TEAM),
    }


def exclusion_reason(meta: dict[str, Any]) -> str:
    """Return '' when the match qualifies, otherwise the first failing filter.

    Filters are applied in a fixed order so every excluded file has exactly one
    documented reason.
    """
    if meta["gender"] != config.GENDER:
        return "gender_not_male"
    if meta["team_type"] != config.TEAM_TYPE:
        return "not_international"
    if config.TEAM not in (meta["team_1"], meta["team_2"]):
        return "england_not_playing"
    if not meta["format"]:
        return "format_not_target"
    if meta["start_date"] is None:
        return "missing_date"
    if meta["start_date"] < config.DATE_START:
        return "before_window"
    if meta["start_date"] > config.DATE_END:
        return "after_window"
    return ""
