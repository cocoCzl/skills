#!/usr/bin/env python3
"""Calculate edge labels and capped reference grades."""

from __future__ import annotations

import argparse
import json
from typing import Any


GRADE_ORDER = {"Pass": 0, "C": 1, "B": 2, "A": 3}
CONFIDENCE = {"high", "medium", "low"}


def _validate_probability(value: float | None, name: str) -> None:
    if value is not None and not (0 <= value <= 1):
        raise ValueError(f"{name} must be between 0 and 1")


def _cap_grade(grade: str, cap: str) -> str:
    return grade if GRADE_ORDER[grade] <= GRADE_ORDER[cap] else cap


def _value_label(edge: float | None) -> str:
    if edge is None:
        return "value_unavailable"
    if edge >= 0.05:
        return "clear_value"
    if edge >= 0.02:
        return "minor_value"
    if edge >= 0:
        return "thin_or_no_value"
    return "negative_value"


def _base_grade(edge: float | None, model_confidence: str, data_confidence: str, odds_confidence: str) -> str:
    if edge is None:
        if data_confidence == "high" and model_confidence == "high":
            return "B"
        if data_confidence == "low" or model_confidence == "low":
            return "C"
        return "C"
    if edge >= 0.05:
        if data_confidence == "high" and model_confidence in {"high", "medium"} and odds_confidence == "high":
            return "A"
        return "B"
    if edge >= 0.02:
        return "B" if data_confidence != "low" else "C"
    if edge >= 0:
        return "C"
    return "Pass"


def calculate(
    model_probability: float | None,
    market_probability: float | None,
    model_confidence: str = "medium",
    data_confidence: str = "medium",
    odds_confidence: str = "medium",
    single_source_odds: bool = False,
    lineup_status: str = "expected",
    near_kickoff: bool = False,
    source_conflict: str = "none",
    market_inconsistency: str = "none",
    risk_tier: str = "medium",
) -> dict[str, Any]:
    _validate_probability(model_probability, "model_probability")
    _validate_probability(market_probability, "market_probability")
    for value, name, allowed in (
        (model_confidence, "model_confidence", CONFIDENCE),
        (data_confidence, "data_confidence", CONFIDENCE),
        (odds_confidence, "odds_confidence", CONFIDENCE),
        (lineup_status, "lineup_status", {"confirmed", "expected", "unconfirmed", "unavailable"}),
        (source_conflict, "source_conflict", {"none", "resolved", "unresolved"}),
        (market_inconsistency, "market_inconsistency", {"none", "resolved", "unresolved"}),
        (risk_tier, "risk_tier", {"low", "medium", "high"}),
    ):
        if value not in allowed:
            raise ValueError(f"{name} must be one of {sorted(allowed)}")

    edge = None
    if model_probability is not None and market_probability is not None:
        edge = model_probability - market_probability

    grade = _base_grade(edge, model_confidence, data_confidence, odds_confidence)
    reasons: list[str] = []
    grade_caps: list[str] = []

    if source_conflict == "unresolved":
        grade = "Pass"
        reasons.append("unresolved source conflict")
        grade_caps.append("unresolved source conflict forces Pass")
    if market_inconsistency == "unresolved":
        grade = "Pass"
        reasons.append("unresolved market inconsistency")
        grade_caps.append("unresolved market inconsistency forces Pass")

    if grade != "Pass":
        if single_source_odds:
            grade_caps.append("single-source odds maximum grade B")
            capped = _cap_grade(grade, "B")
            if capped != grade:
                reasons.append("single-source odds cap grade at B")
            grade = capped
        if data_confidence == "low":
            grade_caps.append("low data confidence maximum grade C")
            capped = _cap_grade(grade, "C")
            if capped != grade:
                reasons.append("low data confidence cap grade at C")
            grade = capped
        if odds_confidence == "low":
            grade_caps.append("low odds confidence maximum grade C")
            capped = _cap_grade(grade, "C")
            if capped != grade:
                reasons.append("low odds confidence cap grade at C")
            grade = capped
        if near_kickoff and lineup_status == "unconfirmed":
            grade_caps.append("unconfirmed lineup near kickoff maximum grade B")
            capped = _cap_grade(grade, "B")
            if capped != grade:
                reasons.append("unconfirmed lineup near kickoff cap grade at B")
            grade = capped
        if near_kickoff and lineup_status == "unavailable":
            grade_caps.append("unavailable lineup near kickoff maximum grade C")
            capped = _cap_grade(grade, "C")
            if capped != grade:
                reasons.append("unavailable lineup near kickoff cap grade at C")
            grade = capped
        if risk_tier == "high":
            grade_caps.append("high risk tier maximum grade C")
            capped = _cap_grade(grade, "C")
            if capped != grade:
                reasons.append("high risk tier cap grade at C")
            grade = capped

    return {
        "inputs": {
            "model_probability": model_probability,
            "market_probability": market_probability,
            "model_confidence": model_confidence,
            "data_confidence": data_confidence,
            "odds_confidence": odds_confidence,
            "single_source_odds": single_source_odds,
            "lineup_status": lineup_status,
            "near_kickoff": near_kickoff,
            "source_conflict": source_conflict,
            "market_inconsistency": market_inconsistency,
            "risk_tier": risk_tier,
        },
        "edge": edge,
        "value_label": _value_label(edge),
        "reference_grade": grade,
        "grade_caps": grade_caps,
        "downgrade_reasons": reasons,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate value edge and reference grade.")
    parser.add_argument("--model-probability", type=float)
    parser.add_argument("--market-probability", type=float)
    parser.add_argument("--model-confidence", choices=sorted(CONFIDENCE), default="medium")
    parser.add_argument("--data-confidence", choices=sorted(CONFIDENCE), default="medium")
    parser.add_argument("--odds-confidence", choices=sorted(CONFIDENCE), default="medium")
    parser.add_argument("--single-source-odds", action="store_true")
    parser.add_argument("--lineup-status", choices=["confirmed", "expected", "unconfirmed", "unavailable"], default="expected")
    parser.add_argument("--near-kickoff", action="store_true")
    parser.add_argument("--source-conflict", choices=["none", "resolved", "unresolved"], default="none")
    parser.add_argument("--market-inconsistency", choices=["none", "resolved", "unresolved"], default="none")
    parser.add_argument("--risk-tier", choices=["low", "medium", "high"], default="medium")
    args = parser.parse_args()

    try:
        result = calculate(
            model_probability=args.model_probability,
            market_probability=args.market_probability,
            model_confidence=args.model_confidence,
            data_confidence=args.data_confidence,
            odds_confidence=args.odds_confidence,
            single_source_odds=args.single_source_odds,
            lineup_status=args.lineup_status,
            near_kickoff=args.near_kickoff,
            source_conflict=args.source_conflict,
            market_inconsistency=args.market_inconsistency,
            risk_tier=args.risk_tier,
        )
    except ValueError as exc:
        parser.error(str(exc))
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
