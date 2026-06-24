#!/usr/bin/env python3
"""Run the deterministic single-match model pipeline.

This script does not fetch data. It composes the local calculators:
xG prior -> bounded adjustments -> Poisson matrix -> implied probability ->
edge/grade caps.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def _load_module(name: str, relative_path: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    if not spec or not spec.loader:
        raise RuntimeError(f"cannot load module: {relative_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


xg_prior = _load_module("xg_prior_calculator", "scripts/xg_prior_calculator.py")
poisson = _load_module("poisson_calculator", "scripts/poisson_calculator.py")
implied = _load_module("implied_probability", "scripts/implied_probability.py")
grade_calc = _load_module("grade_calculator", "scripts/grade_calculator.py")


def _find_market_probability(no_vig: dict[str, float], market_key: str) -> float | None:
    return no_vig.get(market_key)


def calculate(document: dict[str, Any]) -> dict[str, Any]:
    teams = document.get("teams") or {}
    league = document.get("league") or {}
    context = document.get("context") or {}
    odds = document.get("odds") or {}
    grading = document.get("grading") or {}

    required_team_fields = ("home_xg_for", "home_xg_against", "away_xg_for", "away_xg_against")
    missing = [field for field in required_team_fields if teams.get(field) is None]
    if missing:
        raise ValueError(f"teams missing required fields: {', '.join(missing)}")

    adjustments = [xg_prior.parse_adjustment(raw) for raw in context.get("adjustments", [])]
    prior_result = xg_prior.calculate_prior(
        home_xg_for=teams["home_xg_for"],
        home_xg_against=teams["home_xg_against"],
        away_xg_for=teams["away_xg_for"],
        away_xg_against=teams["away_xg_against"],
        league_home_xg=league.get("home_xg", 1.45),
        league_away_xg=league.get("away_xg", 1.15),
        venue_type=context.get("venue_type", "home_away"),
        home_venue_factor=context.get("home_venue_factor", 1.0),
        away_venue_factor=context.get("away_venue_factor", 1.0),
        adjustments=adjustments,
    )

    final_xg = prior_result["final_xg"]
    poisson_result = poisson.calculate(
        final_xg["home_xg"],
        final_xg["away_xg"],
        max_goals=document.get("max_goals", 8),
        over_under_line=odds.get("over_under_line"),
        top_n=document.get("top_n", 6),
    )
    if not document.get("include_score_matrix", False):
        poisson_result = dict(poisson_result)
        poisson_result.pop("score_matrix", None)

    market_probabilities = None
    implied_result = None
    market_key = grading.get("market_key")
    if any(odds.get(key) is not None for key in ("home_price", "draw_price", "away_price", "over_price", "under_price")):
        implied_result = implied.calculate({
            "home": odds.get("home_price"),
            "draw": odds.get("draw_price"),
            "away": odds.get("away_price"),
            "over": odds.get("over_price"),
            "under": odds.get("under_price"),
        })
        market_probabilities = implied_result.get("normalized_no_vig_probabilities")

    model_probability = grading.get("model_probability")
    if model_probability is None and market_key:
        result_probs = poisson_result["result_probabilities"]
        over_under = poisson_result.get("over_under_probabilities", {})
        model_probability = {
            "home": result_probs.get("home_win"),
            "draw": result_probs.get("draw"),
            "away": result_probs.get("away_win"),
            "over": over_under.get("over"),
            "under": over_under.get("under"),
        }.get(market_key)

    market_probability = grading.get("market_probability")
    if market_probability is None and market_probabilities and market_key:
        market_probability = _find_market_probability(market_probabilities, market_key)

    value_judgment_available = model_probability is not None and market_probability is not None
    grade_result = grade_calc.calculate(
        model_probability=model_probability,
        market_probability=market_probability,
        model_confidence=grading.get("model_confidence", "medium"),
        data_confidence=grading.get("data_confidence", "medium"),
        odds_confidence=grading.get("odds_confidence", "medium"),
        single_source_odds=grading.get("single_source_odds", False),
        lineup_status=grading.get("lineup_status", "expected"),
        near_kickoff=grading.get("near_kickoff", False),
        source_conflict=grading.get("source_conflict", "none"),
        market_inconsistency=grading.get("market_inconsistency", "none"),
        risk_tier=grading.get("risk_tier", "medium"),
    )
    grade_result["value_judgment_available"] = value_judgment_available

    return {
        "kind": "match_model_record",
        "model_record": {
            "prior": prior_result,
            "poisson": poisson_result,
            "implied_probability": implied_result,
            "grade": grade_result,
            "calculation_notes": [
                "xG prior and bounded adjustments calculated by xg_prior_calculator.py",
                "Score, result, and goals probabilities calculated by poisson_calculator.py",
                "Odds implied/no-vig probabilities calculated only when odds are supplied",
                "Reference grade is mechanically capped by grade_calculator.py and may be downgraded further in the report",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the football betting deterministic model pipeline.")
    parser.add_argument("path", type=Path, help="JSON input path")
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
