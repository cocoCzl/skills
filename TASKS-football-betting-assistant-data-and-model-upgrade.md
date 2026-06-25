# TASKS: Football Betting Assistant Data And Model Upgrade

Parent PRD: `PRD-football-betting-assistant-data-and-model-upgrade.md`

The tasks below are ordered by dependency. Each task is scoped to be independently grabbable and small enough for one focused Codex session where possible.

## 1. Define The Normalized Football Snapshot Contract

Type: AFK

Blocked by: None

User stories covered: 20, 22, 23, 47

### What to build

Define the canonical JSON contract for collected football match snapshots. The contract should support China Sports Lottery match identity, kickoff timing, team names, competition, market-level availability, selection-level odds, source metadata, confidence, and field-level failure reasons.

This task should also add validation behavior for the new snapshot shape so future provider and workflow work can rely on a stable contract.

### Acceptance criteria

- [ ] A documented snapshot shape exists for match-level, market-level, selection-level, source, availability, and error metadata.
- [ ] The snapshot shape supports `match_result`, `handicap_match_result`, `correct_score`, `total_goals`, and unsupported preserved markets.
- [ ] Each market can represent `available`, `unavailable`, `unknown`, and `parse_failed` states.
- [ ] Availability reasons distinguish at least `not_offered`, `source_missing`, `waf_blocked`, `parser_error`, and `stale_source`.
- [ ] A validator accepts a representative valid snapshot and rejects missing required source, match, market, or selection fields.
- [ ] Validation warnings distinguish "market not offered" from "market could not be parsed".

## 2. Add Snapshot Fixture Examples And Contract Tests

Type: AFK

Blocked by: 1

User stories covered: 20, 21, 22, 47

### What to build

Add realistic example snapshots and raw-response fixtures that exercise the contract without depending on live network access. The examples should cover a normal match with multiple buyable markets, a match without ordinary win/draw/loss, a parse failure, and a source/WAF failure.

### Acceptance criteria

- [ ] Example normalized snapshots cover available markets, unavailable markets, parse failures, and source failures.
- [ ] Example raw fixtures are stored separately from normalized snapshots.
- [ ] Contract tests run without network access.
- [ ] Tests prove that unavailable ordinary win/draw/loss can be represented without making the match invalid.
- [ ] Tests prove that parse failure does not get normalized as a true `not_offered` market.

## 3. Implement The Sporttery Snapshot Provider Skeleton

Type: AFK

Blocked by: 1, 2

User stories covered: 1, 2, 4, 19, 20, 21

### What to build

Create the built-in `sporttery` provider as a best-effort public data collector. The first implementation should establish provider entry points, request handling, source metadata capture, raw-response saving, normalized snapshot output, and conservative failure classification.

It does not need perfect field extraction from every Sporttery surface yet; it must produce a valid snapshot or a valid source-failure result.

### Acceptance criteria

- [ ] The provider can be invoked locally and writes a normalized snapshot file.
- [ ] The provider saves raw public responses separately when responses are obtained.
- [ ] The provider records provider name, source URL, observed time, and confidence.
- [ ] HTTP/WAF/source failures are represented in the snapshot or run result without crashing silently.
- [ ] The provider never attempts login, captcha bypass, WAF bypass, aggressive endpoint scanning, or credential use.
- [ ] Unit or integration tests use fixture responses to verify successful and failed provider output.

## 4. Extract Core Sporttery Fixture And Match Identity Data

Type: AFK

Blocked by: 3

User stories covered: 1, 5, 6, 20

### What to build

Extend the `sporttery` provider to extract the current or future visible football lottery slate: lottery match number, provider match ID when available, competition, kickoff time, home team, away team, and source timing.

The output should support matching requests such as "明天世界杯", "周四001", and team-name based queries in later workflow tasks.

### Acceptance criteria

- [ ] The provider extracts match number when available.
- [ ] The provider extracts competition, kickoff time, home team, and away team for each visible football match.
- [ ] Kickoff times are represented with timezone-aware Beijing-time semantics or explicit timezone metadata.
- [ ] Provider match ID is captured when available, but absence of provider ID does not invalidate a match if other identity fields are present.
- [ ] Tests cover at least match-number based identity and team-name based identity.
- [ ] Failed or missing identity fields downgrade confidence or produce validation errors rather than being invented.

## 5. Extract Core Sporttery Market And Odds Data

Type: AFK

Blocked by: 4

User stories covered: 2, 3, 4, 7, 9, 47

### What to build

Extend the `sporttery` provider to extract core buyable football lottery markets and odds from public source data where available. Normalize China Sports Lottery market names into the canonical market names and preserve unsupported markets without including them in core analysis.

### Acceptance criteria

- [ ] `胜平负` is normalized to `match_result`.
- [ ] `让球胜平负` is normalized to `handicap_match_result`, including the handicap line when available.
- [ ] `比分` is normalized to `correct_score`.
- [ ] `总进球` is normalized to `total_goals`.
- [ ] Unsupported or secondary markets can be preserved with an unsupported marker.
- [ ] Selection-level odds are captured for available markets.
- [ ] Missing market data is represented with availability status and reason.
- [ ] Tests prove that a match without ordinary win/draw/loss does not produce a purchasable ordinary result market.

## 6. Add Developer CLI For Snapshot Collection

Type: AFK

Blocked by: 5

User stories covered: 18, 19, 20, 21, 23

### What to build

Add a developer-facing CLI for collecting football match data. The CLI should default to `china-lottery` and `sporttery`, support an output directory, write normalized snapshots, write raw responses, and avoid overwriting earlier snapshots.

The CLI is for developers and debugging, not the normal user path.

### Acceptance criteria

- [ ] The CLI supports `--mode china-lottery`, `--provider sporttery`, `--football`, and `--out`.
- [ ] The CLI defaults to China lottery Sporttery football collection when appropriate.
- [ ] Snapshot filenames include observation timestamps and do not overwrite previous files.
- [ ] Raw responses are written under a separate raw/debug output location.
- [ ] The CLI exits non-zero for invalid arguments and produces readable errors.
- [ ] The CLI has tests for successful fixture-based runs and failure runs using local fixtures or mocked provider responses.

## 7. Add Snapshot Lookup And Natural-Language Match Selection

Type: AFK

Blocked by: 6

User stories covered: 1, 5, 6, 8, 48

### What to build

Implement snapshot lookup behavior for analysis workflows. The assistant should be able to select matches from existing snapshots by lottery match number, team names, competition, and Beijing-date intent such as today, tomorrow, tonight, or a concrete date.

This task should not yet generate full HTML reports; it should return a selected slate with clear match and market status.

### Acceptance criteria

- [ ] Match lookup supports lottery match number such as 周四001.
- [ ] Match lookup supports team-name matching.
- [ ] Match lookup supports competition and date filtering.
- [ ] Relative date requests are converted into concrete Beijing dates.
- [ ] If a requested match is absent from the snapshot, the result clearly says it cannot be used in a China lottery purchase plan.
- [ ] Tests cover tomorrow/date matching, match-number matching, team matching, and no-match behavior.

## 8. Integrate Automatic Sporttery Collection Into The Skill Workflow

Type: AFK

Blocked by: 6, 7

User stories covered: 1, 12, 13, 18, 45, 48

### What to build

Update the skill workflow so normal user requests in `china-lottery` mode attempt automatic snapshot collection and lookup before analysis. Users should not need to run the CLI. If automatic collection fails or a required field is missing, the workflow should apply the agreed fallback rules and ask only for the minimum missing fields.

### Acceptance criteria

- [ ] `china-lottery` is the default mode for Chinese football lottery requests.
- [ ] Current or future China lottery analysis requests trigger automatic Sporttery collection before asking the user for odds.
- [ ] Existing snapshots can be used before live collection when suitable.
- [ ] If fixtures exist but odds are missing, the workflow permits Probability Analysis only and blocks purchase plans.
- [ ] If odds/handicaps are required and unavailable, the workflow asks for the minimum missing fields.
- [ ] The workflow wording explicitly avoids invented fixtures, odds, handicaps, lineups, injuries, standings, or market movement.

## 9. Enforce China Lottery Market Consistency In Purchase Plans

Type: AFK

Blocked by: 8

User stories covered: 2, 3, 7, 11, 14

### What to build

Add guardrails so China lottery purchase plans can only use markets confirmed as buyable in the Sporttery snapshot or user-provided China lottery data. International bookmaker odds may be shown as market reference only and cannot replace China lottery odds.

### Acceptance criteria

- [ ] Purchase plans exclude unavailable China lottery markets.
- [ ] Ordinary win/draw/loss analysis can appear as Probability Analysis even when not buyable, but cannot appear as a purchase-plan leg.
- [ ] The workflow distinguishes `china-lottery`, `international-odds`, and `analysis-only` modes.
- [ ] Third-party bookmaker odds are labeled as international market reference in `china-lottery` mode.
- [ ] Tests verify that unavailable markets cannot be used in ticket tiers.
- [ ] Tests verify that third-party odds cannot become China lottery purchase odds.

## 10. Generate HTML Reports From Snapshot-Backed Analysis

Type: AFK

Blocked by: 8, 9

User stories covered: 6, 7, 11, 44, 45, 46

### What to build

Connect snapshot-backed slate selection and market data to completed pre-match HTML report generation. The report should show source-aware fixture confirmation, buyable market status, odds/handicap tables, Probability Analysis, Value Judgment only when available, score coverage, and ticket candidates using only valid markets.

### Acceptance criteria

- [ ] Completed pre-match analysis from a snapshot generates an HTML report.
- [ ] Chat output after success is limited to a concise summary and report path.
- [ ] The report includes source and observation time for snapshot data.
- [ ] The report separates Probability Analysis from Value Judgment.
- [ ] The report marks missing odds/markets and suppresses purchase plans when required.
- [ ] If HTML generation fails, the assistant returns the error reason and snapshot path without dumping a full report into chat.

## 11. Save Prediction Snapshots Linked To HTML Reports

Type: AFK

Blocked by: 10

User stories covered: 23, 24, 41, 42, 43

### What to build

When an HTML report is generated, save a corresponding prediction snapshot with a shared report ID. The prediction snapshot should preserve the pre-match data, model probabilities, market grades, score coverage, selected ticket plans, source metadata, and report path.

### Acceptance criteria

- [ ] Every completed HTML report has a corresponding prediction snapshot.
- [ ] The HTML report and prediction snapshot share a report ID.
- [ ] Prediction snapshots include pre-match source data and observation times.
- [ ] Prediction snapshots include model probabilities, market grades, score coverage, and portfolio selections.
- [ ] Prediction snapshots are not overwritten by later reports.
- [ ] Generated prediction snapshots are documented as generated artifacts that should not be committed by default.

## 12. Document Normal Use, CLI Debugging, Providers, And Fallbacks

Type: AFK

Blocked by: 6, 8, 9

User stories covered: 16, 17, 18, 19, 48

### What to build

Update user-facing documentation so GitHub users understand normal natural-language use, developer CLI use, provider configuration, optional API keys, fallback behavior, and data-source boundaries.

Documentation must include realistic environment-variable examples for `API_FOOTBALL_KEY` and `FOOTBALL_DATA_API_KEY`, plus descriptions of API-Football, football-data.org, TheSportsDB, OpenLigaDB, and The Odds API.

### Acceptance criteria

- [ ] Documentation shows the normal zero-operation user flow.
- [ ] Documentation shows CLI usage for developer/debug snapshot collection.
- [ ] Documentation explains that `sporttery` is best-effort public data collection, not a guaranteed official API.
- [ ] Documentation includes realistic examples for `API_FOOTBALL_KEY` and `FOOTBALL_DATA_API_KEY`.
- [ ] Documentation lists the supported and optional data providers and what each can provide.
- [ ] Documentation states that third-party bookmaker odds cannot replace China lottery buyable odds in `china-lottery` mode.
- [ ] Documentation explains fallback behavior when fixtures, odds, or markets are missing.

## 13. Add Team Type And Competition-Parameter Rules

Type: AFK

Blocked by: 10

User stories covered: 26, 27, 30, 31, 32

### What to build

Add documented and testable model rules for `club`, `national`, and `unknown` team types. Youth and women's matches should be unsupported for formal purchase plans. Competition scoring parameters must be separated by club and national contexts, with confidence caps when suitable parameters are missing.

### Acceptance criteria

- [ ] Supported team types are `club`, `national`, and `unknown`.
- [ ] Youth and women's matches are marked unsupported for formal purchase plans.
- [ ] Club and national team recent-form or competition-parameter pools are not mixed.
- [ ] Missing exact competition parameters can fall back to same-type defaults with confidence caps.
- [ ] Global defaults cannot produce A-grade precision without suitable competition context.
- [ ] Tests cover club, national, unknown, and unsupported team type handling.

## 14. Add Recent-Form Provider Guidance And xG Prior Conversion Rules

Type: AFK

Blocked by: 12, 13

User stories covered: 16, 17, 25, 28, 29

### What to build

Define how optional third-party team data feeds into the model. API-Football should be the preferred enhanced provider, with football-data.org and lower-depth public sources as fallback. Recent form should convert into xG-prior inputs automatically when enough data exists, with lower precision when only goals for/against are available.

### Acceptance criteria

- [ ] Documentation explains how API-Football, football-data.org, TheSportsDB, and OpenLigaDB can contribute team-context data.
- [ ] Recent-form rules distinguish club and national team windows.
- [ ] Club rules include recent form, home/away splits, schedule density, competition type, rotation risk, and table pressure.
- [ ] National team rules include official-match emphasis, tournament context, group incentives, neutral venue, travel, and squad selection.
- [ ] Goals for/against can be used as a lower-precision proxy when xG/xGA is unavailable.
- [ ] Missing provider keys do not block the skill, but downgrade model confidence.

## 15. Add Market-Strength, Implied Probability, And Market-Level Grade Rules

Type: AFK

Blocked by: 10, 13

User stories covered: 9, 33, 34, 35, 56, 57, 58

### What to build

Enhance model and report rules so odds shape, handicap depth, raw implied probability, market margin/return rate, no-vig probability, and edge are handled consistently. Ratings should be separated by market family rather than assigning only one match-level grade.

### Acceptance criteria

- [ ] Complete markets calculate raw implied probability and no-vig probability.
- [ ] Incomplete markets are labeled approximate or unavailable for full Value Judgment.
- [ ] Market strength can act as a bounded correction, but does not replace independent model probability.
- [ ] Model-market conflicts downgrade or produce Pass when unexplained.
- [ ] Reports can show separate ratings for match result, handicap result, total goals, correct score, and overall match.
- [ ] Tests cover a match where result grade is stronger than correct-score grade.

## 16. Add Correct-Score Concentration And Coverage Rules

Type: AFK

Blocked by: 15

User stories covered: 10, 35, 36

### What to build

Add correct-score quality rules based on the Poisson score matrix. Reports and portfolio construction should avoid treating diffuse score distributions as strong score picks.

### Acceptance criteria

- [ ] Single top score below 10% cannot be labeled a strong single-score main pick.
- [ ] Top 3 cumulative probability below 25% marks score coverage as weak.
- [ ] Top 4-5 cumulative probability below 33% prevents score tickets from becoming the core portfolio.
- [ ] High total-xG or clear two-way scoring paths widen or downgrade score coverage.
- [ ] Score coverage explains primary path, secondary path, and missed-path protection.
- [ ] Tests cover concentrated, moderate, and diffuse score matrices.

## 17. Add Conservative Portfolio Objective And Correlation Controls

Type: AFK

Blocked by: 9, 15, 16

User stories covered: 7, 8, 37, 43

### What to build

Add portfolio construction rules that choose ticket candidates from buyable markets, model confidence, market agreement, score concentration, and correlation. The default risk preference is conservative unless the user explicitly asks for high-variance ideas.

### Acceptance criteria

- [ ] Pass, unavailable, and low-data legs are excluded from main plans.
- [ ] C-grade legs do not appear in conservative main plans.
- [ ] Score tickets use only the strongest score-concentration matches.
- [ ] Same-match multi-market correlation is detected and explained.
- [ ] Same group/stage/weather/schedule correlation can be noted when present.
- [ ] High-variance or high-odds ideas are separated from the main plan.
- [ ] Tests cover no forced fourfold/eightfold behavior.

## 18. Add Late Update, Odds Movement, And Stop Rules

Type: AFK

Blocked by: 11, 15

User stories covered: 38, 39, 40

### What to build

Add freshness and timing rules for pre-match reports. The assistant should cap grades before late information is available, require reevaluation on major odds movement, and refuse new purchase plans after kickoff or when sales availability cannot be confirmed.

### Acceptance criteria

- [ ] More than 12 hours before kickoff, early analysis is capped at B.
- [ ] Two to six hours before kickoff, the workflow attempts or requests injury, lineup, and market updates.
- [ ] Within 60 minutes of kickoff, missing confirmed lineups prevent A grade.
- [ ] Match-result odds movement of at least 0.08 creates a light warning.
- [ ] Match-result odds movement of at least 0.15 creates a material movement warning and triggers reevaluation.
- [ ] Handicap-line or total-goals center movement triggers reevaluation.
- [ ] Already-started or unavailable-for-sale matches do not receive new pre-match purchase plans.

## 19. Add Post-Match Result Attachment And Review Metrics

Type: AFK

Blocked by: 11, 17, 18

User stories covered: 41, 42, 43

### What to build

Enable post-match review from saved prediction snapshots. The first slice should attach final scores to a prediction snapshot and compute basic review metrics without requiring historical odds backfill.

### Acceptance criteria

- [ ] A saved prediction snapshot can be located by report ID.
- [ ] A final score can be attached to the prediction snapshot or review record.
- [ ] Review output includes match result hit/miss.
- [ ] Review output includes handicap result hit/miss when the market and line were present.
- [ ] Review output includes total-goals hit/miss when the market and line were present.
- [ ] Review output includes correct-score Top 1, Top 3, and coverage-set hit/miss when candidates were present.
- [ ] Review output includes grade breakdown fields suitable for future calibration.

## 20. Add End-To-End Smoke Tests For The Zero-Operation Flow

Type: AFK

Blocked by: 10, 11, 12

User stories covered: 1, 2, 6, 11, 44, 45, 46, 48

### What to build

Add smoke tests or scripted checks that exercise the expected user path with fixture data: natural-language request, automatic snapshot use or collection, slate selection, China lottery market validation, HTML report generation, concise chat summary behavior, and prediction snapshot persistence.

### Acceptance criteria

- [ ] A "明天比赛" style request can be exercised against fixture data without manual command execution.
- [ ] The workflow selects the correct slate from a snapshot.
- [ ] Unavailable markets are not used in purchase plans.
- [ ] A completed run writes an HTML report.
- [ ] A completed run writes a prediction snapshot linked by report ID.
- [ ] A failed HTML generation path reports the error and snapshot path without producing a full chat report.
- [ ] Tests or checks can run without live network access.
