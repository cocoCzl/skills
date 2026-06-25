# Math Model

The Core Math Model is a transparent reasoning frame, not a guarantee engine.

## Expected Goals

Estimate:

- `home_xg`: expected goals for home or nominal-home team.
- `away_xg`: expected goals for away or nominal-away team.

When xG/xGA and competition average inputs are available, calculate the prior
with `scripts/xg_prior_calculator.py` and the parameter rules in
`references/model-parameters.md`. Use:

- Team attacking and defensive output.
- Competition scoring environment.
- Venue or neutral-site context.
- Recent form.
- Injuries and lineups.
- Schedule congestion and motivation.
- Weather and pitch.
- Odds movement as market information.

Every analyzable pre-match report should show:

- prior xG before contextual adjustment.
- meaningful Bayesian adjustments.
- final xG used for the Poisson calculation.
- whether values were calculated with the bundled script, calculated manually, or approximated because tools/data were unavailable.

For Chinese user-facing portfolio reports, also include a short "模型怎么来的" explanation before the recommendations. Use plain language:

- 预期进球不是单纯猜比分；它 starts from team strength, attack/defense level, venue, competition scoring environment, and market strength.
- 贝叶斯修正 means new evidence moves the prior up or down, such as injuries, rotation, group-table incentives, weather, or market movement.
- 泊松模型 converts final xG into a score matrix, then aggregates the matrix into 胜平负, 大小球/总进球, and correct-score concentration.
- 赔率隐含概率 shows what the market is pricing. A favorite can have a high win probability while still being weak on a deep handicap if the score cluster is 1-0 or 2-0.
- This is a transparent decision aid, not a trained guarantee engine.

## Bayesian Updating

Start from a prior expectation, then update with evidence.

Examples:

- Main striker absent: reduce attacking expectation.
- Multiple defensive injuries: increase opponent scoring expectation.
- Knockout match with conservative incentives: reduce total-goal expectation and increase draw/under likelihood.
- Strong under market movement confirmed by lineup news: reduce total-goal expectation.

If evidence is qualitative, state that the adjustment is qualitative. Do not pretend it is a trained model. When a listed adjustment code applies, keep the delta inside the bounded ranges in `references/model-parameters.md` and record the code, target, delta, and reason.

Use Bayesian updating as a disciplined adjustment layer, not as vague wording. State the prior, the evidence, the direction of the update, and the final effect in compact form. Examples:

- `prior 1.80-0.75 -> final 1.70-0.70`: strong favorite, but knockout caution and slow tempo lower total goals.
- `prior 1.35-1.10 -> final 1.25-1.20`: home striker uncertainty lowers home attack; opponent transition threat raises away scoring tail.

If there is no credible evidence for a correction, say "无强修正，沿用基础 xG" rather than inventing an adjustment.

## Poisson Distribution

For expected goals `lambda`, the probability of `k` goals is:

```text
P(k goals) = exp(-lambda) * lambda^k / k!
```

For a score `home_goals-away_goals`:

```text
P(score) = P(home_goals | home_xg) * P(away_goals | away_xg)
```

Aggregate the score matrix:

- Home win: sum scores where home goals > away goals.
- Draw: sum scores where home goals = away goals.
- Away win: sum scores where home goals < away goals.
- Over line: sum scores where total goals > line.
- Under line: sum scores where total goals < line.
- Push: when total goals equals an integer line.

Use `scripts/poisson_calculator.py` when available. Without tools, give ranges and label them approximate.

For each match, report a compact Poisson record:

- Final xG.
- Win/draw/loss probabilities.
- Over/under or total-goals probabilities when a line is available.
- Top three to six score candidates, depending on whether the report is single-match or portfolio coverage.
- Tail risk, such as early goal, red card, rotation, or high-score tail, when it conflicts with the main score set.

For four-match score portfolios, use the score matrix to explain the purchase structure:

- 主单比分: the single most coherent score path after market and football-context checks.
- 核心覆盖: usually one to three high-concentration scores per match.
- 增强覆盖: add the best secondary path, such as favorite concedes once, favorite only wins by one, or late expansion to a higher total.
- 漏洞/补防: the score that would most obviously beat the main ticket logic, such as 1:1, 1:0, 2:1, or 3:1 depending on the match script.

Before a correct-score ticket is promoted to a core plan, run or apply
`scripts/score_coverage_analyzer.py`:

- Single top score below 10% cannot be called a strong single-score pick.
- Top 3 cumulative probability below 25% means weak score coverage.
- Top 4-5 cumulative probability below 33% prevents score tickets from
  becoming the core portfolio.
- High total xG or credible both-teams-to-score paths widen the distribution;
  downgrade or add conceded-goal / late-expansion protection.

Every score coverage section should explain primary path, secondary path, and
missed-path protection. If coverage is weak, keep score picks as analysis or
optional high-variance ideas rather than a main ticket.

## Implied Probability

For decimal odds:

```text
raw implied probability = 1 / odds
```

For a complete market:

```text
market margin = sum(raw implied probabilities) - 1
no-vig probability = raw implied probability / sum(raw implied probabilities)
```

Use `scripts/implied_probability.py` when available.

## Value Judgment

Only make Value Judgment when Odds Data exists.

Useful comparison:

```text
edge = model probability - no-vig market probability
```

Treat small edges cautiously. Use `scripts/grade_calculator.py` when model and market probabilities are available, then apply any additional football-context downgrade. If the data confidence is low or single-source, downgrade.

For market-by-market grading, use `scripts/market_grade_calculator.py` when structured market selections and model probabilities are available. It should produce separate grades for market families such as:

- `match_result`
- `handicap_match_result`
- `total_goals` / `over_under`
- `correct_score`
- overall match view, if the report needs a summary

Complete markets calculate raw implied probability, market margin, return rate,
and no-vig probability for every selection. Incomplete markets, missing odds,
unknown availability, source-missing markets, and parser-failed markets must be
marked approximate or unavailable for full Value Judgment.

Market strength can be used only as a bounded correction to the independent
model probability. It must not replace the football model. If market direction
and model direction conflict and the reason is not explained by team news,
lineups, injuries, or tactical context, downgrade or Pass the affected market.

Use this wording discipline:

- "概率倾向" can be stated from the model.
- "赔率价值" requires verifiable odds or line data.
- "高赔率小单" requires an explainable low-probability scenario and must be labelled high variance.

## Calibration And Backtesting

Treat model probabilities as forecasts that need calibration, not as fixed truth.

When historical samples are available, evaluate:

- Match-result calibration with Brier score and log loss.
- Over-under calibration when an observed line and final total goals exist.
- Score coverage hit rate for Top 1, Top 3, and portfolio coverage sets.
- Reference-grade reliability: A should outperform B, B should outperform C, and Pass should show weak value or insufficient data.
- Bucket reliability: predictions around 60% should win materially more often than predictions around 40%.

Use backtest findings to tune rules, not to overfit one slate. Prefer changes that are explainable from repeated patterns, such as:

- Lowering grade when odds are single-source and edge is small.
- Reducing favorite xG when knockout or qualification incentives slow tempo.
- Widening score coverage when final xG total is high or both teams have clear scoring paths.
- Passing matches where source conflicts or lineup uncertainty create large probability swings.

Never present a historical ROI or hit-rate improvement as a guarantee for future tickets.

## Worked Example

Input assumptions:

- Home expected goals: 1.65
- Away expected goals: 0.85
- Over-under line: 2.5
- Home win decimal odds: 1.85
- Draw decimal odds: 3.55
- Away win decimal odds: 4.60

Model process:

1. Build a Poisson score matrix from 0-0 through the selected max-goal cap.
2. Aggregate scores into home win, draw, away win, and over/under probabilities.
3. Select the three most useful score candidates, balancing raw probability and risk story.
4. Convert odds into raw and no-vig implied probabilities.
5. Compare model probability to no-vig market probability.

Example style for report:

- 预期进球：主队 1.65，客队 0.85。
- 泊松比分集中：1:0、2:0、1:1。
- 贝叶斯修正：客队进攻端伤停使客队进球预期小幅下调。
- 赔率价值：模型主胜约 55%，市场去水后约 52%，仅有轻微价值。

This is still a probability estimate, not a guarantee.
