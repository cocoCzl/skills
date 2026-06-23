# Math Model

The Core Math Model is a transparent reasoning frame, not a guarantee engine.

## Expected Goals

Estimate:

- `home_xg`: expected goals for home or nominal-home team.
- `away_xg`: expected goals for away or nominal-away team.

Use:

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

## Bayesian Updating

Start from a prior expectation, then update with evidence.

Examples:

- Main striker absent: reduce attacking expectation.
- Multiple defensive injuries: increase opponent scoring expectation.
- Knockout match with conservative incentives: reduce total-goal expectation and increase draw/under likelihood.
- Strong under market movement confirmed by lineup news: reduce total-goal expectation.

If evidence is qualitative, state that the adjustment is qualitative. Do not pretend it is a trained model.

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

Treat small edges cautiously. If the data confidence is low or single-source, downgrade.

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
