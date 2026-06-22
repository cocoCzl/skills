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
