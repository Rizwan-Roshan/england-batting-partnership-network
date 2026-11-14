"""Stage 3 - stateful, auditable batting-partnership extraction.

A partnership is the period in an innings during which one unordered pair of
batters shares the crease. The extractor walks deliveries in source order
(innings -> over -> delivery) and keeps the current pair as explicit state.

Boundary rules
--------------
* Runs: ``runs.total`` of every delivery is added exactly once to the pair at
  the crease for that delivery (this already contains the extras).
* A delivery carrying a wicket record whose ``player_out`` is one of the
  current pair closes the partnership *after* the delivery is processed.
  No allow-list of dismissal kinds is used: any wicket record removes the
  named player. Kinds starting with ``retired`` are labelled as retirements.
* If the pair changes without such a record, the extractor looks for a
  batter replacement record; failing that the change is logged as
  ``unexplained_pair_change`` - the old pair is never carried forward silently.
* The open partnership is closed exactly once at the end of the innings.
* A pair that separates and later reunites yields separate observations.
* Innings-level penalty runs are reported by the caller, never given to a pair.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Observation:
    """One partnership occurrence (one pair, one uninterrupted stay)."""

    match_id: str
    innings_index: int  # 1-based position of the innings in the match file
    partnership_seq: int  # 1-based order within the innings
    player_1_id: str
    player_1_name: str
    player_2_id: str
    player_2_name: str
    partnership_runs: int = 0
    batter_runs: int = 0
    extras_runs: int = 0
    deliveries: int = 0  # every delivery record, including wides and no-balls
    start_delivery_id: str = ""
    end_delivery_id: str = ""
    boundary_reason: str = ""
    quality_status: str = "ok"

    def to_row(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class InningsResult:
    """Extractor output for one innings."""

    observations: list[Observation] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)
    runs_from_deliveries: int = 0
    wicket_records: int = 0
    delivery_count: int = 0


def delivery_id(innings_index: int, over: int, ball_seq: int) -> str:
    """Stable identifier: innings index, 0-based over, 1-based position in over."""
    return f"{innings_index}.{over}.{ball_seq}"


def _retirement(kind: str) -> bool:
    return kind.lower().startswith("retired")


def _batter_replacement(delivery: dict[str, Any], names_out: set[str]) -> bool:
    """True if the delivery records a replacement removing one of ``names_out``."""
    repl = delivery.get("replacements", {}) or {}
    for rec in repl.get("role", []) or []:
        if rec.get("role") == "batter" and rec.get("out") in names_out:
            return True
    for rec in repl.get("match", []) or []:
        if rec.get("out") in names_out:
            return True
    return False


def extract_innings(
    innings: dict[str, Any],
    registry: dict[str, str],
    match_id: str,
    innings_index: int,
) -> InningsResult:
    """Extract the partnership observations of one innings.

    Parameters
    ----------
    innings: Cricsheet innings object (``team``, ``overs`` ...).
    registry: ``info.registry.people`` - maps the name used in the file to the
        stable Cricsheet person identifier.
    match_id, innings_index: identify the innings in the output rows.
    """
    res = InningsResult()

    def warn(code: str, did: str, detail: str) -> None:
        res.warnings.append(
            {"match_id": match_id, "innings_index": innings_index, "delivery_id": did,
             "code": code, "detail": detail}
        )

    def pid(name: str, did: str) -> str:
        if name in registry:
            return registry[name]
        warn("player_not_in_registry", did, name)
        return f"unresolved:{name}"

    cur: Observation | None = None
    cur_names: set[str] = set()
    last_delivery: dict[str, Any] | None = None
    # State remembered after a wicket closed a partnership, to validate the
    # transition on the next delivery.
    pending_out: list[tuple[str, str]] = []  # (player name, kind)

    def open_obs(a: str, b: str, did: str) -> Observation:
        ids = sorted([(pid(a, did), a), (pid(b, did), b)])
        return Observation(
            match_id=match_id,
            innings_index=innings_index,
            partnership_seq=len(res.observations) + 1,
            player_1_id=ids[0][0], player_1_name=ids[0][1],
            player_2_id=ids[1][0], player_2_name=ids[1][1],
            start_delivery_id=did,
        )

    def close_obs(reason: str, status: str = "ok") -> None:
        nonlocal cur, cur_names
        assert cur is not None
        cur.boundary_reason = reason
        if status != "ok":
            cur.quality_status = status
        res.observations.append(cur)
        cur, cur_names = None, set()

    for over in innings.get("overs", []):
        over_no = over.get("over")
        for seq, d in enumerate(over.get("deliveries", []), start=1):
            did = delivery_id(innings_index, over_no, seq)
            names = {d["batter"], d["non_striker"]}
            res.delivery_count += 1
            if len(names) != 2:
                warn("batter_equals_non_striker", did, d["batter"])
                # Cannot form a pair: runs are still counted for the innings.
                res.runs_from_deliveries += int(d["runs"]["total"])
                continue

            # --- validate the transition after a wicket -------------------
            if pending_out:
                for name, kind in pending_out:
                    if name in names:
                        warn("player_out_still_at_crease", did, f"{name} ({kind})")
                pending_out = []

            # --- pair changed without a closing wicket record -------------
            if cur is not None and names != cur_names:
                leaving = cur_names - names
                replaced = _batter_replacement(d, leaving) or (
                    last_delivery is not None and _batter_replacement(last_delivery, leaving)
                )
                if replaced:
                    close_obs("replacement")
                else:
                    warn("unexplained_pair_change", did,
                         f"{sorted(cur_names)} -> {sorted(names)}")
                    close_obs("unexplained_pair_change", "warning")

            if cur is None:
                cur = open_obs(d["batter"], d["non_striker"], did)
                cur_names = names

            # --- runs: runs.total exactly once ----------------------------
            runs = d["runs"]
            cur.partnership_runs += int(runs["total"])
            cur.batter_runs += int(runs.get("batter", 0))
            cur.extras_runs += int(runs.get("extras", 0))
            cur.deliveries += 1
            cur.end_delivery_id = did
            res.runs_from_deliveries += int(runs["total"])

            # --- wickets: handle every record on the delivery -------------
            wickets = d.get("wickets", []) or []
            res.wicket_records += len(wickets)
            exits = []
            for w in wickets:
                name, kind = w.get("player_out", ""), str(w.get("kind", "unknown"))
                if name in cur_names:
                    exits.append((name, kind))
                else:
                    warn("player_out_not_at_crease", did, f"{name} ({kind})")
            if exits:
                kinds = "+".join(k for _, k in exits)
                prefix = "retirement" if all(_retirement(k) for _, k in exits) else "dismissal"
                pending_out = exits
                close_obs(f"{prefix}:{kinds}")
            last_delivery = d

    if cur is not None:
        close_obs("innings_end")
    return res
