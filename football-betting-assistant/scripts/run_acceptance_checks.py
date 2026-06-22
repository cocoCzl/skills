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
    "references/report-templates.md",
    "references/downgrade-rules.md",
    "references/glossary.md",
    "schemas/fixture.schema.json",
    "schemas/odds.schema.json",
    "schemas/team-context.schema.json",
    "schemas/match-analysis.schema.json",
    "schemas/portfolio.schema.json",
    "scripts/poisson_calculator.py",
    "scripts/implied_probability.py",
    "scripts/validate_inputs.py",
    "examples/single-match-input.json",
    "examples/portfolio-input.json",
    "examples/single-match-report.md",
    "examples/portfolio-report.md",
    "examples/post-match-review.md",
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
    "## 推荐可选数据源",
    "## 未配置 API 时的默认行为",
    "## 公开网页核验由谁处理",
    "## 数学计算引擎",
    "## 数据不足时如何处理",
    "## 示例提问",
    "## 带盘口赔率的使用例子",
    "## 输入模板",
    "## 输出内容",
    "## 开发检查"
]

README_REQUIRED_PHRASES = [
    "THE_ODDS_API_KEY",
    "The Odds API",
    "2 元档",
    "16 元档",
    "32 元档",
    "48 元档",
    "更多组合候选",
    "比赛大纲",
    "贝叶斯修正",
    "泊松",
    "稳健方向单",
    "搏冷/高赔率小单"
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
    for relative in ("examples/single-match-input.json", "examples/portfolio-input.json"):
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_inputs.py"), str(ROOT / relative)], cwd=ROOT, text=True)
        if result.returncode != 0:
            fail(f"validation failed for {relative}")


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
        "比赛大纲",
        "数据来源总览",
        "逐场分析",
        "数学模型",
        "贝叶斯修正",
        "泊松比分",
        "赔率/盘口摘要",
        "分档参考购买方案",
        "2 元档",
        "16 元档",
        "32 元档",
        "48 元档",
        "稳健方向单",
        "基础比分覆盖",
        "增强比分覆盖",
        "搏冷/高赔率小单",
        "更多组合候选"
    ):
        if phrase not in text:
            fail(f"portfolio template missing: {phrase}")


def check_rich_examples() -> None:
    single = (ROOT / "examples" / "single-match-report.md").read_text(encoding="utf-8")
    portfolio = (ROOT / "examples" / "portfolio-report.md").read_text(encoding="utf-8")
    for phrase in ("数据来源与比赛确认", "基础面分析", "数学模型", "基础 xG prior", "贝叶斯修正", "泊松比分集中", "比分排序"):
        if phrase not in single:
            fail(f"single-match example missing rich section: {phrase}")
    for phrase in ("比赛大纲", "数据来源总览", "逐场分析", "数学模型", "稳健方向单", "基础比分覆盖", "增强比分覆盖", "搏冷/高赔率小单"):
        if phrase not in portfolio:
            fail(f"portfolio example missing rich section: {phrase}")


def check_evals() -> None:
    text = (ROOT / "evals" / "evals.json").read_text(encoding="utf-8")
    for name, needles in EVAL_KEYWORDS.items():
        if not any(needle in text for needle in needles):
            fail(f"eval coverage missing: {name}")


def main() -> int:
    check_files()
    check_json()
    check_tests()
    check_validation_examples()
    check_report_language()
    check_readme_usage()
    check_portfolio_template()
    check_rich_examples()
    check_evals()
    print("football-betting-assistant acceptance checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
