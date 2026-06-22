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
5. Estimate expected goals.
6. Apply Bayesian updates for injuries, lineups, motivation, schedule, weather, and market movement.
7. Use the Poisson model to derive result, goals, and score probabilities.
8. Compare model probabilities with implied probabilities when odds exist.
9. Apply downgrade rules.
10. Produce the Single-Match Report template.

## Betting Portfolio Flow

1. Confirm up to four concrete fixtures.
2. Run the Single-Match Analysis flow in compact form for each match.
3. Check Portfolio Correlation: competition stage, same group/table incentives, rotation, weather clusters, and shared market assumptions.
4. Exclude Pass matches or matches with severe Information Sufficiency gaps.
5. Build main, conservative, and aggressive Portfolio Variants.
6. Provide Score Coverage with up to three scores per match.
7. Produce the Portfolio Report template.

Do not output a single "only correct" portfolio. If enough data exists, always offer main, conservative, and aggressive variants.

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
- Remove certainty, pressure, stake-size, and chase-loss language.
