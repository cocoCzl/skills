#!/usr/bin/env python3
"""Backtest football prediction samples.

The script expects a JSON document with kind=backtest_samples. It does not
fetch data; it only evaluates historical pre-match predictions against known
full-time results.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

RESULT_KEYS = ("home_win", "draw", "away_win")


def _actual_result_key(home_goals: int, away_goals: int) -> str:
    if home_goals > away_goals:
        return "home_win"
    if home_goals == away_goals:
        return "draw"
    return "away_win"


def _top_key(probabilities: dict[str, float]) -> str:
    return max(RESULT_KEYS, key=lambda key: probabilities.get(key, 0.0))


def _brier(probabilities: dict[str, float], actual_key: str) -> float:
    return sum((probabilities.get(key, 0.0) - (1.0 if key == actual_key else 0.0)) ** 2 for key in RESULT_KEYS)


def _log_loss(probabilities: dict[str, float], actual_key: str) -> float:
    probability = min(max(probabilities.get(actual_key, 0.0), 1e-12), 1.0)
    return -math.log(probability)


def _bucket(probability: float) -> str:
    lower = int(probability * 10) * 10
    upper = min(lower + 10, 100)
    return f"{lower}-{upper}%"


def _over_under_actual(home_goals: int, away_goals: int, line: float) -> str:
    total = home_goals + away_goals
    if total > line:
        return "over"
    if total < line:
        return "under"
    return "push"


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _rate(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def _score_hit(candidates: list[dict[str, Any]], actual_score: str, top_n: int) -> bool:
    return any(item.get("score") == actual_score for item in candidates[:top_n])


def calculate(samples: list[dict[str, Any]]) -> dict[str, Any]:
    result_hits = 0
    ou_hits = 0
    ou_count = 0
    top1_hits = 0
    top3_hits = 0
    coverage_hits = 0
    brier_scores: list[float] = []
    log_losses: list[float] = []
    grade_stats: dict[str, dict[str, int]] = defaultdict(lambda: {"count": 0, "result_hits": 0, "score_top3_hits": 0})
    confidence_stats: dict[str, dict[str, int]] = defaultdict(lambda: {"count": 0, "result_hits": 0})
    bucket_stats: dict[str, dict[str, int]] = defaultdict(lambda: {"count": 0, "hits": 0})
    evaluated_samples: list[dict[str, Any]] = []

    for sample in samples:
        prediction = sample["prediction"]
        actual = sample["actual_result"]
        home_goals = actual["home_goals"]
        away_goals = actual["away_goals"]
        actual_key = _actual_result_key(home_goals, away_goals)
        probabilities = prediction["result_probabilities"]
        predicted_key = _top_key(probabilities)
        result_hit = predicted_key == actual_key
        actual_score = f"{home_goals}:{away_goals}"
        score_candidates = prediction.get("score_candidates", [])
        top1_hit = _score_hit(score_candidates, actual_score, 1)
        top3_hit = _score_hit(score_candidates, actual_score, 3)
        coverage_hit = any(item.get("score") == actual_score for item in score_candidates)

        result_hits += int(result_hit)
        top1_hits += int(top1_hit)
        top3_hits += int(top3_hit)
        coverage_hits += int(coverage_hit)
        brier_scores.append(_brier(probabilities, actual_key))
        log_losses.append(_log_loss(probabilities, actual_key))

        grade = prediction.get("reference_grade", "unknown")
        grade_stats[grade]["count"] += 1
        grade_stats[grade]["result_hits"] += int(result_hit)
        grade_stats[grade]["score_top3_hits"] += int(top3_hit)

        model_confidence = prediction.get("model_confidence", "unknown")
        confidence_stats[model_confidence]["count"] += 1
        confidence_stats[model_confidence]["result_hits"] += int(result_hit)

        predicted_probability = probabilities.get(predicted_key, 0.0)
        bucket_name = _bucket(predicted_probability)
        bucket_stats[bucket_name]["count"] += 1
        bucket_stats[bucket_name]["hits"] += int(result_hit)

        ou_record = prediction.get("over_under_probabilities")
        ou_actual = None
        ou_predicted = None
        ou_hit = None
        if ou_record and "line" in ou_record:
            ou_actual = _over_under_actual(home_goals, away_goals, ou_record["line"])
            if ou_actual != "push":
                ou_predicted = "over" if ou_record.get("over", 0.0) >= ou_record.get("under", 0.0) else "under"
                ou_hit = ou_predicted == ou_actual
                ou_hits += int(ou_hit)
                ou_count += 1

        evaluated_samples.append({
            "sample_id": sample.get("sample_id"),
            "predicted_result": predicted_key,
            "actual_result": actual_key,
            "result_hit": result_hit,
            "actual_score": actual_score,
            "score_top1_hit": top1_hit,
            "score_top3_hit": top3_hit,
            "score_coverage_hit": coverage_hit,
            "over_under_predicted": ou_predicted,
            "over_under_actual": ou_actual,
            "over_under_hit": ou_hit,
            "reference_grade": grade,
            "model_confidence": model_confidence,
            "data_confidence": prediction.get("data_confidence")
        })

    sample_count = len(samples)
    return {
        "sample_count": sample_count,
        "result_hit_rate": _rate(result_hits, sample_count),
        "over_under_hit_rate": _rate(ou_hits, ou_count),
        "over_under_sample_count": ou_count,
        "score_top1_hit_rate": _rate(top1_hits, sample_count),
        "score_top3_hit_rate": _rate(top3_hits, sample_count),
        "score_coverage_hit_rate": _rate(coverage_hits, sample_count),
        "brier_score_mean": _mean(brier_scores),
        "log_loss_mean": _mean(log_losses),
        "grade_breakdown": {
            grade: {
                "count": stats["count"],
                "result_hit_rate": _rate(stats["result_hits"], stats["count"]),
                "score_top3_hit_rate": _rate(stats["score_top3_hits"], stats["count"])
            }
            for grade, stats in sorted(grade_stats.items())
        },
        "model_confidence_breakdown": {
            confidence: {
                "count": stats["count"],
                "result_hit_rate": _rate(stats["result_hits"], stats["count"])
            }
            for confidence, stats in sorted(confidence_stats.items())
        },
        "calibration_buckets": {
            bucket: {
                "count": stats["count"],
                "hit_rate": _rate(stats["hits"], stats["count"])
            }
            for bucket, stats in sorted(bucket_stats.items())
        },
        "samples": evaluated_samples
    }


def load_samples(path: Path) -> list[dict[str, Any]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("kind") != "backtest_samples":
        raise ValueError("top-level kind must be backtest_samples")
    samples = document.get("data", {}).get("samples")
    if not isinstance(samples, list) or not samples:
        raise ValueError("data.samples must be a non-empty list")
    return samples


def main() -> int:
    parser = argparse.ArgumentParser(description="Backtest football prediction samples.")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()

    try:
        samples = load_samples(args.path)
        result = calculate(samples)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        parser.error(str(exc))
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
