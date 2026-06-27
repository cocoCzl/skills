#!/usr/bin/env python3
"""Helpers for prediction snapshots, legacy report records, and reviews."""

from __future__ import annotations

import re
import math
from datetime import datetime, timezone
from typing import Any


RESULT_KEYS = ("home_win", "draw", "away_win")
GRADE_VALUES = {"Pass": 0, "C": 1, "B": 2, "A": 3}


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def split_match_name(value: Any) -> tuple[str | None, str | None]:
    text = str(value or "").strip()
    text = re.sub(r"^周[一二三四五六日]\d+\s+", "", text)
    parts = re.split(r"\s+(?:vs|v|VS|V)\s+|对|vs|VS| v ", text)
    if len(parts) != 2:
        return None, None
    return parts[0].strip() or None, parts[1].strip() or None


def confidence_en(value: Any, default: str = "low") -> str:
    mapping = {"高": "high", "中": "medium", "低": "low", "high": "high", "medium": "medium", "low": "low"}
    return mapping.get(str(value or "").strip(), default)


def grade_cap(*grades: str | None) -> str:
    known = [grade for grade in grades if grade in GRADE_VALUES]
    if not known:
        return "Pass"
    return min(known, key=lambda grade: GRADE_VALUES[grade])


def parse_percent_triplet(text: str) -> dict[str, float] | None:
    match = re.search(
        r"胜/平/负概率约\s*([0-9]+(?:\.[0-9]+)?)%/([0-9]+(?:\.[0-9]+)?)%/([0-9]+(?:\.[0-9]+)?)%",
        text,
    )
    if not match:
        return None
    values = [float(item) / 100 for item in match.groups()]
    total = sum(values)
    if total <= 0:
        return None
    normalized = [item / total for item in values]
    return dict(zip(RESULT_KEYS, normalized))


def parse_final_xg(text: str) -> dict[str, float] | None:
    match = re.search(r"最终\s*xG\s*([0-9]+(?:\.[0-9]+)?)-([0-9]+(?:\.[0-9]+)?)", text, re.IGNORECASE)
    if not match:
        return None
    return {"home_xg": float(match.group(1)), "away_xg": float(match.group(2)), "total_xg": float(match.group(1)) + float(match.group(2))}


def parse_over_under(text: str) -> dict[str, float] | None:
    match = re.search(
        r"([0-9]+(?:\.[0-9]+)?)球大/小约\s*([0-9]+(?:\.[0-9]+)?)%/([0-9]+(?:\.[0-9]+)?)%",
        text,
    )
    if not match:
        return None
    over = float(match.group(2)) / 100
    under = float(match.group(3)) / 100
    total = over + under
    if total <= 0:
        return None
    return {"line": float(match.group(1)), "over": over / total, "under": under / total, "push": 0.0}


def parse_top_scores(text: str, fallback: Any = None) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    score_block = ""
    match = re.search(r"前[五六0-9]+比分[:：]\s*([^。]+)", text)
    if match:
        score_block = match.group(1)
    if score_block:
        for score, probability in re.findall(r"(\d+:\d+)\s*([0-9]+(?:\.[0-9]+)?)%", score_block):
            candidates.append({"score": score, "probability": float(probability) / 100})
    if candidates:
        return candidates
    if isinstance(fallback, list):
        return [{"score": str(item), "probability": None} for item in fallback if re.match(r"^\d+:\d+$", str(item))]
    if isinstance(fallback, str):
        return [{"score": item, "probability": None} for item in re.findall(r"\d+:\d+", fallback)]
    return []


def total_goals_tail_flags(record: dict[str, Any]) -> list[str]:
    flags: list[str] = []
    final_xg = record.get("final_xg") or {}
    total_xg = final_xg.get("total_xg")
    if isinstance(total_xg, (int, float)) and total_xg >= 3.0:
        flags.append("high_total_xg_tail")
    total_probs = record.get("total_goals_probabilities") or []
    if isinstance(total_probs, list):
        tail_5_plus = sum(float(item.get("probability") or 0.0) for item in total_probs if int(item.get("total_goals") or 0) >= 5)
        if tail_5_plus >= 0.12:
            flags.append("five_plus_goal_tail")
        record["tail_5_plus_probability"] = round(tail_5_plus, 6)
    if record.get("deep_handicap"):
        flags.append("deep_handicap_tail")
    if record.get("final_round_goal_difference_pressure"):
        flags.append("goal_difference_pressure_tail")
    return flags


def poisson_total_goals(home_xg: float, away_xg: float, max_goals: int = 8) -> list[dict[str, Any]]:
    total_xg = home_xg + away_xg
    probabilities: list[dict[str, Any]] = []
    covered = 0.0
    for goals in range(max_goals + 1):
        probability = math.exp(-total_xg) * (total_xg**goals) / math.factorial(goals)
        probabilities.append({"total_goals": goals, "probability": probability})
        covered += probability
    if covered < 1.0:
        probabilities.append({"total_goals": max_goals + 1, "probability": max(0.0, 1.0 - covered), "label": f"{max_goals + 1}+"})
    return probabilities


def structured_match_record(analysis: dict[str, Any], fixture: dict[str, Any] | None = None, report_meta: dict[str, Any] | None = None) -> dict[str, Any]:
    fixture = fixture or {}
    report_meta = report_meta or {}
    summary = str(analysis.get("poisson_summary") or "")
    match_name = str(analysis.get("match") or fixture.get("match") or "")
    home_team, away_team = split_match_name(match_name)
    score_candidates = parse_top_scores(summary, analysis.get("score_candidates"))
    record: dict[str, Any] = {
        "match": match_name,
        "home_team": home_team or fixture.get("home_team"),
        "away_team": away_team or fixture.get("away_team"),
        "kickoff_time": analysis.get("kickoff_time") or fixture.get("kickoff_time"),
        "competition": analysis.get("competition") or fixture.get("competition"),
        "observed_at": report_meta.get("generated_at"),
        "result_pick": analysis.get("result_pick"),
        "handicap_pick": analysis.get("handicap_pick"),
        "totals_pick": analysis.get("totals_pick"),
        "score_candidates": score_candidates,
        "result_probabilities": parse_percent_triplet(summary),
        "over_under_probabilities": parse_over_under(summary),
        "final_xg": parse_final_xg(summary),
        "reference_grade": analysis.get("reference_grade") or ("C" if analysis.get("data_confidence") in {"中", "medium"} else "Pass"),
        "model_confidence": confidence_en(analysis.get("model_confidence"), "low"),
        "data_confidence": confidence_en(analysis.get("data_confidence"), "low"),
        "risk_points": list(analysis.get("risk_notes") or []),
        "poisson_summary": summary,
        "market_availability": analysis.get("market_availability") or [],
    }
    if record.get("final_xg"):
        record["total_goals_probabilities"] = poisson_total_goals(
            float(record["final_xg"]["home_xg"]),
            float(record["final_xg"]["away_xg"]),
        )
    record["tail_risk_flags"] = total_goals_tail_flags(record)
    if record["tail_risk_flags"]:
        record["risk_points"].append("总进球尾部风险： " + " / ".join(record["tail_risk_flags"]))
    return record


def normalize_prediction_snapshot(document: dict[str, Any], source_path: str | None = None) -> dict[str, Any] | None:
    if document.get("kind") == "prediction_snapshot":
        data = document.get("data") or {}
        model_outputs = data.setdefault("model_outputs", {})
        if "match_records" not in model_outputs:
            fixtures = {item.get("match"): item for item in (data.get("pre_match_data") or {}).get("fixtures", []) or [] if isinstance(item, dict)}
            model_outputs["match_records"] = [
                structured_match_record(item, fixtures.get(item.get("match")), data)
                for item in model_outputs.get("match_analyses", []) or []
                if isinstance(item, dict)
            ]
        return document

    if not isinstance(document.get("matches"), list):
        return None

    report_id = document.get("report_id") or (source_path or "legacy-prediction").split("/")[-1].replace(".json", "")
    created_at = document.get("created_at") or now_iso()
    matches = [item for item in document.get("matches", []) if isinstance(item, dict)]
    match_records = [structured_match_record(item, report_meta={"generated_at": created_at}) for item in matches]
    guardrails = document.get("guardrails") if isinstance(document.get("guardrails"), dict) else {}
    return {
        "kind": "prediction_snapshot",
        "data": {
            "report_id": report_id,
            "generated_at": created_at,
            "source_snapshot_id": document.get("source_snapshot"),
            "source_provider": "legacy_manual_report",
            "html_report_path": document.get("html_report_path") or source_path,
            "html_report_input_path": document.get("report_input"),
            "pre_match_data": {
                "fixtures": [
                    {
                        "match": item.get("match"),
                        "kickoff_time": item.get("kickoff_time"),
                        "competition": item.get("competition"),
                        "data_confidence": item.get("data_confidence"),
                    }
                    for item in matches
                ],
                "direction_summary": [],
                "data_gaps": ["legacy_snapshot_missing_structured_fields"],
            },
            "model_outputs": {
                "match_analyses": matches,
                "match_records": match_records,
                "ticket_plans": document.get("ticket_plans", []),
                "risks": list(guardrails.get("notes") or []),
            },
            "post_match_result": None,
            "compatibility_notes": [
                "Converted from legacy prediction format; missing probabilities or lines are left unavailable.",
            ],
        },
    }


def backtest_sample_from_record(record: dict[str, Any], actual_result: dict[str, Any], sample_id: str) -> dict[str, Any] | None:
    probabilities = record.get("result_probabilities")
    if not probabilities:
        return None
    return {
        "sample_id": sample_id,
        "fixture": {
            "match": record.get("match"),
            "home_team": record.get("home_team"),
            "away_team": record.get("away_team"),
            "kickoff_time": record.get("kickoff_time"),
            "competition": record.get("competition"),
        },
        "prediction": {
            "observed_at": record.get("observed_at") or now_iso(),
            "result_probabilities": probabilities,
            "over_under_probabilities": record.get("over_under_probabilities"),
            "score_candidates": record.get("score_candidates") or [],
            "reference_grade": record.get("reference_grade") if record.get("reference_grade") in GRADE_VALUES else "Pass",
            "model_confidence": record.get("model_confidence") if record.get("model_confidence") in {"high", "medium", "low"} else "low",
            "data_confidence": record.get("data_confidence") if record.get("data_confidence") in {"high", "medium", "low"} else "low",
            "risk_points": record.get("risk_points") or [],
        },
        "actual_result": actual_result,
    }
