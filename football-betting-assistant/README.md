# Football Betting Assistant

`football-betting-assistant` is an agent-first skill package for Chinese football betting analysis.

## Usage

Place the `football-betting-assistant/` directory in your Codex or agent skills directory. The skill should trigger automatically when a user asks for football betting analysis, 竞彩, 胜平负, 让球胜平负, 比分推荐, 大小球, 总进球, 串关, 四串一, or 赛后复盘.

The skill works best when the agent has browsing, search, local files, configured football data APIs, or the bundled calculators available. When live tools are unavailable, it should ask for the minimum missing match data instead of inventing fixtures, odds, lineups, injuries, or weather.

## What It Does

- Discovers fixtures when users ask natural-language requests.
- Verifies current odds, lines, team form, injuries, lineups, weather, and competition context when tools are available.
- Uses a transparent model: expected goals, Bayesian updates, Poisson score probabilities, and implied probability comparison.
- Produces Single-Match Reports, Portfolio Reports, Score Coverage, Reference Purchase Plans, and Post-Match Reviews.

## What It Does Not Do

- It does not guarantee outcomes.
- It does not prescribe stake sizes or bankroll allocation.
- It does not produce chase-loss advice.
- It does not log into bookmaker accounts or bypass access restrictions.
- It does not hardcode football data credentials or large-model API keys.

## Example Prompts

```text
帮我分析今晚西班牙 vs 沙特，给胜平负、让球、大小球和三个比分候选。
```

```text
明天早上四场世界杯比赛，帮我做一个四串一参考购买方案，重点看比分和大小球。
```

```text
现在不能联网。我给你赔率和球队近况，你按离线模式分析法国 vs 日本有没有价值。
```

```text
A站说德国让1球，B站说德国让1.25；A站说主力前锋伤缺，B站没提。帮我分析风险。
```

```text
复盘一下我昨天买的四串一为什么没中，重点看模型偏差和数据偏差。
```

## Input Template

When the agent cannot verify current data, provide this template:

```markdown
比赛：
开赛时间：
赛事：
主客/中立：
想看玩法：胜平负 / 让球胜平负 / 比分 / 大小球 / 四串一
赔率/盘口：
伤停/首发：
近期状态或数据：
```

## Output Shape

Single-match reports should include:

- 数据确认：fixture, odds/lines, form, xG or scoring data, injuries, lineup, weather, motivation, gaps.
- 结论摘要：胜平负、让球、大小球、参考等级、模型置信度、数据置信度。
- 概率判断：result probabilities and over-under probabilities.
- 模型依据：expected goals, Poisson score concentration, Bayesian adjustments, odds-value comparison when odds exist.
- 三个比分候选：primary, secondary, and upset-aware score candidates.
- 参考购买方案：non-guaranteed reference plan, plus items not recommended.
- 风险点：late lineup, single-source odds, source conflicts, market consistency, or other uncertainty.

Portfolio reports should include fixture confirmation, compact conclusions for each match, portfolio correlation checks, main/conservative/aggressive variants, and Pass or exclusion notes.

Post-match reviews should compare pre-match assumptions with actual outcomes, identify model and data bias, and avoid recovery-bet advice.

## Development Checks

Run script tests:

```bash
python3 football-betting-assistant/tests/test_scripts.py
```

Validate examples:

```bash
python3 football-betting-assistant/scripts/validate_inputs.py football-betting-assistant/examples/single-match-input.json
python3 football-betting-assistant/scripts/validate_inputs.py football-betting-assistant/examples/portfolio-input.json
```

Run acceptance checks:

```bash
python3 football-betting-assistant/scripts/run_acceptance_checks.py
```
