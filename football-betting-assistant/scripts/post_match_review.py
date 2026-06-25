#!/usr/bin/env python3
"""Attach final scores to a prediction snapshot and compute review metrics."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _match_result(home_goals: int, away_goals: int) -> str:
    if home_goals > away_goals:
        return "胜"
    if home_goals == away_goals:
        return "平"
    return "负"


def _handicap_result(home_goals: int, away_goals: int, line: float) -> str:
    adjusted = home_goals + line - away_goals
    if adjusted > 0:
        return "让胜"
    if adjusted == 0:
        return "让平"
    return "让负"


def _parse_line(value: Any) -> float | None:
    if value in (None, ""):
        return None
    match = re.search(r"[-+]?\d+(?:\.\d+)?", str(value))
    return float(match.group(0)) if match else None


def _score_set(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if value is None:
        return []
    return [item.strip() for item in re.split(r"/|,|，|\s+", str(value)) if item.strip()]


def _evaluate_leg(leg: dict[str, Any], home_goals: int, away_goals: int) -> dict[str, Any]:
    market = str(leg.get("source_snapshot_market") or leg.get("market") or "")
    selection = str(leg.get("selection") or "")
    final_score = f"{home_goals}:{away_goals}"
    total = home_goals + away_goals
    hit: bool | None = None
    metric = "unknown"

    if market == "match_result" or leg.get("market") == "胜平负":
        metric = "match_result"
        hit = _match_result(home_goals, away_goals) in selection
    elif market == "handicap_match_result" or leg.get("market") == "让球胜平负":
        metric = "handicap_result"
        line = _parse_line(leg.get("source_line"))
        if line is not None:
            hit = _handicap_result(home_goals, away_goals, line) in selection
    elif market in {"total_goals", "总进球"} or leg.get("market") == "总进球":
        metric = "total_goals"
        hit = f"{total}球" in selection or str(total) == selection
    elif market in {"correct_score", "比分"} or leg.get("market") == "比分":
        metric = "correct_score"
        hit = final_score in _score_set(selection)

    return {
        "match": leg.get("match"),
        "market": leg.get("market"),
        "source_snapshot_market": leg.get("source_snapshot_market"),
        "selection": selection,
        "metric": metric,
        "hit": hit,
    }


def build_review(prediction: dict[str, Any], match_name: str, home_goals: int, away_goals: int, result_source: str | None) -> dict[str, Any]:
    data = prediction.get("data") or {}
    model_outputs = data.get("model_outputs") or {}
    analyses = model_outputs.get("match_analyses") or []
    ticket_plans = model_outputs.get("ticket_plans") or []
    final_score = f"{home_goals}:{away_goals}"
    score_candidates: list[str] = []
    for analysis in analyses:
        if analysis.get("match") == match_name:
            score_candidates = _score_set(analysis.get("score_candidates"))
            break

    evaluated_legs = []
    for plan in ticket_plans:
        for leg in plan.get("legs", []) or []:
            if leg.get("match") == match_name:
                evaluated_legs.append(_evaluate_leg(leg, home_goals, away_goals))

    score_top1_hit = bool(score_candidates[:1] and final_score == score_candidates[0])
    score_top3_hit = final_score in score_candidates[:3]
    score_coverage_hit = final_score in score_candidates

    return {
        "kind": "post_match_review",
        "data": {
            "report_id": data.get("report_id"),
            "reviewed_at": _now(),
            "source_prediction_snapshot": data.get("report_id"),
            "result_source": result_source or "user-provided",
            "match": match_name,
            "final_score": {
                "home_goals": home_goals,
                "away_goals": away_goals,
                "score": final_score,
                "match_result": _match_result(home_goals, away_goals),
                "total_goals": home_goals + away_goals,
            },
            "score_review": {
                "candidates": score_candidates,
                "top1_hit": score_top1_hit,
                "top3_hit": score_top3_hit,
                "coverage_hit": score_coverage_hit,
            },
            "leg_reviews": evaluated_legs,
            "grade_breakdown_fields": {
                "reference_grade": None,
                "model_confidence": None,
                "data_confidence": None,
                "market_type": None,
            },
        },
    }


def write_unique(path: Path, document: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    target = path
    for index in range(2, 1000):
        if not target.exists():
            break
        target = path.with_name(f"{path.stem}-{index}{path.suffix}")
    target.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Build post-match review from a prediction snapshot and final score.")
    parser.add_argument("prediction_snapshot", type=Path)
    parser.add_argument("--match", required=True)
    parser.add_argument("--home-goals", type=int, required=True)
    parser.add_argument("--away-goals", type=int, required=True)
    parser.add_argument("--result-source")
    parser.add_argument("--out-dir", type=Path, default=Path("data/football/reviews"))
    args = parser.parse_args()

    if args.home_goals < 0 or args.away_goals < 0:
        parser.error("goals must be non-negative")
        return 2
    prediction = json.loads(args.prediction_snapshot.read_text(encoding="utf-8"))
    if prediction.get("kind") != "prediction_snapshot":
        parser.error("input kind must be prediction_snapshot")
        return 2
    review = build_review(prediction, args.match, args.home_goals, args.away_goals, args.result_source)
    report_id = review["data"].get("report_id") or "unknown-report"
    path = write_unique(args.out_dir / f"{report_id}.review.json", review)
    print(json.dumps({"review_path": str(path), "review": review["data"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
