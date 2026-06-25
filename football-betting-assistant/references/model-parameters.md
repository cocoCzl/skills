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

## Team Type And Competition Parameters

Before selecting recent-form windows or scoring parameters, classify the match
with `scripts/team_context_rules.py`.

Supported formal-analysis team types:

- `club`: senior men's club matches.
- `national`: senior men's national-team matches.
- `unknown`: team type cannot be verified; analysis may continue, but precision
  is capped until a suitable context is confirmed.

Unsupported for formal purchase plans:

- Youth or age-group teams, such as U17, U19, U21, U23, 青年队, or 预备队.
- Women's football, such as 女足, 女子, or women competitions.

Do not mix competition-parameter pools:

- Club matches must use club-league or club-tournament scoring context.
- National-team matches must use national-team competition context.
- World Cup, continental cups, international friendlies, and qualifiers should
  not borrow club-league scoring averages as if they were equivalent.
- Unknown matches may use same-type defaults only after the type is identified;
  otherwise cap Reference Grade at `C`.

Confidence caps:

| Team type | Parameter pool | Default cap |
|---|---|---:|
| `club` | club | `B` until exact competition context is verified |
| `national` | national | `B` until exact competition context is verified |
| `unknown` | same-type default required | `C` |
| `unsupported` | unsupported | `Pass` for purchase plans |

An A-grade needs a verified team type, suitable competition scoring context,
current team data, and no unresolved major source conflict. Global defaults
alone cannot produce A-grade precision.

## Recent Form To xG Prior Inputs

Use `scripts/recent_form_to_xg.py` when recent-form aggregates need to become
inputs for `scripts/xg_prior_calculator.py`.

Provider priority for recent form:

1. API-Football when `API_FOOTBALL_KEY` is configured, because it can provide
   fixtures, team form, standings, injuries, lineups, and some richer match
   statistics.
2. football-data.org when `FOOTBALL_DATA_API_KEY` is configured, mainly for
   fixtures, results, and standings in supported club competitions.
3. TheSportsDB, OpenLigaDB, or public pages as lower-depth fallback for
   fixtures/results context only.
4. User-provided recent form or structured match data.

Club recent-form rules:

- Prefer last 10 senior men's club matches in the same or comparable
  competition context.
- Track home/away splits when available.
- Consider schedule density, travel, rotation risk, table pressure, and
  competition type before applying Bayesian adjustments.
- Do not mix club-league scoring parameters with national-team tournament
  parameters.

National-team recent-form rules:

- Prefer last 8 senior men's national-team matches, with higher weight on
  official matches than friendlies.
- Tournament context, group incentives, neutral venue, travel, and squad
  selection matter more than club home/away splits.
- World Cup and continental tournament data should use national-team scoring
  context, not domestic league averages.

Precision rules:

- If xG/xGA aggregates are available, use them as preferred recent-form inputs.
- If only goals for/against are available, convert them to per-match proxy
  values and cap precision at `C` unless other strong data compensates.
- Small samples below the minimum window cap precision at `C`.
- Missing provider keys do not block the skill; they downgrade model confidence
  and push the assistant toward public/user-authorized fallback data.

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

Market-level grading should stay separate by market family. A match can have a
usable handicap grade while correct-score coverage remains weak, or a strong
result lean while total-goals value is unavailable. Do not collapse every market
into one match-level grade unless the report also shows the underlying market
grades.

Market-strength corrections are bounded to small deltas and must not replace
the independent model probability. Use them only when the market shape is
supported by verifiable context; otherwise treat unexplained model-market
conflict as a downgrade or Pass.

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
