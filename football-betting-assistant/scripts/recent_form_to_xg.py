#!/usr/bin/env python3
"""Convert recent-form aggregates into lower-precision xG prior inputs."""

from __future__ import annotations

import argparse
import json
from typing import Any


WINDOWS = {
    "club": {"min_matches": 5, "preferred_matches": 10, "confidence_cap": "B"},
    "national": {"min_matches": 4, "preferred_matches": 8, "confidence_cap": "B"},
    "unknown": {"min_matches": 5, "preferred_matches": 10, "confidence_cap": "C"},
}


def _rate(total: float, matches: int) -> float:
    return round(total / matches, 3)


def convert_recent_form(
    *,
    team_type: str,
    matches: int,
    goals_for: float | None = None,
    goals_against: float | None = None,
    xg_for: float | None = None,
    xg_against: float | None = None,
) -> dict[str, Any]:
    if matches <= 0:
        raise ValueError("matches must be greater than zero")
    if team_type not in WINDOWS:
        raise ValueError("team_type must be one of club, national, unknown")

    rules = WINDOWS[team_type]
    notes: list[str] = []
    if xg_for is not None and xg_against is not None:
        source_precision = "xg"
        output_xg_for = _rate(float(xg_for), matches)
        output_xg_against = _rate(float(xg_against), matches)
        notes.append("Used xG/xGA aggregates as preferred recent-form inputs.")
    elif goals_for is not None and goals_against is not None:
        source_precision = "goals_proxy"
        output_xg_for = _rate(float(goals_for), matches)
        output_xg_against = _rate(float(goals_against), matches)
        notes.append("Used goals for/against as lower-precision proxy because xG/xGA were unavailable.")
    else:
        raise ValueError("provide either xg_for/xg_against or goals_for/goals_against")

    confidence_cap = rules["confidence_cap"]
    if source_precision == "goals_proxy" and confidence_cap == "B":
        confidence_cap = "C"
    if matches < rules["min_matches"]:
        confidence_cap = "C"
        notes.append(f"Recent-form sample below minimum {rules['min_matches']} matches.")
    elif matches < rules["preferred_matches"]:
        notes.append(f"Recent-form sample below preferred {rules['preferred_matches']} matches.")

    return {
        "team_type": team_type,
        "matches": matches,
        "preferred_matches": rules["preferred_matches"],
        "source_precision": source_precision,
        "xg_for": output_xg_for,
        "xg_against": output_xg_against,
        "confidence_cap": confidence_cap,
        "notes": notes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert recent-form aggregates into xG prior inputs.")
    parser.add_argument("--team-type", choices=sorted(WINDOWS), required=True)
    parser.add_argument("--matches", type=int, required=True)
    parser.add_argument("--goals-for", type=float)
    parser.add_argument("--goals-against", type=float)
    parser.add_argument("--xg-for", type=float)
    parser.add_argument("--xg-against", type=float)
    args = parser.parse_args()

    try:
        result = convert_recent_form(
            team_type=args.team_type,
            matches=args.matches,
            goals_for=args.goals_for,
            goals_against=args.goals_against,
            xg_for=args.xg_for,
            xg_against=args.xg_against,
        )
    except ValueError as exc:
        parser.error(str(exc))
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
