#!/usr/bin/env python3
"""Acceptance checks for the football-betting-assistant skill package."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "SKILL.md",
    "references/workflow.md",
    "references/data-sources.md",
    "references/math-model.md",
    "references/model-parameters.md",
    "references/backtesting.md",
    "references/report-templates.md",
    "references/downgrade-rules.md",
    "references/glossary.md",
    "schemas/fixture.schema.json",
    "schemas/odds.schema.json",
    "schemas/team-context.schema.json",
    "schemas/match-analysis.schema.json",
    "schemas/portfolio.schema.json",
    "schemas/backtest-sample.schema.json",
    "scripts/xg_prior_calculator.py",
    "scripts/poisson_calculator.py",
    "scripts/implied_probability.py",
    "scripts/grade_calculator.py",
    "scripts/match_model_calculator.py",
    "scripts/validate_inputs.py",
    "scripts/backtest_predictions.py",
    "examples/single-match-input.json",
    "examples/portfolio-input.json",
    "examples/backtest-sample.json",
    "evals/evals.json",
    "tests/test_scripts.py"
]

BANNED_REPORT_PHRASES = [
    "必中",
    "稳赢",
    "包中",
    "必买",
    "重仓",
    "稳胆",
    "这单稳了",
    "回本",
    "翻本"
]

README_REQUIRED_SECTIONS = [
    "## 使用方式",
    "## 赔率获取途径",
    "## 数据服务/API 怎么配置",
    "## 未配置 API 时的默认行为",
    "## 数学计算引擎",
    "## 数据不足时如何处理",
    "## 示例提问",
    "## 带盘口赔率的使用例子",
    "## 输入模板",
    "## 输出内容",
    "## 回测和校准",
    "## 开发检查"
]

README_REQUIRED_PHRASES = [
    "THE_ODDS_API_KEY",
    "The Odds API",
    "不要固定套用 `2/16/32/48 元` 档位",
    "组合候选",
    "比赛大纲",
    "贝叶斯修正",
    "泊松",
    "xg_prior_calculator.py",
    "grade_calculator.py",
    "match_model_calculator.py",
    "回测",
    "Brier",
    "log loss",
    "让球/胜平负方向单",
    "大小球/总进球单",
    "混合过关单",
    "reports/football-betting/YYYY-MM-DD-[slug].html"
]

EVAL_KEYWORDS = {
    "fixture_discovery": ["明天早上四场世界杯", "Fixture Discovery"],
    "fallback": ["不能联网", "offline fallback"],
    "single_match": ["西班牙 vs 沙特"],
    "portfolio": ["四串一"],
    "missing_odds": ["没有赔率", "Value Judgment"],
    "conflict": ["A站说德国让1球", "Source Conflict"],
    "consistency": ["大2.5", "Market Consistency"],
    "review": ["复盘"]
}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def check_files() -> None:
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).exists():
            fail(f"missing required file: {relative}")


def check_json() -> None:
    for path in list((ROOT / "schemas").glob("*.json")) + list((ROOT / "examples").glob("*.json")) + [ROOT / "evals" / "evals.json"]:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")


def check_tests() -> None:
    result = subprocess.run([sys.executable, str(ROOT / "tests" / "test_scripts.py")], cwd=ROOT, text=True)
    if result.returncode != 0:
        fail("script-level tests failed")


def check_validation_examples() -> None:
    for relative in ("examples/single-match-input.json", "examples/portfolio-input.json", "examples/backtest-sample.json"):
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_inputs.py"), str(ROOT / relative)], cwd=ROOT, text=True)
        if result.returncode != 0:
            fail(f"validation failed for {relative}")


def check_match_model_example() -> None:
    result = subprocess.run([sys.executable, str(ROOT / "scripts" / "match_model_calculator.py"), str(ROOT / "examples" / "single-match-model-input.json")], cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        fail("match model example failed")
    payload = json.loads(result.stdout)
    model_record = payload.get("model_record") or {}
    for key in ("prior", "poisson", "grade"):
        if key not in model_record:
            fail(f"match model example missing model_record.{key}")
    if not model_record["grade"].get("value_judgment_available"):
        fail("match model example should have value judgment available")


def check_backtest_example() -> None:
    result = subprocess.run([sys.executable, str(ROOT / "scripts" / "backtest_predictions.py"), str(ROOT / "examples" / "backtest-sample.json")], cwd=ROOT, text=True)
    if result.returncode != 0:
        fail("backtest example failed")


def check_report_language() -> None:
    for path in (ROOT / "examples").glob("*.md"):
        text = path.read_text(encoding="utf-8")
        for phrase in BANNED_REPORT_PHRASES:
            if phrase in text:
                fail(f"banned phrase '{phrase}' found in {path.relative_to(ROOT)}")


def check_readme_usage() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    for section in README_REQUIRED_SECTIONS:
        if section not in text:
            fail(f"README usage section missing: {section}")
    for phrase in README_REQUIRED_PHRASES:
        if phrase not in text:
            fail(f"README required phrase missing: {phrase}")


def check_portfolio_template() -> None:
    text = (ROOT / "references" / "report-templates.md").read_text(encoding="utf-8")
    for phrase in (
        "北京时间比赛清单",
        "今天四场先看结论",
        "比赛大纲",
        "小组当前战绩",
        "当前胜平负",
        "出线形势",
        "潜在淘汰赛",
        "玩法可买性",
        "数据来源总览",
        "逐场分析",
        "比赛剧本",
        "数学模型",
        "贝叶斯修正",
        "泊松比分",
        "edge/评级封顶",
        "胜平负与大小球汇总",
        "比分覆盖建议",
        "四串一参考购买方案",
        "让球/胜平负方向单",
        "大小球/总进球单",
        "稳健方向单",
        "基础比分覆盖",
        "增强比分覆盖",
        "混合过关单",
        "补洞单",
        "搏冷/高赔率小单",
        "更多组合候选"
    ):
        if phrase not in text:
            fail(f"portfolio template missing: {phrase}")
    for forbidden in ("2 元档", "16 元档", "32 元档", "48 元档", "分档参考购买方案"):
        if forbidden in text:
            fail(f"portfolio template still contains fixed tier wording: {forbidden}")


def check_evals() -> None:
    text = (ROOT / "evals" / "evals.json").read_text(encoding="utf-8")
    for name, needles in EVAL_KEYWORDS.items():
        if not any(needle in text for needle in needles):
            fail(f"eval coverage missing: {name}")
    for phrase in ("回测", "Brier", "log loss", "reference_grade"):
        if phrase not in text:
            fail(f"eval coverage missing backtesting phrase: {phrase}")


def main() -> int:
    check_files()
    check_json()
    check_tests()
    check_validation_examples()
    check_match_model_example()
    check_backtest_example()
    check_report_language()
    check_readme_usage()
    check_portfolio_template()
    check_evals()
    print("football-betting-assistant acceptance checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
