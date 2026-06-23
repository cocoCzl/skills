# Backtesting And Calibration

Use backtesting to improve decision quality with measured evidence. The goal is better-calibrated probabilities and clearer Pass rules, not certainty.

## Required Sample Shape

Every historical sample must be a pre-match snapshot plus the final result:

- Fixture identity, kickoff time, competition, and venue context.
- Odds and lines observed before kickoff, with source and timestamp.
- Team context observed before kickoff, with source and timestamp.
- Model probabilities and score candidates created before kickoff.
- Reference grade, model confidence, data confidence, and risk points.
- Actual full-time score and derived market outcomes.

Do not use post-match xG, post-match reports, or final lineup knowledge unless it was actually available before kickoff.

## Metrics To Report

Report each metric separately:

- 胜平负命中率: whether the highest model result probability matched the actual result.
- 大小球命中率: whether the model's over/under lean matched the final total against the observed line.
- 比分覆盖率: whether the final score was included in Top 1, Top 3, or the supplied coverage set.
- Brier score: lower is better for probability calibration.
- Log loss: lower is better; heavily penalizes confident wrong forecasts.
- Calibration buckets: compare predicted probability buckets with actual hit rates.
- Grade breakdown: A/B/C/Pass sample count and hit rate.

## Improvement Rules

Only change model rules after a pattern repeats across enough samples. Good changes are concrete:

- Downgrade A/B picks when current data is single-source, stale, or conflicting.
- Add Pass when model edge is small and the odds source is not consensus.
- Widen score coverage for high total-xG matches or clear two-way scoring paths.
- Avoid forcing exact-score portfolios when score probability mass is diffuse.
- Track competitions separately when tempo or rotation patterns differ.

## Report Wording

Use cautious language:

- "历史样本显示..."
- "这类场景需要降级..."
- "下一轮应优先验证..."

Avoid:

- "以后一定提高命中"
- "这个规则保证有效"
- "按回测买就行"
