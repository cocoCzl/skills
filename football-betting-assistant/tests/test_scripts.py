#!/usr/bin/env python3
"""Smoke tests for football-betting-assistant helper scripts."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


poisson = load_module("poisson_calculator", "scripts/poisson_calculator.py")
implied = load_module("implied_probability", "scripts/implied_probability.py")
validator = load_module("validate_inputs", "scripts/validate_inputs.py")
backtest = load_module("backtest_predictions", "scripts/backtest_predictions.py")


class PoissonCalculatorTests(unittest.TestCase):
    def test_result_probabilities_are_sensible(self):
        result = poisson.calculate(1.65, 0.85, max_goals=10, over_under_line=2.5)
        probs = result["result_probabilities"]
        total = probs["home_win"] + probs["draw"] + probs["away_win"]
        self.assertGreater(total, 0.99)
        self.assertLessEqual(total, 1.0)

    def test_top_scores_are_sorted(self):
        result = poisson.calculate(1.4, 1.0, max_goals=8)
        top = result["top_scores"]
        self.assertEqual(top, sorted(top, key=lambda item: item["probability"], reverse=True))

    def test_over_under_is_calculated(self):
        result = poisson.calculate(1.6, 1.1, max_goals=10, over_under_line=2.5)
        ou = result["over_under_probabilities"]
        self.assertGreater(ou["over"], 0)
        self.assertGreater(ou["under"], 0)

    def test_invalid_expected_goals_fail(self):
        with self.assertRaises(ValueError):
            poisson.calculate(-1, 1)


class ImpliedProbabilityTests(unittest.TestCase):
    def test_match_result_no_vig_probabilities(self):
        result = implied.calculate({"home": 1.85, "draw": 3.55, "away": 4.6})
        no_vig = result["normalized_no_vig_probabilities"]
        self.assertAlmostEqual(sum(no_vig.values()), 1.0, places=8)
        self.assertIn("market_margin", result)

    def test_incomplete_market_warns(self):
        result = implied.calculate({"home": 1.85})
        self.assertFalse(result["complete_market"])
        self.assertTrue(result["warnings"])

    def test_invalid_odds_fail(self):
        with self.assertRaises(ValueError):
            implied.calculate({"home": 1.0})


class ValidatorTests(unittest.TestCase):
    def test_valid_example_bundle(self):
        path = ROOT / "examples" / "single-match-input.json"
        if not path.exists():
            self.skipTest("examples not created yet")
        document = json.loads(path.read_text(encoding="utf-8"))
        result = validator.validate_document(document)
        self.assertTrue(result["valid"], result)

    def test_invalid_fixture_missing_fields(self):
        result = validator.validate_document({"kind": "fixture", "data": {"home_team": "A"}})
        self.assertFalse(result["valid"])
        self.assertTrue(any("missing required field" in error for error in result["errors"]))

    def test_valid_backtest_sample(self):
        path = ROOT / "examples" / "backtest-sample.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        result = validator.validate_document(document)
        self.assertTrue(result["valid"], result)


class BacktestTests(unittest.TestCase):
    def test_backtest_metrics_are_calculated(self):
        path = ROOT / "examples" / "backtest-sample.json"
        samples = backtest.load_samples(path)
        result = backtest.calculate(samples)
        self.assertEqual(result["sample_count"], 2)
        self.assertAlmostEqual(result["result_hit_rate"], 0.5)
        self.assertAlmostEqual(result["score_top3_hit_rate"], 1.0)
        self.assertAlmostEqual(result["grade_breakdown"]["B"]["result_hit_rate"], 1.0)
        self.assertAlmostEqual(result["grade_breakdown"]["C"]["result_hit_rate"], 0.0)
        self.assertIn("B", result["grade_breakdown"])
        self.assertIn("calibration_buckets", result)

    def test_backtest_load_rejects_wrong_kind(self):
        with self.assertRaises(ValueError):
            backtest.load_samples(ROOT / "examples" / "single-match-input.json")


if __name__ == "__main__":
    raise SystemExit(unittest.main())
