#!/usr/bin/env python3
"""Deterministic Poisson calculator for football score analysis.

This script does not collect external data. It only turns expected goals into
score, result, and goals probabilities.
"""

from __future__ import annotations

import argparse
import json
import math
from typing import Any


HALF_TIME_FULL_TIME_LABELS = {
    ("home_win", "home_win"): "胜胜",
    ("home_win", "draw"): "胜平",
    ("home_win", "away_win"): "胜负",
    ("draw", "home_win"): "平胜",
    ("draw", "draw"): "平平",
    ("draw", "away_win"): "平负",
    ("away_win", "home_win"): "负胜",
    ("away_win", "draw"): "负平",
    ("away_win", "away_win"): "负负",
}


def _prob(lam: float, goals: int) -> float:
    return math.exp(-lam) * (lam**goals) / math.factorial(goals)


def _result(home_goals: int, away_goals: int) -> str:
    if home_goals > away_goals:
        return "home_win"
    if home_goals == away_goals:
        return "draw"
    return "away_win"


def _half_time_full_time_probabilities(home_xg: float, away_xg: float, max_goals: int, first_half_share: float) -> dict[str, float]:
    home_first_xg = home_xg * first_half_share
    away_first_xg = away_xg * first_half_share
    home_second_xg = home_xg - home_first_xg
    away_second_xg = away_xg - away_first_xg

    home_first_probs = [_prob(home_first_xg, i) for i in range(max_goals + 1)]
    away_first_probs = [_prob(away_first_xg, i) for i in range(max_goals + 1)]
    home_second_probs = [_prob(home_second_xg, i) for i in range(max_goals + 1)]
    away_second_probs = [_prob(away_second_xg, i) for i in range(max_goals + 1)]

    output = {label: 0.0 for label in HALF_TIME_FULL_TIME_LABELS.values()}
    for ht_home in range(max_goals + 1):
        for ht_away in range(max_goals + 1):
            first_probability = home_first_probs[ht_home] * away_first_probs[ht_away]
            half_time_result = _result(ht_home, ht_away)
            for second_home in range(max_goals + 1):
                for second_away in range(max_goals + 1):
                    full_time_result = _result(ht_home + second_home, ht_away + second_away)
                    label = HALF_TIME_FULL_TIME_LABELS[(half_time_result, full_time_result)]
                    output[label] += first_probability * home_second_probs[second_home] * away_second_probs[second_away]
    return output


def calculate(home_xg: float, away_xg: float, max_goals: int = 8, over_under_line: float | None = None, top_n: int = 6, first_half_share: float = 0.45) -> dict[str, Any]:
    if home_xg < 0 or away_xg < 0:
        raise ValueError("expected goals must be non-negative")
    if max_goals < 1:
        raise ValueError("max_goals must be at least 1")
    if top_n < 1:
        raise ValueError("top_n must be at least 1")
    if not 0 < first_half_share < 1:
        raise ValueError("first_half_share must be between 0 and 1")

    home_probs = [_prob(home_xg, i) for i in range(max_goals + 1)]
    away_probs = [_prob(away_xg, i) for i in range(max_goals + 1)]

    matrix: list[dict[str, Any]] = []
    home_win = draw = away_win = 0.0
    total_goals: dict[int, float] = {}
    over = under = push = None

    over_value = 0.0
    under_value = 0.0
    push_value = 0.0

    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            p = home_probs[h] * away_probs[a]
            total = h + a
            score = f"{h}:{a}"
            matrix.append({"score": score, "home_goals": h, "away_goals": a, "probability": p})
            total_goals[total] = total_goals.get(total, 0.0) + p
            if h > a:
                home_win += p
            elif h == a:
                draw += p
            else:
                away_win += p

            if over_under_line is not None:
                if total > over_under_line:
                    over_value += p
                elif total < over_under_line:
                    under_value += p
                else:
                    push_value += p

    score_mass = sum(item["probability"] for item in matrix)
    tail_mass = max(0.0, 1.0 - score_mass)
    top_scores = sorted(matrix, key=lambda item: item["probability"], reverse=True)[:top_n]

    result: dict[str, Any] = {
        "inputs": {
            "home_xg": home_xg,
            "away_xg": away_xg,
            "max_goals": max_goals,
            "over_under_line": over_under_line,
            "first_half_share": first_half_share
        },
        "score_matrix_mass": score_mass,
        "tail_mass": tail_mass,
        "result_probabilities": {
            "home_win": home_win,
            "draw": draw,
            "away_win": away_win
        },
        "top_scores": top_scores,
        "total_goals_probabilities": [
            {"total_goals": goals, "probability": probability}
            for goals, probability in sorted(total_goals.items())
        ],
        "half_time_full_time_probabilities": [
            {"selection": name, "probability": probability}
            for name, probability in _half_time_full_time_probabilities(home_xg, away_xg, max_goals, first_half_share).items()
        ],
        "score_matrix": matrix
    }

    if over_under_line is not None:
        result["over_under_probabilities"] = {
            "line": over_under_line,
            "over": over_value,
            "under": under_value,
            "push": push_value
        }

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate Poisson football probabilities.")
    parser.add_argument("--home-xg", type=float, required=True)
    parser.add_argument("--away-xg", type=float, required=True)
    parser.add_argument("--max-goals", type=int, default=8)
    parser.add_argument("--over-under-line", type=float)
    parser.add_argument("--top-n", type=int, default=6)
    parser.add_argument("--first-half-share", type=float, default=0.45)
    args = parser.parse_args()

    try:
        result = calculate(args.home_xg, args.away_xg, args.max_goals, args.over_under_line, args.top_n, args.first_half_share)
    except ValueError as exc:
        parser.error(str(exc))
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
