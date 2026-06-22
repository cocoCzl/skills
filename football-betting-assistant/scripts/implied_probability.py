#!/usr/bin/env python3
"""Convert decimal odds into implied probabilities.

This script does not fetch odds. It only calculates probabilities from odds
already supplied by the user, agent, or local data.
"""

from __future__ import annotations

import argparse
import json
from typing import Any


def _validate_price(price: float | None, name: str) -> None:
    if price is not None and price <= 1:
        raise ValueError(f"{name} must be greater than 1.0")


def calculate(prices: dict[str, float | None]) -> dict[str, Any]:
    for key, price in prices.items():
        _validate_price(price, key)

    supplied = {key: price for key, price in prices.items() if price is not None}
    if not supplied:
        raise ValueError("at least one decimal odd is required")

    raw = {key: 1.0 / price for key, price in supplied.items()}
    total = sum(raw.values())
    complete_market = len(raw) in (2, 3)

    result: dict[str, Any] = {
        "raw_implied_probabilities": raw,
        "supplied_prices": supplied,
        "complete_market": complete_market,
        "warnings": []
    }

    if complete_market:
        result["market_margin"] = total - 1.0
        result["normalized_no_vig_probabilities"] = {key: value / total for key, value in raw.items()}
    else:
        result["warnings"].append("Incomplete market: no-vig normalization and margin are unavailable.")

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate implied probabilities from decimal odds.")
    parser.add_argument("--home", type=float)
    parser.add_argument("--draw", type=float)
    parser.add_argument("--away", type=float)
    parser.add_argument("--over", type=float)
    parser.add_argument("--under", type=float)
    args = parser.parse_args()

    prices = {
        "home": args.home,
        "draw": args.draw,
        "away": args.away,
        "over": args.over,
        "under": args.under
    }

    try:
        result = calculate(prices)
    except ValueError as exc:
        parser.error(str(exc))
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
