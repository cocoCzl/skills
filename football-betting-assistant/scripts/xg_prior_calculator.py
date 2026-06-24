#!/usr/bin/env python3
"""Calculate reproducible football xG priors and bounded adjustments."""

from __future__ import annotations

import argparse
import json
from typing import Any


ADJUSTMENT_RULES: dict[str, tuple[float, float]] = {
    "main_striker_absent": (-0.25, -0.10),
    "key_creator_absent": (-0.20, -0.05),
    "two_center_backs_absent": (0.15, 0.35),
    "defensive_rotation": (0.10, 0.25),
    "heavy_rotation": (-0.30, -0.10),
    "knockout_caution": (-0.30, -0.10),
    "heavy_rain": (-0.25, -0.10),
    "market_under_move": (-0.20, -0.05),
    "must_win_openness": (0.10, 0.30),
    "opponent_transition_threat": (0.05, 0.20),
}

TARGETS = {"home", "away", "total"}


class Adjustment:
    def __init__(self, code: str, target: str, delta: float, note: str = "") -> None:
        self.code = code
        self.target = target
        self.delta = delta
        self.note = note


def _validate_non_negative(value: float, name: str) -> None:
    if value < 0:
        raise ValueError(f"{name} must be non-negative")


def _clamp(value: float, lower: float = 0.0, upper: float = 5.0) -> float:
    return min(max(value, lower), upper)


def parse_adjustment(raw: str) -> Adjustment:
    parts = raw.split(":", 3)
    if len(parts) < 3:
        raise ValueError("adjustments must use CODE:TARGET:DELTA or CODE:TARGET:DELTA:NOTE")
    code, target, delta_text = parts[:3]
    note = parts[3] if len(parts) == 4 else ""
    if code not in ADJUSTMENT_RULES:
        raise ValueError(f"unknown adjustment code: {code}")
    if target not in TARGETS:
        raise ValueError(f"adjustment target must be one of {sorted(TARGETS)}")
    try:
        delta = float(delta_text)
    except ValueError as exc:
        raise ValueError(f"invalid adjustment delta: {delta_text}") from exc
    low, high = ADJUSTMENT_RULES[code]
    if not (low <= delta <= high):
        raise ValueError(f"{code} delta {delta} outside allowed range [{low}, {high}]")
    return Adjustment(code=code, target=target, delta=delta, note=note)


def calculate_prior(
    home_xg_for: float,
    home_xg_against: float,
    away_xg_for: float,
    away_xg_against: float,
    league_home_xg: float = 1.45,
    league_away_xg: float = 1.15,
    venue_type: str = "home_away",
    home_venue_factor: float = 1.0,
    away_venue_factor: float = 1.0,
    adjustments: list[Adjustment] | None = None,
) -> dict[str, Any]:
    for name, value in {
        "home_xg_for": home_xg_for,
        "home_xg_against": home_xg_against,
        "away_xg_for": away_xg_for,
        "away_xg_against": away_xg_against,
        "league_home_xg": league_home_xg,
        "league_away_xg": league_away_xg,
        "home_venue_factor": home_venue_factor,
        "away_venue_factor": away_venue_factor,
    }.items():
        _validate_non_negative(value, name)
    if league_home_xg == 0 or league_away_xg == 0:
        raise ValueError("league xG averages must be greater than zero")
    if venue_type not in {"home_away", "neutral"}:
        raise ValueError("venue_type must be home_away or neutral")

    league_avg_xg = (league_home_xg + league_away_xg) / 2
    if league_avg_xg <= 0:
        raise ValueError("league average xG must be greater than zero")

    home_attack_index = home_xg_for / league_avg_xg
    away_defense_index = away_xg_against / league_avg_xg
    away_attack_index = away_xg_for / league_avg_xg
    home_defense_index = home_xg_against / league_avg_xg

    if venue_type == "neutral":
        home_environment = league_avg_xg
        away_environment = league_avg_xg
    else:
        home_environment = league_home_xg
        away_environment = league_away_xg

    home_base_xg = _clamp(home_environment * home_attack_index * away_defense_index * home_venue_factor)
    away_base_xg = _clamp(away_environment * away_attack_index * home_defense_index * away_venue_factor)

    home_final_xg = home_base_xg
    away_final_xg = away_base_xg
    adjustment_records: list[dict[str, Any]] = []

    for adjustment in adjustments or []:
        before = {"home_xg": home_final_xg, "away_xg": away_final_xg}
        if adjustment.target == "home":
            home_final_xg = _clamp(home_final_xg + adjustment.delta)
        elif adjustment.target == "away":
            away_final_xg = _clamp(away_final_xg + adjustment.delta)
        else:
            total = home_final_xg + away_final_xg
            if total <= 0:
                home_share = away_share = 0.5
            else:
                home_share = home_final_xg / total
                away_share = away_final_xg / total
            home_final_xg = _clamp(home_final_xg + adjustment.delta * home_share)
            away_final_xg = _clamp(away_final_xg + adjustment.delta * away_share)
        low, high = ADJUSTMENT_RULES[adjustment.code]
        adjustment_records.append({
            "code": adjustment.code,
            "target": adjustment.target,
            "delta": adjustment.delta,
            "allowed_range": [low, high],
            "note": adjustment.note,
            "before": before,
            "after": {"home_xg": home_final_xg, "away_xg": away_final_xg},
        })

    return {
        "inputs": {
            "home_xg_for": home_xg_for,
            "home_xg_against": home_xg_against,
            "away_xg_for": away_xg_for,
            "away_xg_against": away_xg_against,
            "league_home_xg": league_home_xg,
            "league_away_xg": league_away_xg,
            "venue_type": venue_type,
            "home_venue_factor": home_venue_factor,
            "away_venue_factor": away_venue_factor,
        },
        "indices": {
            "home_attack_index": home_attack_index,
            "away_defense_index": away_defense_index,
            "away_attack_index": away_attack_index,
            "home_defense_index": home_defense_index,
        },
        "prior_xg": {
            "home_xg": home_base_xg,
            "away_xg": away_base_xg,
        },
        "adjustments": adjustment_records,
        "final_xg": {
            "home_xg": home_final_xg,
            "away_xg": away_final_xg,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate football xG prior and bounded contextual adjustments.")
    parser.add_argument("--home-xg-for", type=float, required=True)
    parser.add_argument("--home-xg-against", type=float, required=True)
    parser.add_argument("--away-xg-for", type=float, required=True)
    parser.add_argument("--away-xg-against", type=float, required=True)
    parser.add_argument("--league-home-xg", type=float, default=1.45)
    parser.add_argument("--league-away-xg", type=float, default=1.15)
    parser.add_argument("--venue-type", choices=["home_away", "neutral"], default="home_away")
    parser.add_argument("--home-venue-factor", type=float, default=1.0)
    parser.add_argument("--away-venue-factor", type=float, default=1.0)
    parser.add_argument(
        "--adjustment",
        action="append",
        default=[],
        help="Repeatable CODE:TARGET:DELTA or CODE:TARGET:DELTA:NOTE; target is home, away, or total.",
    )
    args = parser.parse_args()

    try:
        adjustments = [parse_adjustment(raw) for raw in args.adjustment]
        result = calculate_prior(
            home_xg_for=args.home_xg_for,
            home_xg_against=args.home_xg_against,
            away_xg_for=args.away_xg_for,
            away_xg_against=args.away_xg_against,
            league_home_xg=args.league_home_xg,
            league_away_xg=args.league_away_xg,
            venue_type=args.venue_type,
            home_venue_factor=args.home_venue_factor,
            away_venue_factor=args.away_venue_factor,
            adjustments=adjustments,
        )
    except ValueError as exc:
        parser.error(str(exc))
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
