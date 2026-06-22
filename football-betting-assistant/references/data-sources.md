# Data Sources

The assistant should actively verify current information when tools are available. Do not rely on model memory for current fixtures, odds, lineups, injuries, weather, or market movement.

## Source Priority

1. User-provided source, screenshot, table, link, or structured data.
2. Configured football data provider or API result. For odds and lines, prefer The Odds API when `THE_ODDS_API_KEY` is configured.
3. Public web search or browser verification.
4. User clarification for missing data.

## Data Source Credentials

Data Source Credentials are optional credentials for football data providers: odds, fixtures, lineups, injuries, team stats, or weather. They are not large-model API keys.

Never write credentials into reports, examples, references, or scripts. Refer to environment variables or local configuration names only.

## Provider Configuration

This skill does not include credentials, but it may use a configured provider adapter when the current agent environment exposes one. A "configured football data provider or API result" means the current agent environment already exposes a user-authorized data capability, such as:

- MCP or tool calls for fixtures, odds, lineups, injuries, team stats, or weather.
- A local or internal HTTP service that the agent can call.
- Local JSON, CSV, database, or exported files supplied by the user.
- Environment variables or local config names that a separate adapter uses, such as `API_FOOTBALL_KEY`, `THE_ODDS_API_KEY`, or `WEATHER_API_KEY`.

Do not assume these providers exist. If no callable provider is available, use public/user-authorized sources when tools allow it, then fall back to asking the user for the minimum missing data.

## Recommended Odds Provider

For odds and lines, the default recommended provider is **The Odds API** because it is designed for multi-bookmaker odds aggregation. The public official site shows a Starter free tier with 500 credits per month and support for soccer, head-to-head odds, spreads/handicap, and totals/over-under markets. Use `THE_ODDS_API_KEY` only when the user or environment has configured it.

When The Odds API is available, request these markets first:

- `h2h` for 胜平负 / match result.
- `spreads` for handicap / 让球 lines.
- `totals` for 大小球 / over-under lines.

Normalize provider output into the skill's Odds Data fields, including source, bookmaker, observed time, line, decimal odds, and confidence. If multiple bookmakers are returned, summarize the consensus range and highlight outliers instead of copying every price.

## Optional Context Providers

API-Football can be useful for fixtures, lineups, injuries, team stats, and some odds. Treat it as a complementary context provider unless the user specifically configures it as the primary odds source.

Discovering an API through web search does not make it a configured provider. Do not auto-register accounts, request keys on the user's behalf, guess keys, call unknown free APIs, or treat unauthenticated endpoints as authorized data sources.

## Public Web Verification Responsibility

When browsing, search, or webpage-reading tools are available, the assistant should actively perform public web verification itself. The user does not need to manually paste public data unless tools are unavailable, public access fails, sources conflict, or the user has a more authoritative source.

If public pages require login, bypassing restrictions, captcha solving, or unauthorized scraping, stop using that source and downgrade or ask the user for authorized data.

## Public-Web-First Mode Without API Keys

When no odds API key is configured but browsing or search tools are available, behave like a web-enabled assistant:

1. Search for the exact fixture plus odds terms, such as `[home team] [away team] odds`, `[home team] vs [away team] handicap`, `[competition] odds`, or Chinese equivalents like `赔率`, `盘口`, `让球`, `大小球`.
2. Prefer pages that visibly publish current odds or lines, such as odds aggregators, bookmaker public pages, official lottery pages, or reputable live-score/odds pages.
3. Open candidate pages and extract only data that is visible without login, captcha bypassing, paid access, or restricted scraping.
4. Record source names, accessed time, market, line, and prices. If a page is a prediction article rather than an odds table, label it as prediction/context, not Odds Data.
5. Try up to two alternative public sources after the first failure or conflict, then apply the Retrieval Stop Rule.

This mode should feel as helpful as a web ChatGPT search, but it must be more explicit about source quality. If public odds are found, include them and continue with Value Judgment at the appropriate confidence level. If only predictions or stale pages are found, use them as context and say that verifiable Odds Data is still missing.

## Credential Fallback

If no provider credential exists:

1. Try public or user-authorized sources.
2. Apply the Retrieval Stop Rule.
3. Ask the user for missing critical data if public collection fails.
4. Downgrade rather than inventing current data.

## Required Current Data

For every current data item, record a Source Timestamp:

- Source name.
- Accessed or observed time.
- Timezone when relevant.
- Whether the data is confirmed, expected, stale, unavailable, or conflicting.

## Multi-Source Odds Check

For odds value judgment, prefer more than one odds source. If only one source is available:

- Continue only if the source is usable.
- Mark odds confidence as lower.
- Downgrade Value Judgment.

Do not treat one bookmaker as market consensus.

## Odds And Line Display

When odds or lines are found, include a compact odds table in the report. Show:

- Market: 胜平负, 让球/handicap, 大小球/totals, or 比分 if available.
- Source/bookmaker or aggregator.
- Observed time and timezone.
- Line, where applicable.
- Decimal prices or price range.
- Confidence and whether the source is single-source or multi-source.

If odds collection fails, state the failure category: no configured provider, public page blocked, login/captcha required, market unavailable, source conflict, or stale data.

## Source Conflict Handling

When sources conflict:

1. Surface the conflict in the Data Summary Table or risk notes.
2. Prefer official, fresher, or more specialized sources when justified.
3. If unresolved, mark the field uncertain.
4. Downgrade Data Confidence.
5. Do not silently average conflicting match facts.

## Retrieval Stop Rule

For each key category, try the primary source and no more than two alternative public or authorized sources. If still unavailable, mark the gap and continue only if Information Sufficiency remains adequate.

Key categories:

- Fixture identity.
- Odds and lines.
- Lineups and injuries.
- Team form and attacking/defensive output.
- Weather and venue context.
- Competition incentives.

## Excluded Collection Methods

Do not:

- Log into bookmaker accounts.
- Bypass access restrictions, captchas, rate limits, or regional controls.
- Depend on unauthorized scraping.
- Hardcode bookmaker credentials.
- Claim to have live odds when no source was checked.
