#!/usr/bin/env python3
"""Select matches from a normalized football snapshot.

This helper is intentionally small: it gives the assistant a deterministic way
to filter Sporttery snapshots by Beijing date, lottery match number, team, or
competition before model analysis.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


BEIJING = ZoneInfo("Asia/Shanghai")


def _load_snapshot(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("kind") != "football_snapshot":
        raise ValueError("snapshot kind must be football_snapshot")
    return document["data"]


def _parse_dt(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value).astimezone(BEIJING)


def _target_date(value: str | None) -> str | None:
    if not value:
        return None
    now = datetime.now(BEIJING)
    if value == "today":
        return now.date().isoformat()
    if value == "tomorrow":
        return (now + timedelta(days=1)).date().isoformat()
    return datetime.fromisoformat(value).date().isoformat()


def _contains(haystack: str | None, needle: str | None) -> bool:
    if not needle:
        return True
    return needle.lower() in (haystack or "").lower()


def select_matches(
    snapshot: dict[str, Any],
    *,
    date: str | None = None,
    match_no: str | None = None,
    team: str | None = None,
    competition: str | None = None,
) -> list[dict[str, Any]]:
    wanted_date = _target_date(date)
    selected: list[dict[str, Any]] = []
    for match in snapshot.get("matches", []):
        if match_no and match.get("match_no") != match_no:
            continue
        if competition and not _contains(match.get("competition"), competition):
            continue
        if team and not (_contains(match.get("home_team"), team) or _contains(match.get("away_team"), team)):
            continue
        if wanted_date:
            try:
                kickoff_date = _parse_dt(match["kickoff_time"]).date().isoformat()
            except (KeyError, ValueError):
                continue
            if kickoff_date != wanted_date:
                continue
        selected.append(match)
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description="Select matches from a normalized football snapshot.")
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--date", help="today, tomorrow, or YYYY-MM-DD in Beijing time")
    parser.add_argument("--match-no")
    parser.add_argument("--team")
    parser.add_argument("--competition")
    args = parser.parse_args()

    snapshot = _load_snapshot(args.snapshot)
    matches = select_matches(
        snapshot,
        date=args.date,
        match_no=args.match_no,
        team=args.team,
        competition=args.competition,
    )
    output = {
        "snapshot_id": snapshot.get("snapshot_id"),
        "selected_count": len(matches),
        "matches": matches,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if matches else 2


if __name__ == "__main__":
    raise SystemExit(main())
