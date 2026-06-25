#!/usr/bin/env python3
"""Calculate market-level implied probabilities, edge, and grades."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMPLETE_MARKET_MIN_SELECTIONS = {
    "match_result": 3,
    "handicap_match_result": 3,
    "over_under": 2,
    "total_goals": 2,
    "correct_score": 2,
}


def _load_grade_module() -> Any:
    path = ROOT / "scripts" / "grade_calculator.py"
    spec = importlib.util.spec_from_file_location("grade_calculator", path)
    if not spec or not spec.loader:
        raise RuntimeError("cannot load grade_calculator.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


grade_calculator = _load_grade_module()


def _raw_implied(odds: float) -> float:
    return 1.0 / odds


def _is_complete_market(market: dict[str, Any]) -> bool:
    selections = [item for item in market.get("selections", []) if item.get("odds")]
    minimum = COMPLETE_MARKET_MIN_SELECTIONS.get(str(market.get("market")), 2)
    return len(selections) >= minimum and all(float(item["odds"]) > 1 for item in selections)


def calculate_market_grade(market: dict[str, Any], model_probabilities: dict[str, float], grading: dict[str, Any]) -> dict[str, Any]:
    selections = [item for item in market.get("selections", []) if item.get("odds")]
    availability = market.get("availability") or {}
    complete = availability.get("status") == "available" and _is_complete_market(market)
    output: dict[str, Any] = {
        "market": market.get("market"),
        "source_market_name": market.get("source_market_name"),
        "status": "complete" if complete else "incomplete",
        "value_judgment_available": complete,
        "selections": [],
    }
    if not complete:
        output["reason"] = availability.get("reason") or "incomplete_market"
        return output

    raw_sum = sum(_raw_implied(float(item["odds"])) for item in selections)
    output["market_margin"] = round(raw_sum - 1.0, 6)
    output["return_rate"] = round(1.0 / raw_sum, 6) if raw_sum else None

    market_conflict = grading.get("market_inconsistency", "none")
    market_strength_delta = float(grading.get("market_strength_delta", 0.0) or 0.0)
    if market_strength_delta > 0.03:
        market_strength_delta = 0.03
    if market_strength_delta < -0.03:
        market_strength_delta = -0.03

    for item in selections:
        name = str(item.get("name"))
        odds = float(item["odds"])
        raw_probability = _raw_implied(odds)
        no_vig_probability = raw_probability / raw_sum
        independent_model_probability = model_probabilities.get(name)
        adjusted_model_probability = None
        grade = None
        edge = None
        if independent_model_probability is not None:
            adjusted_model_probability = max(0.0, min(1.0, independent_model_probability + market_strength_delta))
            grade = grade_calculator.calculate(
                model_probability=adjusted_model_probability,
                market_probability=no_vig_probability,
                model_confidence=grading.get("model_confidence", "medium"),
                data_confidence=grading.get("data_confidence", "medium"),
                odds_confidence=grading.get("odds_confidence", "medium"),
                single_source_odds=grading.get("single_source_odds", False),
                lineup_status=grading.get("lineup_status", "expected"),
                near_kickoff=grading.get("near_kickoff", False),
                source_conflict=grading.get("source_conflict", "none"),
                market_inconsistency=market_conflict,
                risk_tier=grading.get("risk_tier", "medium"),
            )
            edge = adjusted_model_probability - no_vig_probability
        output["selections"].append(
            {
                "name": name,
                "odds": odds,
                "raw_implied_probability": round(raw_probability, 6),
                "no_vig_probability": round(no_vig_probability, 6),
                "independent_model_probability": round(independent_model_probability, 6) if independent_model_probability is not None else None,
                "market_strength_delta": market_strength_delta,
                "adjusted_model_probability": round(adjusted_model_probability, 6) if adjusted_model_probability is not None else None,
                "edge": round(edge, 6) if edge is not None else None,
                "grade": grade,
            }
        )
    return output


def calculate(document: dict[str, Any]) -> dict[str, Any]:
    markets = document.get("markets")
    if not isinstance(markets, list) or not markets:
        raise ValueError("markets must be a non-empty list")
    model_probabilities = document.get("model_probabilities") or {}
    if not isinstance(model_probabilities, dict):
        raise ValueError("model_probabilities must be an object")
    grading = document.get("grading") or {}
    return {
        "kind": "market_grade_record",
        "markets": [calculate_market_grade(market, model_probabilities.get(str(market.get("market")), {}), grading) for market in markets],
        "notes": [
            "Market strength delta is bounded to +/-0.03 and never replaces the independent model probability.",
            "Incomplete markets are not eligible for full value judgment.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate market-level betting grades.")
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
