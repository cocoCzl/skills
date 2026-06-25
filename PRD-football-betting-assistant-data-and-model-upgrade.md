# PRD: Football Betting Assistant Data And Model Upgrade

## Problem Statement

The current football betting assistant can produce Chinese football lottery analysis with expected goals, Bayesian adjustments, Poisson score probabilities, implied-probability checks, Reference Grades, and HTML reports. However, the user still has to provide too much current match data manually, especially China Sports Lottery / 竞彩 fixtures, buyable markets, handicap lines, and odds. This makes normal use cumbersome and weakens analysis quality because the assistant may lack the actual market surface needed for a proper Value Judgment.

The user wants the skill to behave more like a real football betting assistant: the user should be able to ask naturally, such as "帮我看下北京时间明天的几场世界杯比赛", and the skill should automatically collect the current or future football lottery slate, identify buyable markets, analyze odds and handicaps, run the math model, produce score coverage and ticket candidates, and save an HTML report without requiring screenshots or manual command-line steps unless automatic collection fails.

The user also wants future model quality to improve. The first priority is higher hit rate, followed by more reasonable recommendations, better odds-value judgment, and better correct-score coverage. The agreed path is to improve the data pipeline first, then enhance model inputs, market comparison, score coverage, portfolio construction, and post-match calibration.

## Solution

Build a default `china-lottery` data flow for the football betting assistant.

The skill will include a best-effort `sporttery` provider that collects publicly visible China Sports Lottery football data from `sporttery.cn` pages, public HTML fragments, or public endpoints. It will collect the current or future visible football lottery slate, match numbers, kickoff times, competitions, home and away teams, buyable markets, handicap lines, and odds. The provider is not treated as an official stable API. It must stop and mark missing fields when public access fails, pages change, WAF blocks access, login is required, or odds cannot be parsed.

The normal user path is zero-operation. In `china-lottery` mode, when the user asks for current or future football betting analysis, the assistant must first attempt automatic data collection and local snapshot generation. The user should not need to run a command manually. CLI commands remain available for developers, debugging, and scheduled jobs.

The assistant will read standardized JSON snapshot files, match the user's natural-language request against the slate, run existing and enhanced model calculations, and generate only an HTML report for completed pre-match analysis. Chat output should remain a concise summary plus the report path.

The solution also defines a V2 model enhancement path: configurable third-party providers for team recent form, competition-specific parameters, market-strength corrections, separate market ratings, score concentration thresholds, portfolio objective functions, correlation controls, late-update rules, prediction snapshots, and post-match review metrics.

## User Stories

1. As a China Sports Lottery user, I want to ask for tomorrow's football matches in natural language, so that I do not need to manually collect fixtures and odds.

2. As a China Sports Lottery user, I want the assistant to use the official lottery buyable market surface as the purchase-plan source, so that recommendations match what I can actually buy.

3. As a China Sports Lottery user, I want ordinary win/draw/loss to be excluded from purchase plans when it is not available for a match, so that reports do not recommend unavailable markets.

4. As a China Sports Lottery user, I want the assistant to collect handicap result, correct score, total goals, and other visible football lottery markets, so that it can choose the most suitable buyable market family.

5. As a China Sports Lottery user, I want match numbers such as 周四001 to be supported, so that I can refer to matches using the local lottery convention.

6. As a China Sports Lottery user, I want the assistant to analyze every match in the requested slate, so that weak matches can be excluded rather than silently ignored.

7. As a China Sports Lottery user, I want the assistant to build ticket plans from the actual model confidence and buyable markets, so that it does not force fixed fourfold or eightfold structures.

8. As a cautious user, I want the default portfolio risk preference to be conservative, so that the main plan avoids low-confidence legs.

9. As a user seeking odds value, I want odds to be converted into implied and no-vig probabilities, so that Value Judgment is based on model probability versus market probability.

10. As a user seeking score recommendations, I want correct-score coverage to show cumulative probability and missing paths, so that score tickets are not presented as falsely stable.

11. As a user seeking a realistic assistant, I want the report to separate Probability Analysis from Value Judgment, so that analysis without odds is not mistaken for a buy recommendation.

12. As a user, I want the assistant to immediately ask for missing odds and handicap lines when automatic China lottery data collection fails, so that it does not invent market data.

13. As a user, I want basic probability analysis to continue when fixtures are available but odds are missing, so that I still get useful football context without a purchase plan.

14. As a user, I want third-party bookmaker odds to be used only as international market reference in China lottery mode, so that they do not replace actual 竞彩 buyable odds.

15. As an international user, I want an `international-odds` mode, so that I can use The Odds API or another authorized bookmaker provider instead of China lottery data.

16. As a GitHub user, I want the skill documentation to explain how to configure `API_FOOTBALL_KEY` and `FOOTBALL_DATA_API_KEY`, so that I can add team recent-form data when I have provider access.

17. As a GitHub user, I want the documentation to list supported and optional data providers, so that I understand what works without credentials and what requires keys.

18. As a GitHub user, I want examples for both normal natural-language use and developer CLI use, so that I can use the skill without reading code.

19. As a developer, I want a CLI for snapshot collection, so that I can debug the data pipeline and run scheduled collection jobs.

20. As a developer, I want standardized JSON snapshots, so that data collection, model calculation, HTML rendering, and future backtesting share one contract.

21. As a developer, I want raw public responses saved separately from normalized snapshots, so that parser failures can be diagnosed when pages change.

22. As a developer, I want field-level availability and error reasons, so that unavailable markets are distinguishable from parser failures.

23. As a developer, I want snapshots to never overwrite previous snapshots, so that odds movement and analysis timing can be reviewed.

24. As a developer, I want generated snapshots and reports treated as generated output, so that they are not committed by default.

25. As a model user, I want team recent form to include near-term and broader windows, so that analysis is not overfit to only the last five matches.

26. As a model user, I want club and national team matches handled separately, so that club league form is not mixed with national team competition form.

27. As a model user, I want youth and women's matches excluded from the supported scope, so that the model does not overreach into data contexts not targeted by the feature.

28. As a model user, I want club matches to consider schedule density, rotation motivation, league position, cup priorities, and upcoming fixtures, so that xG adjustments reflect club-specific incentives.

29. As a model user, I want national team matches to consider group stage, qualification pressure, goal difference needs, neutral venues, travel, and tournament path, so that motivation is modeled correctly.

30. As a model user, I want competition-specific scoring environments, so that Premier League, Serie A, World Cup, and Asian Cup matches do not all share one generic goal prior.

31. As a model user, I want club competition parameters derived only from club competition data and national team parameters derived only from national team data, so that incompatible scoring environments are not mixed.

32. As a model user, I want missing competition parameters to downgrade Model Confidence, so that the report does not overstate precision.

33. As a model user, I want market strength and odds shape to influence the prior as a bounded correction, so that the model respects market information without simply copying the market.

34. As a model user, I want model-market conflicts to be surfaced and downgraded when unexplained, so that the assistant avoids forcing contrarian recommendations without evidence.

35. As a model user, I want separate grades for match result, handicap result, total goals, correct score, and overall match, so that a strong result lean does not imply a strong score recommendation.

36. As a model user, I want score concentration thresholds, so that low-probability exact scores are not treated as strong picks.

37. As a model user, I want portfolio correlation checks, so that one wrong match script does not silently damage multiple supposedly diversified tickets.

38. As a model user, I want late update rules for lineups, injuries, weather, and odds movement, so that near-kickoff recommendations are not stale.

39. As a model user, I want missing lineups near kickoff to cap Reference Grade, so that A grades require adequate late information.

40. As a model user, I want start-time and sales-status checks, so that the assistant does not generate pre-match purchase plans after kickoff or when markets are unavailable.

41. As a model user, I want every completed report to save a prediction snapshot, so that future review and calibration can happen without reconstructing historical inputs.

42. As a model user, I want prediction snapshots linked to HTML reports through a shared report ID, so that post-match review can locate the exact pre-match assumptions.

43. As a model user, I want post-match review metrics for result, handicap, totals, score coverage, grade reliability, and Brier score, so that future calibration has measured feedback.

44. As a user, I want reports to remain HTML-only for completed pre-match analysis, so that long multi-match reasoning is readable and not dumped into chat.

45. As a user, I want concise chat output after successful HTML generation, so that the conversation stays usable.

46. As a user, I want a clear failure response when HTML generation fails, so that I know where the snapshot is and why the report was not produced.

47. As a user, I want unsupported markets to be preserved in the snapshot but excluded from core analysis until supported, so that future extension does not lose source data.

48. As a user, I want the assistant to ask only for the minimum missing fields when automation fails, so that manual fallback remains lightweight.

## Implementation Decisions

- The default runtime mode for China Sports Lottery requests is `china-lottery`.

- `china-lottery` mode uses a built-in `sporttery` provider by default.

- The `sporttery` provider is a best-effort collector for publicly visible China Sports Lottery football data. It is not described as an official stable API client.

- The normal user path is natural-language only. The assistant automatically attempts data collection before analysis.

- A CLI remains available for developer debugging, scheduled jobs, and manual snapshot generation, but it is not the primary user path.

- The first data-collection milestone focuses on core ticket data: fixtures, match numbers, competitions, kickoff times, home and away teams, buyable markets, handicap lines, and odds.

- First milestone collection does not include deep team recent form, standings, injuries, or news as hard requirements. Those are model-enhancement inputs.

- The collector must use conservative public access only. It must not log into accounts, bypass WAF, bypass captcha, scan hidden endpoints aggressively, or evade access controls.

- Known public pages, public HTML fragments, and verified public endpoints may be maintained as provider entry points. The provider should not behave as a generic endpoint discovery crawler.

- The assistant fallback order in `china-lottery` mode is: local snapshot, automatic `sporttery` collection, browser/public page fallback, configured international provider as reference only, then minimum user clarification.

- If China lottery odds or handicaps are unavailable and no authorized fallback data exists, the assistant must stop full Value Judgment and ask for odds/handicap input.

- If fixtures are available but odds are missing, the assistant may produce Probability Analysis only, with no purchase plan and no odds-value claim.

- Third-party bookmaker odds must not replace China lottery buyable odds inside China lottery purchase plans.

- `international-odds` mode is separate from `china-lottery` mode and may use The Odds API or a custom authorized provider.

- `analysis-only` mode is used when odds or buyable markets are missing.

- Normalized snapshots are written as JSON files.

- Raw provider responses are saved separately for debugging and parser maintenance.

- Snapshots must not overwrite prior snapshots. Snapshot filenames include an observation timestamp.

- Every snapshot records source name, source URL when available, observed time, and data confidence.

- Every market records availability status and reason. `not_offered`, `source_missing`, `waf_blocked`, `parser_error`, and `stale_source` are distinct outcomes.

- Market data is normalized around matches, markets, and selections.

- Core market mapping is:
  - `胜平负` maps to `match_result`.
  - `让球胜平负` maps to `handicap_match_result`.
  - `比分` maps to `correct_score`.
  - `总进球` maps to `total_goals`.
  - Unsupported or secondary markets may be preserved but excluded from core analysis.

- Match lookup supports lottery match number, provider match ID when available, team names, competition, and kickoff time.

- The assistant must convert relative dates such as "明天" or "今晚" into concrete Beijing dates.

- Current and future visible China lottery lists are supported first. Arbitrary far-future dates are not guaranteed.

- If a user-specified match is not present in the China lottery snapshot, it cannot be used in a China lottery purchase plan.

- Completed pre-match analysis generates an HTML report only. Chat output is limited to a short summary and the report path.

- If HTML rendering fails, the assistant returns the failure reason and snapshot path, not a full long-form replacement report.

- Every completed HTML report should have a corresponding prediction snapshot and shared report ID.

- Prediction snapshots include pre-match data, model probabilities, market grades, portfolio choices, score coverage, and report metadata.

- Future post-match review attaches final results to prediction snapshots through report ID.

- Team type scope is limited to `club`, `national`, and `unknown`. Youth and women's matches are unsupported for formal purchase plans.

- Club and national team models use separate recent-form logic and competition parameter pools.

- Club recent form uses recent overall form, home/away splits, schedule density, competition type, rotation risk, and table pressure.

- National team recent form emphasizes recent official matches, tournament context, group-table incentives, neutral venue, travel, squad selection, and qualification pressure.

- Recent form should be converted into xG-prior inputs automatically. Real xG/xGA is preferred; goals for/against may be used as a lower-precision proxy with downgraded confidence.

- Match type and competition type affect weighting. Friendlies, heavy rotation matches, cross-competition samples, and low-relevance fixtures receive lower weight.

- Competition scoring environments are type-specific. Club league parameters must not be applied directly to national team tournaments.

- Missing competition parameters cap Model Confidence and downgrade score coverage.

- Market odds and handicap shape may act as bounded model corrections, but they must not replace independent probability estimation.

- If team data and market signal conflict, market signal is respected but not blindly followed. Unexplained conflicts downgrade the grade or produce Pass.

- Odds analysis must calculate raw implied probability, market margin or return-rate where possible, no-vig probability, and edge.

- Market-level grades are separate: match result, handicap result, total goals, correct score, and overall match.

- Correct-score ratings are more conservative than direction-market ratings.

- Correct-score coverage uses concentration thresholds:
  - single top score below 10% should not be presented as a strong single-score main pick.
  - Top 3 below 25% means weak score coverage.
  - Top 4-5 below 33% means score tickets should not be the core portfolio.
  - high total-xG or clear two-way scoring paths widen or downgrade score coverage.

- The portfolio constructor uses a conservative default objective: exclude Pass and unavailable markets, prefer model-market agreement, avoid C-grade main legs, reduce correlation, and avoid forcing weak legs.

- High-variance or high-odds ideas are separated from the main plan.

- Late update rules cap grades by data freshness:
  - more than 12 hours before kickoff: early analysis, maximum grade B.
  - 2-6 hours before kickoff: attempt injury, lineup, and market updates.
  - within 60 minutes: confirmed lineup should be checked if available; missing lineup prevents A grade.
  - major odds or line movement forces reevaluation.

- Odds movement thresholds begin with conservative defaults:
  - any match-result option movement of at least 0.08 is a light movement warning.
  - movement of at least 0.15 is a material movement warning and triggers reevaluation.
  - handicap-line movement or major total-goals center movement triggers reevaluation.

- Stop rules prevent pre-match purchase plans after kickoff, after sales close, or when sales availability cannot be confirmed near kickoff.

## Testing Decisions

- Tests should verify external behavior and data contracts rather than parser internals.

- The highest-value test seam is the provider-to-snapshot contract: given representative public HTML/API fixtures or raw response files, the provider produces the expected normalized snapshot.

- Snapshot validation should test required match fields, market fields, selection fields, source timestamps, confidence, availability status, and error reasons.

- Fallback behavior should be tested at the workflow seam: when odds are missing, the assistant produces Probability Analysis only and does not produce Value Judgment or purchase plans.

- China lottery market consistency should be tested: unavailable ordinary match result markets cannot appear in purchase plans.

- International provider behavior should be tested separately: third-party odds may appear as market reference in China lottery mode but not as China lottery purchase odds.

- CLI behavior should be tested through generated snapshot files, exit codes, and validation messages.

- HTML report generation should be tested from normalized snapshots and prediction records, confirming that a completed report is written and chat output can remain concise.

- Prediction snapshot generation should be tested to ensure report ID, observed time, model probabilities, market grades, portfolio selections, and score coverage are preserved.

- Model tests should cover club versus national team separation, unsupported youth/women team types, missing competition parameters, and confidence caps.

- Odds analysis tests should cover raw implied probability, market margin, no-vig probability, and edge calculations for complete and incomplete markets.

- Correct-score tests should cover concentration thresholds and downgrade behavior when score mass is diffuse.

- Portfolio-construction tests should cover conservative defaults, no C-grade main legs, no unavailable markets, exact-score leg limits, and correlation warnings.

- Late-update tests should cover kickoff windows, lineup availability caps, material odds movement, and no-purchase-plan behavior after kickoff.

- Existing deterministic calculator scripts are prior art for model calculation tests. Existing input validators and HTML renderer are prior art for contract and generated-report tests.

## Acceptance Criteria

1. A user can ask a natural-language China lottery football question without manually running a command, and the assistant attempts automatic data collection before analysis.

2. The default mode for Chinese football lottery requests is `china-lottery`.

3. The first version includes a built-in `sporttery` provider that attempts to collect current or future publicly visible football lottery fixtures, buyable markets, handicaps, and odds.

4. The provider writes a normalized JSON snapshot with match-level and market-level data.

5. The provider writes raw responses separately for debugging when available.

6. Snapshot files include observation timestamps and do not overwrite earlier snapshots.

7. Each market includes availability status and a reason when unavailable or unknown.

8. The assistant can match user requests by lottery match number, team names, competition, and kickoff time.

9. If a market is not available in the China lottery snapshot, it is not used in a China lottery purchase plan.

10. If odds or handicap data cannot be obtained for a China lottery purchase-plan request, the assistant stops full Value Judgment and asks for the minimum missing odds/handicap input.

11. If fixtures are available but odds are not, the assistant may produce downgraded Probability Analysis only and must not output a purchase plan.

12. Third-party bookmaker odds cannot be used as replacement China lottery odds in `china-lottery` mode.

13. Completed pre-match analysis generates an HTML report and does not dump the full report into chat.

14. The chat response after successful report generation is limited to a concise summary and the HTML path.

15. If HTML generation fails, the assistant returns the error reason and snapshot path without outputting the full report in chat.

16. The documentation explains normal natural-language use and developer CLI/debug use.

17. The documentation includes real environment-variable examples for `API_FOOTBALL_KEY` and `FOOTBALL_DATA_API_KEY`.

18. The documentation lists supported and optional data sources and states what each source can and cannot provide.

19. The documentation explains that the `sporttery` provider is best-effort public data collection, not a guaranteed official API.

20. The documentation states that missing data must downgrade confidence or trigger clarification rather than being invented.

21. V2 model rules are documented for club/national separation, team recent form, competition parameters, market corrections, score thresholds, portfolio objective functions, late updates, prediction snapshots, and post-match review.

22. Youth and women's matches are marked unsupported for formal purchase plans.

23. Club and national team data are not mixed for recent form or competition parameters.

24. Market-level ratings can differ within a match, such as result A/B and score C/Pass.

25. Correct-score recommendations include concentration logic and do not present diffuse score distributions as stable.

26. Portfolio construction defaults to conservative behavior unless the user explicitly requests aggressive or high-variance ideas.

27. Every completed report can be paired with a prediction snapshot through a report ID.

28. Generated snapshots, prediction files, and HTML reports are treated as generated artifacts that should not be committed by default.

## Non-Functional Requirements

- The normal user experience must be zero-operation: no command-line step is required for ordinary analysis.

- The data pipeline must be source-aware. Every current-data field should include source and observation time when available.

- The provider must be resilient to partial failure. Missing fields should be represented explicitly instead of crashing the whole workflow when possible.

- The system must not invent fixtures, odds, handicaps, lineups, injuries, standings, or market movement.

- The system must respect public-data boundaries. It must not bypass login, WAF, captcha, paywalls, rate limits, or access restrictions.

- The normalized snapshot schema should be stable enough for analysis, report rendering, prediction snapshots, and future calibration.

- The implementation should use deterministic scripts for calculations where possible, so reports are reproducible.

- Reports must remain Chinese user-readable and explain the evidence chain without overclaiming certainty.

- The assistant must avoid certainty, pressure, bankroll-allocation, Kelly sizing, and chase-loss language.

- The default portfolio behavior must be conservative and should not force weak matches into tickets.

- The feature must remain usable without optional third-party API keys, but model confidence may be downgraded.

- Optional API credentials must be referenced only through environment variables or local configuration and must never be written into reports, examples, references, or generated outputs.

## Out of Scope

- Backfilling historical China lottery odds or handicap data.

- Guaranteeing access to private, official, undocumented, or stable Sporttery APIs.

- Bypassing WAF, captcha, login, regional restrictions, paywalls, rate limits, or other access controls.

- Automatically registering accounts or acquiring API keys for third-party providers.

- Treating third-party bookmaker odds as China Sports Lottery buyable odds.

- Requiring ordinary users to run command-line scripts before asking for analysis.

- Supporting youth-team or women's football purchase-plan analysis in this scope.

- Building a full generic web crawler for arbitrary betting websites.

- Producing bankroll allocation, Kelly bet sizing, chase-loss plans, recovery betting, or guaranteed-pick language.

- Producing completed pre-match reports as Markdown instead of HTML.

- Making historical hit-rate improvement claims before enough prediction snapshots and post-match results exist.

- Replacing transparent model reasoning with unexplained black-box predictions.

## Further Notes

- The first implementation should prioritize automatic China lottery snapshot collection and HTML report flow before deeper team-data modeling.

- Historical backtesting is not required before the first release, but prediction snapshots should be saved from the start so future calibration becomes possible without reconstructing old inputs.

- Optional provider documentation should include at least API-Football, football-data.org, TheSportsDB, OpenLigaDB, and The Odds API, with clear notes about free-tier limitations and suitable use.

- The agreed priority order is: hit rate, recommendation reasonableness, odds-value judgment, then correct-score coverage. The PRD supports this by first improving data availability, then saving predictions for calibration, then improving model inputs and portfolio construction.

- Any future issue breakdown should separate the work into independently shippable slices: Sporttery snapshot provider, snapshot schema and validator, workflow integration, HTML report integration, provider documentation, model-enhancement rules, prediction snapshots, and post-match review.
