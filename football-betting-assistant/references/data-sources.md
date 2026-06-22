# Data Sources

The assistant should actively verify current information when tools are available. Do not rely on model memory for current fixtures, odds, lineups, injuries, weather, or market movement.

## Source Priority

1. User-provided source, screenshot, table, link, or structured data.
2. Configured football data provider or API result.
3. Public web search or browser verification.
4. User clarification for missing data.

## Data Source Credentials

Data Source Credentials are optional credentials for football data providers: odds, fixtures, lineups, injuries, team stats, or weather. They are not large-model API keys.

Never write credentials into reports, examples, references, or scripts. Refer to environment variables or local configuration names only.

## Provider Configuration

This skill does not bind to a specific vendor and does not include a built-in data-provider client. A "configured football data provider or API result" means the current agent environment already exposes a user-authorized data capability, such as:

- MCP or tool calls for fixtures, odds, lineups, injuries, team stats, or weather.
- A local or internal HTTP service that the agent can call.
- Local JSON, CSV, database, or exported files supplied by the user.
- Environment variables or local config names that a separate adapter uses, such as `API_FOOTBALL_KEY`, `THE_ODDS_API_KEY`, or `WEATHER_API_KEY`.

Do not assume these providers exist. If no callable provider is available, use public/user-authorized sources when tools allow it, then fall back to asking the user for the minimum missing data.

## Optional Provider Examples

Optional provider examples include API-Football for football fixtures, lineups, injuries, team stats, and odds, and The Odds API for multi-bookmaker odds aggregation. These are examples only. The user must register, obtain credentials, and configure a callable tool or adapter before the assistant can use them.

Discovering an API through web search does not make it a configured provider. Do not auto-register accounts, request keys on the user's behalf, guess keys, call unknown free APIs, or treat unauthenticated endpoints as authorized data sources.

## Public Web Verification Responsibility

When browsing, search, or webpage-reading tools are available, the assistant should actively perform public web verification itself. The user does not need to manually paste public data unless tools are unavailable, public access fails, sources conflict, or the user has a more authoritative source.

If public pages require login, bypassing restrictions, captcha solving, or unauthorized scraping, stop using that source and downgrade or ask the user for authorized data.

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
