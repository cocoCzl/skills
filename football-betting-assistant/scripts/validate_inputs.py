#!/usr/bin/env python3
"""Validate football assistant JSON inputs and data-quality rules.

The validator intentionally uses only the Python standard library so the skill
package remains portable. It checks the schema-required fields and the project
specific data-quality warnings used by the assistant.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SCHEMA_REQUIRED: dict[str, list[str]] = {
    "fixture": ["home_team", "away_team", "competition", "kickoff_time", "timezone", "venue_type", "source", "observed_at"],
    "odds": ["market", "bookmaker_or_source", "observed_at", "confidence"],
    "team_context": ["team", "last_5_summary", "last_10_summary", "lineup_status", "source", "observed_at"],
    "match_analysis": ["fixture", "home_xg", "away_xg", "bayesian_adjustments", "result_probabilities", "score_candidates", "model_confidence", "data_confidence", "reference_grade", "risk_points"],
    "portfolio": ["matches", "correlation_notes", "ticket_tiers", "more_combination_candidates", "excluded_matches", "portfolio_risk_tier"]
}

CONFIDENCE = {"high", "medium", "low"}
REFERENCE_GRADES = {"A", "B", "C", "Pass"}
LINEUP_STATUSES = {"confirmed", "expected", "unconfirmed", "unavailable"}
VENUE_TYPES = {"home_away", "neutral", "unknown"}


def _missing(record: dict[str, Any], fields: list[str]) -> list[str]:
    return [field for field in fields if field not in record or record[field] in ("", None)]


def _warn_timestamp(record: dict[str, Any], label: str, warnings: list[str]) -> None:
    if not record.get("observed_at"):
        warnings.append(f"{label}: missing source timestamp")


def validate_fixture(record: dict[str, Any], path: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for field in _missing(record, SCHEMA_REQUIRED["fixture"]):
        errors.append(f"{path}: missing required field '{field}'")
    if record.get("venue_type") not in VENUE_TYPES:
        errors.append(f"{path}: venue_type must be one of {sorted(VENUE_TYPES)}")
    _warn_timestamp(record, path, warnings)
    if record.get("venue_type") == "unknown":
        warnings.append(f"{path}: venue type unknown; downgrade data confidence")
    return errors, warnings


def validate_odds(record: dict[str, Any], path: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for field in _missing(record, SCHEMA_REQUIRED["odds"]):
        errors.append(f"{path}: missing required field '{field}'")
    if record.get("confidence") not in CONFIDENCE:
        errors.append(f"{path}: confidence must be one of {sorted(CONFIDENCE)}")
    _warn_timestamp(record, path, warnings)
    if record.get("confidence") == "low":
        warnings.append(f"{path}: low odds confidence; downgrade value judgment")
    prices = [record.get(name) for name in ("home_price", "draw_price", "away_price", "over_price", "under_price")]
    if not any(price is not None for price in prices):
        warnings.append(f"{path}: no prices supplied; value judgment unavailable")
    return errors, warnings


def validate_team_context(record: dict[str, Any], path: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for field in _missing(record, SCHEMA_REQUIRED["team_context"]):
        errors.append(f"{path}: missing required field '{field}'")
    if record.get("lineup_status") not in LINEUP_STATUSES:
        errors.append(f"{path}: lineup_status must be one of {sorted(LINEUP_STATUSES)}")
    _warn_timestamp(record, path, warnings)
    if record.get("lineup_status") in {"unconfirmed", "unavailable"}:
        warnings.append(f"{path}: lineup not confirmed; A grade unavailable near kickoff")
    if record.get("xg_for") is None or record.get("xg_against") is None:
        warnings.append(f"{path}: xG/xGA unavailable; use goals data and downgrade model precision")
    return errors, warnings


def validate_match_analysis(record: dict[str, Any], path: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for field in _missing(record, SCHEMA_REQUIRED["match_analysis"]):
        errors.append(f"{path}: missing required field '{field}'")
    if record.get("reference_grade") not in REFERENCE_GRADES:
        errors.append(f"{path}: reference_grade must be A, B, C, or Pass")
    scores = record.get("score_candidates", [])
    if len(scores) != 3:
        errors.append(f"{path}: score_candidates must contain exactly three entries")
    if record.get("data_confidence") == "low" and record.get("reference_grade") == "A":
        errors.append(f"{path}: A grade cannot be used with low data confidence")
    return errors, warnings


def validate_portfolio(record: dict[str, Any], path: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for field in _missing(record, SCHEMA_REQUIRED["portfolio"]):
        errors.append(f"{path}: missing required field '{field}'")
    matches = record.get("matches", [])
    if not (1 <= len(matches) <= 4):
        errors.append(f"{path}: portfolio must contain one to four matches")
    for i, tier in enumerate(record.get("ticket_tiers", []), start=1):
        unit_count = tier.get("unit_count")
        total_amount = tier.get("total_amount")
        unit_price = tier.get("unit_price")
        if unit_count and unit_price and total_amount and abs((unit_count * unit_price) - total_amount) > 0.01:
            errors.append(f"{path}.ticket_tiers[{i}]: total_amount must equal unit_count x unit_price")
        if tier.get("stake_label") in {"稳健方向单", "基础比分覆盖", "增强比分覆盖", "补洞单", "搏冷/高赔率小单"}:
            if not unit_count:
                warnings.append(f"{path}.ticket_tiers[{i}]: named portfolio variants should show unit_count")
        for leg_index, leg in enumerate(tier.get("legs", []), start=1):
            coverage = leg.get("score_coverage", [])
            if len(coverage) > 4:
                errors.append(f"{path}.ticket_tiers[{i}].legs[{leg_index}]: score_coverage must have at most four scores")
    for variant_name in ("more_combination_candidates",):
        variants = record.get(variant_name) or []
        for variant_index, variant in enumerate(variants, start=1):
            if variant.get("unit_count") and variant.get("unit_price") and variant.get("total_amount"):
                if abs((variant["unit_count"] * variant["unit_price"]) - variant["total_amount"]) > 0.01:
                    errors.append(f"{path}.{variant_name}[{variant_index}]: total_amount must equal unit_count x unit_price")
            for i, leg in enumerate(variant.get("legs", []), start=1):
                coverage = leg.get("score_coverage", [])
                if len(coverage) > 4:
                    errors.append(f"{path}.{variant_name}[{variant_index}].legs[{i}]: score_coverage must have at most four scores")
    if record.get("portfolio_risk_tier") == "high":
        warnings.append(f"{path}: high portfolio risk tier; ensure aggressive framing is explicit")
    return errors, warnings


VALIDATORS = {
    "fixture": validate_fixture,
    "odds": validate_odds,
    "team_context": validate_team_context,
    "match_analysis": validate_match_analysis,
    "portfolio": validate_portfolio
}

BUNDLE_KEYS = {
    "fixture": "fixture",
    "fixtures": "fixture",
    "odds": "odds",
    "team_context": "team_context",
    "team_contexts": "team_context",
    "match_analysis": "match_analysis",
    "match_analyses": "match_analysis",
    "portfolio": "portfolio",
    "portfolios": "portfolio"
}


def validate_document(document: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    kind = document.get("kind")
    if kind in VALIDATORS:
        e, w = VALIDATORS[kind](document.get("data", {}), "data")
        errors.extend(e)
        warnings.extend(w)
    elif kind == "bundle":
        for key, value in document.get("data", {}).items():
            items = value if isinstance(value, list) else [value]
            validator_key = BUNDLE_KEYS.get(key)
            validator = VALIDATORS.get(validator_key or "")
            if not validator:
                warnings.append(f"data.{key}: no validator registered")
                continue
            for i, item in enumerate(items):
                e, w = validator(item, f"data.{key}[{i}]")
                errors.extend(e)
                warnings.extend(w)
    else:
        errors.append("top-level 'kind' must be one of fixture, odds, team_context, match_analysis, portfolio, bundle")

    return {"valid": not errors, "errors": errors, "warnings": warnings}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate football assistant JSON input.")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()

    document = json.loads(args.path.read_text(encoding="utf-8"))
    result = validate_document(document)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
