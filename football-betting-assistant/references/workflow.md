# Workflow

Follow this workflow before producing any football betting report.

## Runtime Modes

**Agent mode**: Use when browsing, search, local files, configured APIs, or calculators are available. Actively perform Fixture Discovery, Live Verification, data collection, and model calculation.

**Assisted context mode**: Use when the user or local files provide partial data. Validate what is supplied, identify gaps, and ask only for missing critical fields.

**Offline fallback mode**: Use when no live tools are available. Use only user-provided data and never invent current fixtures, odds, lineups, injuries, or weather.

## Request Classification

Classify the user request as one of:

1. Single-Match Analysis.
2. Betting Portfolio, up to four matches.
3. Post-Match Review.
4. Historical Backtest / Calibration.

If the user asks for more than four matches in a portfolio, analyze the fixture list but ask them to reduce the portfolio to four matches or fewer for the first version.

If the user asks to improve hit rate, accuracy, calibration, or model quality, route to Historical Backtest / Calibration. Do not claim the skill can improve future outcomes without measured historical evidence.

## Single-Match Analysis Flow

1. Confirm teams, competition, kickoff time, timezone, and home/away or neutral venue.
2. Collect Odds Data when Value Judgment is requested or implied.
3. Collect Team Form Window and current team context.
4. Build a Data Summary Table.
5. Estimate expected goals from attack/defense strength, venue, competition scoring environment, and recent form.
6. Apply Bayesian updates for injuries, lineups, motivation, schedule, weather, and market movement. Show the direction of each meaningful adjustment.
7. Use the Poisson model to derive result, goals, and score probabilities. Use `scripts/poisson_calculator.py` when available; otherwise label the probabilities approximate.
8. Compare model probabilities with implied probabilities when odds exist.
9. Apply downgrade rules.
10. Produce the Single-Match Report template.

Single-match reports must include a visible evidence chain:

- 数据来源：name the source categories used, such as official fixture page, odds aggregator/bookmaker, team news outlet, stats site, weather source, or user-provided data.
- 基础面：form, attack/defense, injuries/lineups, venue/weather, motivation/schedule.
- 数学模型：prior xG, Bayesian adjustments, final xG, Poisson concentration, and result/total-goals probabilities.
- 玩法判断：separate probability lean from odds value.
- 风险：why the grade is not higher, and what late information could change it.

For group-stage final-round matches, calculate qualification context before treating motivation as a model adjustment. Include current points, goal difference, ranking routes under plausible results, rotation probability, and potential knockout-stage opponents. Treat "避强队" or "选路线" only as a motivation/risk modifier, not as certain team behavior.

## Betting Portfolio Flow

1. Confirm up to four concrete fixtures.
2. Default to the 经理人详版 for 四串一, 串关, and "明天早上四场" requests unless the user asks for a short answer. Use this order: 先给总方案 -> 比赛大纲/赛程确认 -> 小组排名/积分/战意 -> 赔率与市场中心 -> 模型怎么来的 -> 逐场分析 -> 比分覆盖和买法 -> 组合风险.
3. Start with a 比赛大纲 / 今日赛程确认 section that lists every match, kickoff time in the user's timezone, group/competition, venue context, and current data confidence.
4. For tournament group-stage slates, verify or request current group ranking, points, goal difference, qualification pressure, and rotation risk before using motivation as a model adjustment. If unavailable, show an "未确认" cell and downgrade data confidence instead of omitting the section.
5. Build a compact 赔率与市场中心 section before the match notes. When correct-score odds are available, list the lowest-price score cluster for each match and explain what the market center implies.
6. Explain the math model in user-readable language before or during the match notes: expected-goals prior, Bayesian adjustment direction, final xG, Poisson score concentration, odds implied/no-vig probability when odds exist, and whether the calculator/script or an approximation was used.
7. Run the Single-Match Analysis flow in compact but substantive prose for each match before giving any portfolio plan. Each match should read like a decision note, not only a row in a table.
8. For each match, include source notes, group/table context, basic football context, match script, model record, result lean, handicap lean, over-under/total-goals lean, score ranking, reference grade, and risk.
9. Check Portfolio Correlation: competition stage, same group/table incentives, rotation, weather clusters, and shared market assumptions.
10. Exclude Pass matches or matches with severe Information Sufficiency gaps.
11. Build portfolio variants from the actual score concentration and user intent. Do not force fixed 2/16/32/48 元 tiers. Calculate units as the product of selected outcomes per match and show amount only as `units x 2 元/unit`.
12. Add named portfolio variants when supported by the data: 胜平负四串一主线, 单比分主推小单, 基础比分覆盖, 增强比分覆盖, 补洞单, and 搏冷/高赔率小单. Keep speculative variants clearly optional and high variance.
13. Provide More Combination Candidates only when there are extra plausible directions, and keep them separate from the main plans.
14. Provide Score Coverage with up to four scores per match only when a match has a meaningful secondary path, such as late-goal expansion, red-card tail risk, draw protection, favorite-underperformance risk, or underdog transition threat.
15. Produce the Portfolio Report template.

Do not output a single "only correct" portfolio. If enough data exists, always offer tiered reference purchase plans plus optional alternative combinations.

Do not compress portfolio analysis into only one summary table. The user should see why each match is included: source notes, model direction, top scores, risk, and grade.

For four-match score portfolios, the default answer should be detailed enough that a user can understand why a 2:0 is preferred over 3:0, why a favorite may win but not cover, and which draw or underdog-goal score is the most important missing path. Avoid terse "model summary only" reports when data is available.

## Ticket Tier Construction

Construct the ticket structures from the match slate:

- Start with the most defensible direction plan, often using 胜平负, 让球胜平负, 大小球, or 总进球 rather than exact score for every match.
- For score portfolios, identify each match's core score cluster first, then decide whether it deserves one, two, three, or four score candidates.
- Use wider coverage on the most volatile match, not mechanically on the first match.
- If the user proposes their own score list, evaluate it directly: say what is合理, what is漏防, and how to补洞 if they have already bought it.
- Show every score portfolio as `A x B x C x D = N 注`; amount is `N x 2 元/unit = X 元` unless the user gives a different unit price.

Use 2 元 per unit by default only for explaining total amount, not for bankroll advice. If the user's local lottery unit price differs, state the assumed unit price and let the user adjust.

Default named portfolio variants:

- 稳健方向单: uses result, handicap result, over-under, or total-goals directions rather than fragile exact scores.
- 基础比分覆盖: uses the most concentrated score candidates from the Poisson matrix.
- 增强比分覆盖: adds one plausible secondary path for the highest-variance match or for a favorite that may only win narrowly.
- 补洞单: covers the most obvious omitted path, such as favorite 1:0, draw drag, underdog goal, or late score expansion.
- 搏冷/高赔率小单: uses lower-probability but explainable outcomes; label it optional, high variance, and not the core plan.

## Report File Output

Default chat output should be complete Markdown. If the user asks for a document, report file, md, html, or saved result and local file writes are available:

1. Create `reports/football-betting/` when needed.
2. Save Markdown as `reports/football-betting/YYYY-MM-DD-[short-slug].md`.
3. Save HTML as `reports/football-betting/YYYY-MM-DD-[short-slug].html`.
4. Keep the same analysis content in chat or provide a concise summary plus paths.
5. Treat generated report files as local outputs, not source files to commit.

## Post-Match Review Flow

1. Confirm actual results from user-provided or current sources.
2. Reconstruct the pre-match assumptions if available.
3. Compare expected goals, score candidates, odds value, and risk points with actual outcome.
4. Identify model bias and data bias.
5. Suggest future weighting adjustments.
6. Do not produce chase-loss, recovery-bet, or "下一场翻本" advice.

## Historical Backtest / Calibration Flow

Use this flow when the user wants to improve hit rate, audit predictions, or evaluate historical model quality.

1. Require historical pre-match snapshots: fixture, kickoff time, odds/line observed before kickoff, team context observed before kickoff, model probabilities, score candidates, reference grade, and actual result.
2. Reject or flag samples that mix in post-match information. If a field was not known before kickoff, mark it unavailable rather than backfilling it.
3. Validate samples with `scripts/validate_inputs.py` when they are supplied as JSON bundles.
4. Run `scripts/backtest_predictions.py` on the historical sample file when local execution is available.
5. Report hit rates for match result, over-under, and score coverage separately. Do not collapse them into one "命中率".
6. Report probability calibration with Brier score, log loss, and probability buckets. Favor better-calibrated probabilities over louder single-pick language.
7. Break results down by `reference_grade`, `model_confidence`, `data_confidence`, competition, and market type when sample size allows.
8. Convert findings into specific rule changes, such as downgrading low-data A/B picks, widening score coverage for high-total matches, or passing single-source odds edges below the edge threshold.
9. State sample size and limitations before giving model-improvement conclusions.

## Final Checks

Before answering:

- Separate Probability Analysis from Value Judgment.
- Check Market Consistency.
- Check source timestamps and data gaps.
- Apply Reference Grade and confidence rules.
- For backtests, check that every sample used only pre-match data and that sample size is shown.
- For group-stage final-round matches, check that qualification context uses potential knockout-stage opponents instead of assuming the next opponent is always a round-of-16 opponent.
- Remove certainty, pressure, bankroll-allocation, personalized stake-size, and chase-loss language.
