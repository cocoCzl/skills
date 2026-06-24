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
xg_prior = load_module("xg_prior_calculator", "scripts/xg_prior_calculator.py")
grade_calc = load_module("grade_calculator", "scripts/grade_calculator.py")
match_model = load_module("match_model_calculator", "scripts/match_model_calculator.py")
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


class XgPriorCalculatorTests(unittest.TestCase):
    def test_prior_and_bounded_adjustments_are_calculated(self):
        adjustments = [
            xg_prior.Adjustment("defensive_rotation", "home", 0.12, "away fullback doubtful"),
            xg_prior.Adjustment("knockout_caution", "total", -0.12, "slow tempo"),
        ]
        result = xg_prior.calculate_prior(1.85, 0.85, 0.9, 1.65, venue_type="neutral", adjustments=adjustments)
        self.assertGreater(result["prior_xg"]["home_xg"], result["prior_xg"]["away_xg"])
        self.assertEqual(len(result["adjustments"]), 2)
        self.assertGreater(result["final_xg"]["home_xg"], 0)
        self.assertGreater(result["final_xg"]["away_xg"], 0)

    def test_adjustment_outside_range_fails(self):
        with self.assertRaises(ValueError):
            xg_prior.parse_adjustment("main_striker_absent:home:-0.50")


class GradeCalculatorTests(unittest.TestCase):
    def test_clear_edge_can_be_a_with_strong_inputs(self):
        result = grade_calc.calculate(0.58, 0.52, model_confidence="high", data_confidence="high", odds_confidence="high")
        self.assertEqual(result["value_label"], "clear_value")
        self.assertEqual(result["reference_grade"], "A")

    def test_single_source_caps_grade_at_b(self):
        result = grade_calc.calculate(0.58, 0.52, model_confidence="high", data_confidence="high", odds_confidence="high", single_source_odds=True)
        self.assertEqual(result["reference_grade"], "B")
        self.assertTrue(result["grade_caps"])
        self.assertTrue(result["downgrade_reasons"])

    def test_unresolved_conflict_forces_pass(self):
        result = grade_calc.calculate(0.58, 0.52, source_conflict="unresolved")
        self.assertEqual(result["reference_grade"], "Pass")


class MatchModelCalculatorTests(unittest.TestCase):
    def test_match_model_record_is_calculated_from_example(self):
        path = ROOT / "examples" / "single-match-model-input.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        result = match_model.calculate(document)
        record = result["model_record"]
        self.assertIn("prior", record)
        self.assertIn("poisson", record)
        self.assertIn("grade", record)
        self.assertTrue(record["grade"]["value_judgment_available"])
        self.assertIsNotNone(record["grade"]["edge"])
        self.assertTrue(record["grade"]["grade_caps"])

    def test_match_model_without_odds_has_no_value_judgment(self):
        document = {
            "teams": {
                "home_xg_for": 1.4,
                "home_xg_against": 1.0,
                "away_xg_for": 1.1,
                "away_xg_against": 1.2
            },
            "context": {"venue_type": "home_away"},
            "grading": {"market_key": "home"}
        }
        result = match_model.calculate(document)
        grade = result["model_record"]["grade"]
        self.assertFalse(grade["value_judgment_available"])
        self.assertIsNone(grade["edge"])


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
