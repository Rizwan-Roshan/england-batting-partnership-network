"""Synthetic Cricsheet-shaped fixtures with hand-computed expected values."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

REGISTRY = {"A One": "id_a", "B Two": "id_b", "C Three": "id_c", "D Four": "id_d",
            "E Five": "id_e", "A. One": "id_a", "A One Jr": "id_a2", "R Roster": "id_r"}


def ball(batter, non_striker, total=0, batter_runs=None, extras=0, wickets=None, **extra):
    """One delivery. ``total`` is runs.total; batter runs default to total - extras."""
    d = {"batter": batter, "non_striker": non_striker, "bowler": "X Bowler",
         "runs": {"batter": total - extras if batter_runs is None else batter_runs,
                  "extras": extras, "total": total}}
    if wickets:
        d["wickets"] = [{"player_out": p, "kind": k} for p, k in wickets]
    d.update(extra)
    return d


def innings(deliveries, team="England", per_over=6, **extra):
    overs = [{"over": i // per_over, "deliveries": deliveries[i:i + per_over]}
             for i in range(0, len(deliveries), per_over)]
    return {"team": team, "overs": overs, **extra}


def match(innings_list, date="2022-06-01", match_type="ODI", gender="male",
          team_type="international", teams=("England", "Australia"), players=None):
    return {
        "meta": {"data_version": "1.3.0", "created": "2022-06-02", "revision": 1},
        "info": {"dates": [date], "gender": gender, "team_type": team_type,
                 "match_type": match_type, "teams": list(teams), "outcome": {},
                 "players": players or {}, "registry": {"people": dict(REGISTRY)}},
        "innings": innings_list,
    }
