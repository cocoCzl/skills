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

## Bayesian Updating

Start from a prior expectation, then update with evidence.

Examples:

- Main striker absent: reduce attacking expectation.
- Multiple defensive injuries: increase opponent scoring expectation.
- Knockout match with conservative incentives: reduce total-goal expectation and increase draw/under likelihood.
- Strong under market movement confirmed by lineup news: reduce total-goal expectation.

If evidence is qualitative, state that the adjustment is qualitative. Do not pretend it is a trained model.

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
