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


def _prob(lam: float, goals: int) -> float:
    return math.exp(-lam) * (lam**goals) / math.factorial(goals)


def calculate(home_xg: float, away_xg: float, max_goals: int = 8, over_under_line: float | None = None, top_n: int = 6) -> dict[str, Any]:
    if home_xg < 0 or away_xg < 0:
        raise ValueError("expected goals must be non-negative")
    if max_goals < 1:
        raise ValueError("max_goals must be at least 1")
    if top_n < 1:
        raise ValueError("top_n must be at least 1")

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
            "over_under_line": over_under_line
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
    args = parser.parse_args()

    try:
        result = calculate(args.home_xg, args.away_xg, args.max_goals, args.over_under_line, args.top_n)
    except ValueError as exc:
        parser.error(str(exc))
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
