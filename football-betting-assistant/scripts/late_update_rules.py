#!/usr/bin/env python3
"""Evaluate late-update, odds-movement, and kickoff stop rules."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


def _parse_time(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)


def _odds_delta(opening: float | None, current: float | None) -> float | None:
    if opening is None or current is None:
        return None
    return abs(float(current) - float(opening))


def evaluate(document: dict[str, Any]) -> dict[str, Any]:
    now = _parse_time(str(document["observed_at"]))
    kickoff = _parse_time(str(document["kickoff_time"]))
    hours_to_kickoff = (kickoff - now).total_seconds() / 3600
    sales_available = bool(document.get("sales_available", True))
    lineup_status = str(document.get("lineup_status") or "expected")

    stop_new_purchase_plan = hours_to_kickoff <= 0 or not sales_available
    warnings: list[str] = []
    reevaluation_required = False
    grade_cap = None

    if hours_to_kickoff > 12:
        grade_cap = "B"
        warnings.append("More than 12 hours before kickoff; early analysis is capped at B.")
    elif 2 <= hours_to_kickoff <= 6:
        warnings.append("Two to six hours before kickoff; attempt injury, lineup, and market updates.")
    elif 0 < hours_to_kickoff <= 1 and lineup_status != "confirmed":
        grade_cap = "B" if lineup_status == "unconfirmed" else "C"
        warnings.append("Within 60 minutes of kickoff without confirmed lineup; A grade unavailable.")

    if stop_new_purchase_plan:
        grade_cap = "Pass"
        warnings.append("Match already started or sales availability cannot be confirmed; do not create new pre-match purchase plans.")

    result_delta = _odds_delta(document.get("opening_match_result_odds"), document.get("current_match_result_odds"))
    if result_delta is not None:
        if result_delta >= 0.15:
            reevaluation_required = True
            warnings.append("Material match-result odds movement >= 0.15; reevaluation required.")
        elif result_delta >= 0.08:
            warnings.append("Light match-result odds movement >= 0.08; add movement warning.")

    for key, label in (("handicap_line_moved", "Handicap line movement"), ("total_goals_line_moved", "Total-goals line movement")):
        if document.get(key):
            reevaluation_required = True
            warnings.append(f"{label} detected; reevaluation required.")

    return {
        "kind": "late_update_record",
        "hours_to_kickoff": round(hours_to_kickoff, 3),
        "grade_cap": grade_cap,
        "reevaluation_required": reevaluation_required,
        "stop_new_purchase_plan": stop_new_purchase_plan,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate late-update and kickoff stop rules.")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    try:
        document = json.loads(args.path.read_text(encoding="utf-8"))
        result = evaluate(document)
    except (json.JSONDecodeError, KeyError, ValueError) as exc:
        parser.error(str(exc))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
