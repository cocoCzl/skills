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

If the user asks for more than four matches in a portfolio, analyze the fixture list but ask them to reduce the portfolio to four matches or fewer for the first version.

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

## Betting Portfolio Flow

1. Confirm up to four concrete fixtures.
2. Start the report with a 比赛大纲 / 今日赛程确认 section that lists every match, kickoff time, group/competition, venue context, and current data confidence.
3. Run the Single-Match Analysis flow in compact but substantive form for each match before giving any portfolio plan.
4. Check Portfolio Correlation: competition stage, same group/table incentives, rotation, weather clusters, and shared market assumptions.
5. Exclude Pass matches or matches with severe Information Sufficiency gaps.
6. Build ticket tiers: 2 元, 16 元, 32 元, and 48 元 when four matches are available and score coverage is requested or implied.
7. Add named portfolio variants when supported by the data: 稳健方向单, 基础比分覆盖, 增强比分覆盖, and 搏冷/高赔率小单. Keep speculative variants clearly optional and high variance.
8. Provide More Combination Candidates when there are extra plausible directions, but keep them separate from the four ticket tiers.
9. Provide Score Coverage with up to four scores per match only when calculating a higher ticket tier; otherwise keep compact coverage to no more than three scores per match.
10. Produce the Portfolio Report template.

Do not output a single "only correct" portfolio. If enough data exists, always offer tiered reference purchase plans plus optional alternative combinations.

Do not compress portfolio analysis into only one summary table. The user should see why each match is included: source notes, model direction, top scores, risk, and grade.

## Ticket Tier Construction

Use these default tiers for four-match portfolios:

- 2 元档: 1 selection per match, usually 胜平负/让球/大小球 direction rather than exact score.
- 16 元档: 8 units at 2 元/unit, usually `1 x 2 x 2 x 2 = 8` units.
- 32 元档: 16 units at 2 元/unit, usually `2 x 2 x 2 x 2 = 16` units.
- 48 元档: 24 units at 2 元/unit, usually `3 x 2 x 2 x 2 = 24` units or another explicitly shown 24-unit structure.

Use 2 元 per unit by default only for explaining total amount, not for bankroll advice. If the user's local lottery unit price differs, state the assumed unit price and let the user adjust.

Default named portfolio variants:

- 稳健方向单: uses result, handicap result, over-under, or total-goals directions rather than fragile exact scores.
- 基础比分覆盖: uses the most concentrated score candidates from the Poisson matrix.
- 增强比分覆盖: adds one plausible secondary path for the highest-variance match.
- 搏冷/高赔率小单: uses lower-probability but explainable outcomes; label it optional, high variance, and not the core plan.

## Post-Match Review Flow

1. Confirm actual results from user-provided or current sources.
2. Reconstruct the pre-match assumptions if available.
3. Compare expected goals, score candidates, odds value, and risk points with actual outcome.
4. Identify model bias and data bias.
5. Suggest future weighting adjustments.
6. Do not produce chase-loss, recovery-bet, or "下一场翻本" advice.

## Final Checks

Before answering:

- Separate Probability Analysis from Value Judgment.
- Check Market Consistency.
- Check source timestamps and data gaps.
- Apply Reference Grade and confidence rules.
- Remove certainty, pressure, bankroll-allocation, personalized stake-size, and chase-loss language.
