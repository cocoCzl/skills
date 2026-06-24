# Model Parameters

Use this reference when the report needs reproducible expected-goals priors,
bounded contextual adjustments, and value/grade thresholds.

## Expected-Goals Prior

When xG/xGA inputs and competition averages are available, calculate the base
expected goals with `scripts/xg_prior_calculator.py`.

Default formula:

```text
league_avg_xg = (league_home_xg + league_away_xg) / 2
home_attack_index = home_xg_for / league_avg_xg
away_defense_index = away_xg_against / league_avg_xg
home_base_xg = base_home_environment * home_attack_index * away_defense_index

away_attack_index = away_xg_for / league_avg_xg
home_defense_index = home_xg_against / league_avg_xg
away_base_xg = base_away_environment * away_attack_index * home_defense_index
```

For normal home/away matches, `base_home_environment = league_home_xg` and
`base_away_environment = league_away_xg`. For neutral-site matches, both sides
use `league_avg_xg` before any explicit venue factor.

Use team xG/xGA when available. If only goals for/against are available, the
agent may use them as a lower-precision proxy and must downgrade model
precision in the report.

## Bounded Adjustments

Contextual adjustments must be explicit and bounded. The agent chooses the
scenario and delta from verified evidence, then the calculator validates that
the requested delta sits inside the allowed range.

| Code | Typical target | Allowed delta | Meaning |
|---|---|---:|---|
| `main_striker_absent` | affected team's attack | -0.25 to -0.10 | Main finisher absent or severely limited |
| `key_creator_absent` | affected team's attack | -0.20 to -0.05 | Main creator absent or minutes-limited |
| `two_center_backs_absent` | opponent attack | +0.15 to +0.35 | Two first-choice center backs absent |
| `defensive_rotation` | opponent attack | +0.10 to +0.25 | Defensive rotation or makeshift back line |
| `heavy_rotation` | affected team's attack | -0.30 to -0.10 | Strong rotation lowers attacking cohesion |
| `knockout_caution` | total goals | -0.30 to -0.10 | Incentives support a slower, lower-risk script |
| `heavy_rain` | total goals | -0.25 to -0.10 | Weather or pitch lowers execution quality |
| `market_under_move` | total goals | -0.20 to -0.05 | Confirmed under move supported by team news |
| `must_win_openness` | total goals | +0.10 to +0.30 | Game state incentives raise late-goal risk |
| `opponent_transition_threat` | threatening team's attack | +0.05 to +0.20 | Underdog or away transition path is credible |

If the evidence does not fit a listed code, use a conservative manual note in
the report and mark the model record as partially qualitative. Do not invent a
new range inside a match report.

## Value Thresholds

Use `scripts/grade_calculator.py` when model and market probabilities are both
available.

```text
edge = model_probability - market_no_vig_probability
clear value: edge >= 0.05
minor value: 0.02 <= edge < 0.05
thin or no value: 0 <= edge < 0.02
negative value: edge < 0
```

Treat small edges cautiously. Single-source odds, stale data, unresolved market
conflicts, low data confidence, or late lineup uncertainty should cap or reduce
the grade even when the numerical edge is positive.

## Grade Caps

Start from the numerical edge and confidence inputs, then apply caps:

- Single-source odds: maximum `B`.
- Low odds confidence: maximum `C`.
- Low data confidence: maximum `C`.
- Near kickoff with unconfirmed lineup: maximum `B`.
- Near kickoff with unavailable lineup: maximum `C`.
- High risk tier: maximum `C`.
- Unresolved source conflict: `Pass`.
- Unresolved market inconsistency: `Pass`.

The agent may downgrade further for football reasons, but should not upgrade
above these caps without new verified information.
