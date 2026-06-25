#!/usr/bin/env python3
"""Analyze correct-score concentration and coverage quality."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _score_sort_key(item: dict[str, Any]) -> float:
    return float(item.get("probability") or 0.0)


def _normalize_scores(document: dict[str, Any]) -> list[dict[str, Any]]:
    raw_scores = document.get("score_matrix") or document.get("top_scores") or document.get("scores")
    if not isinstance(raw_scores, list) or not raw_scores:
        raise ValueError("score_matrix, top_scores, or scores must be a non-empty list")
    scores: list[dict[str, Any]] = []
    for item in raw_scores:
        if not isinstance(item, dict):
            continue
        score = item.get("score")
        probability = item.get("probability")
        if score is None or probability is None:
            continue
        probability_value = float(probability)
        if probability_value < 0:
            raise ValueError("score probabilities must be non-negative")
        scores.append({"score": str(score), "probability": probability_value})
    if not scores:
        raise ValueError("no valid score/probability entries found")
    return sorted(scores, key=_score_sort_key, reverse=True)


def analyze_scores(scores: list[dict[str, Any]], total_xg: float | None = None, both_teams_score_path: bool = False) -> dict[str, Any]:
    top1 = sum(item["probability"] for item in scores[:1])
    top3 = sum(item["probability"] for item in scores[:3])
    top5 = sum(item["probability"] for item in scores[:5])
    warnings: list[str] = []

    if top1 < 0.10:
        single_score_strength = "weak"
        warnings.append("Top 1 score below 10%; do not label a single correct score as strong.")
    elif top1 < 0.14:
        single_score_strength = "moderate"
    else:
        single_score_strength = "strong"

    if top3 < 0.25:
        coverage_quality = "weak"
        warnings.append("Top 3 cumulative probability below 25%; score coverage is weak.")
    elif top5 < 0.33:
        coverage_quality = "moderate"
        warnings.append("Top 4-5 cumulative probability below 33%; score tickets should not be core portfolio.")
    else:
        coverage_quality = "strong"

    if total_xg is not None and total_xg >= 3.2:
        warnings.append("High total xG widens the score distribution; downgrade exact-score confidence.")
        if coverage_quality == "strong":
            coverage_quality = "moderate"
        elif coverage_quality == "moderate":
            coverage_quality = "weak"
    if both_teams_score_path:
        warnings.append("Both teams have a credible scoring path; include conceded-goal protection or downgrade coverage.")
        if single_score_strength == "strong":
            single_score_strength = "moderate"

    core_scores = [item["score"] for item in scores[: min(3, len(scores))]]
    enhanced_scores = [item["score"] for item in scores[: min(5, len(scores))]]
    return {
        "top1_probability": round(top1, 6),
        "top3_probability": round(top3, 6),
        "top5_probability": round(top5, 6),
        "single_score_strength": single_score_strength,
        "coverage_quality": coverage_quality,
        "core_portfolio_allowed": coverage_quality == "strong",
        "exact_score_ticket_allowed": coverage_quality in {"strong", "moderate"},
        "primary_path": core_scores[0] if core_scores else None,
        "secondary_path": " / ".join(core_scores[1:]) if len(core_scores) > 1 else "无明显次路径",
        "missed_path_protection": " / ".join(enhanced_scores[3:]) if len(enhanced_scores) > 3 else "无明显补洞路径",
        "core_scores": core_scores,
        "enhanced_scores": enhanced_scores,
        "warnings": warnings,
    }


def calculate(document: dict[str, Any]) -> dict[str, Any]:
    scores = _normalize_scores(document)
    analysis = analyze_scores(
        scores,
        total_xg=document.get("total_xg"),
        both_teams_score_path=bool(document.get("both_teams_score_path", False)),
    )
    return {
        "kind": "score_coverage_record",
        "score_coverage": analysis,
        "notes": [
            "Single top score below 10% cannot be labelled a strong score pick.",
            "Top 3 below 25% is weak score coverage.",
            "Top 4-5 below 33% prevents exact-score tickets from becoming the core portfolio.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze correct-score concentration and coverage quality.")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    try:
        document = json.loads(args.path.read_text(encoding="utf-8"))
        result = calculate(document)
    except (json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
