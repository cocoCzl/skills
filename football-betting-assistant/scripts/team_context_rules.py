#!/usr/bin/env python3
"""Classify football team context for model parameter selection."""

from __future__ import annotations

import argparse
import json
from typing import Any


SUPPORTED_TEAM_TYPES = {"club", "national", "unknown"}
ALL_TEAM_TYPES = SUPPORTED_TEAM_TYPES | {"unsupported"}

YOUTH_MARKERS = (
    "u17",
    "u18",
    "u19",
    "u20",
    "u21",
    "u23",
    "u-17",
    "u-18",
    "u-19",
    "u-20",
    "u-21",
    "u-23",
    "青年",
    "青年队",
    "预备队",
)
WOMEN_MARKERS = ("women", "woman", "女子", "女足", "女队")
NATIONAL_MARKERS = (
    "世界杯",
    "欧洲杯",
    "亚洲杯",
    "美洲杯",
    "非洲杯",
    "国家队",
    "世预赛",
    "欧国联",
    "中北美金杯",
    "国际友谊",
)
CLUB_MARKERS = (
    "英超",
    "西甲",
    "意甲",
    "德甲",
    "法甲",
    "欧冠",
    "欧联",
    "欧协联",
    "中超",
    "日职",
    "韩职",
    "美职",
    "解放者杯",
)


def _haystack(*values: str | None) -> str:
    return " ".join(value for value in values if value).lower()


def classify_team_context(
    *,
    competition: str | None = None,
    home_team: str | None = None,
    away_team: str | None = None,
    explicit_team_type: str | None = None,
) -> dict[str, Any]:
    """Return team-type and model-parameter guidance.

    The rules intentionally prefer conservative `unknown` over guessing club or
    national context when the competition name is not enough.
    """

    explicit = (explicit_team_type or "").strip().lower()
    text = _haystack(competition, home_team, away_team)
    if explicit in ALL_TEAM_TYPES:
        team_type = explicit
        reason = "explicit"
    elif any(marker in text for marker in YOUTH_MARKERS):
        team_type = "unsupported"
        reason = "youth_team"
    elif any(marker in text for marker in WOMEN_MARKERS):
        team_type = "unsupported"
        reason = "women_team"
    elif any(marker.lower() in text for marker in NATIONAL_MARKERS):
        team_type = "national"
        reason = "national_competition"
    elif any(marker.lower() in text for marker in CLUB_MARKERS):
        team_type = "club"
        reason = "club_competition"
    else:
        team_type = "unknown"
        reason = "insufficient_competition_context"

    if team_type == "club":
        parameter_pool = "club"
        confidence_cap = "B"
        formal_purchase_allowed = True
    elif team_type == "national":
        parameter_pool = "national"
        confidence_cap = "B"
        formal_purchase_allowed = True
    elif team_type == "unknown":
        parameter_pool = "same-type-default-required"
        confidence_cap = "C"
        formal_purchase_allowed = True
    else:
        parameter_pool = "unsupported"
        confidence_cap = "Pass"
        formal_purchase_allowed = False

    return {
        "team_type": team_type,
        "reason": reason,
        "parameter_pool": parameter_pool,
        "confidence_cap": confidence_cap,
        "formal_purchase_allowed": formal_purchase_allowed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify team context for football model parameters.")
    parser.add_argument("--competition")
    parser.add_argument("--home-team")
    parser.add_argument("--away-team")
    parser.add_argument("--team-type")
    args = parser.parse_args()

    result = classify_team_context(
        competition=args.competition,
        home_team=args.home_team,
        away_team=args.away_team,
        explicit_team_type=args.team_type,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
