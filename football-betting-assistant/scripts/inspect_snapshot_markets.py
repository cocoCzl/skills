#!/usr/bin/env python3
"""Inspect buyable market availability in a football snapshot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


CORE_MARKETS = {"match_result", "handicap_match_result", "correct_score", "over_under", "total_goals"}


def _load(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("kind") != "football_snapshot":
        raise ValueError("snapshot kind must be football_snapshot")
    return document["data"]


def inspect_match(match: dict[str, Any]) -> dict[str, Any]:
    buyable: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    for market in match.get("markets", []):
        market_name = market.get("market")
        if market_name not in CORE_MARKETS:
            continue
        availability = market.get("availability") or {}
        selections = market.get("selections") or []
        item = {
            "market": market_name,
            "source_market_name": market.get("source_market_name"),
            "line": market.get("line"),
            "status": availability.get("status"),
            "reason": availability.get("reason"),
            "selection_count": len(selections),
        }
        if availability.get("status") == "available" and selections:
            buyable.append(item)
        else:
            blocked.append(item)
    needs_user_odds = not buyable
    return {
        "match_id": match.get("match_id"),
        "match_no": match.get("match_no"),
        "home_team": match.get("home_team"),
        "away_team": match.get("away_team"),
        "kickoff_time": match.get("kickoff_time"),
        "buyable_markets": buyable,
        "blocked_markets": blocked,
        "needs_user_odds": needs_user_odds,
        "can_build_purchase_plan": bool(buyable),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect buyable market availability in a football snapshot.")
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--match-no")
    args = parser.parse_args()

    snapshot = _load(args.snapshot)
    matches = snapshot.get("matches", [])
    if args.match_no:
        matches = [match for match in matches if match.get("match_no") == args.match_no]
    report = {
        "snapshot_id": snapshot.get("snapshot_id"),
        "provider": snapshot.get("provider"),
        "matches": [inspect_match(match) for match in matches],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.match_no and not report["matches"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
