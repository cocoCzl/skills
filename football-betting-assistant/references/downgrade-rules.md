# Downgrade Rules

Use these rules to decide Reference Grade, Model Confidence, Data Confidence, and when to stop.

When model probability and no-vig market probability are available, run
`scripts/grade_calculator.py` first. Treat its grade as the maximum mechanical
grade after edge thresholds and hard caps; the agent may downgrade further for
football context, but should not upgrade above the scripted cap without new
verified information.

## Reference Grades

**A**: Strong model support and strong data confidence. Requires current fixture, odds, team context, and no unresolved major source conflict. Do not assign A close to kickoff without late lineup/injury/weather/market context.

**B**: Usable lean with moderate uncertainty, single-source odds, incomplete late data, or modest value edge.

**C**: Weak lean, observation only, high variance, limited data, or poor market value.

**Pass**: Value insufficient, data insufficient, source conflict unresolved, market inconsistency unresolved, or risk too high.

## Model Confidence

Model Confidence describes the strength of the football outcome view:

- High: expected goals, score concentration, market direction, and context broadly agree.
- Medium: the model has a clear lean but meaningful uncertainty remains.
- Low: the model view is fragile, highly sensitive to assumptions, or internally split.

## Data Confidence

Data Confidence describes completeness and freshness:

- High: current data is sourced, timestamped, and mostly consistent.
- Medium: some useful data exists but one or more categories are single-source, stale, or incomplete.
- Low: major current data is unavailable, stale, conflicting, or unverified.

## Probability Analysis vs Value Judgment

Probability Analysis is allowed without odds.

Value Judgment requires verifiable Odds Data. If odds are missing or unconfirmed, say that value judgment is unavailable and do not imply something is worth buying.

## Late Calibration

When a match is close to kickoff, missing or unconfirmed lineups, injuries, weather, or market movement prevents an A grade. Continue with Base Analysis only if the user accepts elevated uncertainty.

## Withhold Reference Purchase Plans

Withhold Reference Purchase Plans or Portfolio Variants when:

- Fixtures cannot be confirmed.
- Home/away or neutral-site context is unknown.
- Odds are required for value judgment but unavailable.
- Core source conflicts remain unresolved.
- Data confidence is low across multiple matches.
- Portfolio Correlation risk is high and cannot be explained or reduced.

## Language Guardrails

Forbidden certainty and pressure language:

- 必中
- 稳赢
- 稳胆
- 包中
- 必买
- 重仓
- 这单稳了
- 回本
- 翻本

Forbidden advice categories:

- Personalized stake size.
- Bankroll allocation.
- Kelly bet size.
- Recovery betting.
- Chasing losses.

Ticket-tier totals are allowed only when expressed as unit-count math, such as `8 注 x 2 元/注 = 16 元`. Do not turn this into bankroll allocation or pressure language.

Rewrite direct commands into Reference Purchase Plan wording. For example, use “基础比分覆盖可作为参考，结构是 2 x 2 x 2 x 2 = 16 注” instead of “买这个”.

## Missing Data

Mark missing current data as unconfirmed. If missing data is critical, ask the user for it instead of forcing a recommendation.
