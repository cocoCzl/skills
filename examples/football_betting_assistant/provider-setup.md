# Provider Setup Examples

`football-betting-assistant` 可以在没有第三方 key 的情况下用 Sporttery 公开快照做中国竞彩赛程和赔率/盘口核验；但球队近期状态、赛程密度、伤停、积分榜、赛果等上下文需要额外数据源、公开网页或用户提供数据。

## Environment Variables

在启动 Codex/agent 的 shell 中配置：

```bash
export THE_ODDS_API_KEY="your_the_odds_api_key"
export API_FOOTBALL_KEY="your_api_football_key"
export FOOTBALL_DATA_API_KEY="your_football_data_key"
```

重新启动 agent 会话，或确认运行环境能读取这些环境变量。

## Provider Roles

| Provider | 适合获取 | 不能做什么 |
| --- | --- | --- |
| Sporttery | 中国竞彩赛程、可买玩法、部分赔率/盘口 | 不是官方稳定 API；不能提供完整球队上下文 |
| API-Football | 近期战绩、赛程、积分榜、阵容、伤停、技术统计 | 不能替代中国竞彩可买赔率 |
| football-data.org | 部分赛事赛程、赛果、积分榜 | 覆盖有限；通常不提供伤停/首发 |
| The Odds API | 国际 h2h/spreads/totals 赔率和部分赛果 | 不能替代中国竞彩赔率 |

## Key Sources

- The Odds API: https://the-odds-api.com/
- API-Football: https://www.api-football.com/
- football-data.org: https://www.football-data.org/

这些服务的套餐、覆盖范围、限频和字段会变化，以各自 dashboard 和官方文档为准。

## Expected Behavior

配置 provider 后，用户仍然只需要自然语言提问，例如：

```text
帮我分析北京时间明天早上四场世界杯比赛，给我一个四串一参考购买方案，重点看比分和大小球。
```

agent 应该：

- 用 Sporttery 或用户提供数据确认中国竞彩可买玩法和赔率/盘口。
- 用可用 provider 或公开网页补近期状态、赛程密度、伤停、积分榜/战意、天气/场地等上下文。
- 把每类数据的来源和观察时间写进报告。
- 如果 provider 不可用、限频、无覆盖或来源冲突，标明数据缺口并降级。

## Current Implementation Note

当前 skill 已有 Sporttery 快照采集、结构化校验、xG/泊松/赔率/评级脚本，以及赛后复盘 provider 逻辑。赛前 API-Football / football-data.org 的完整 team-context 自动采集器仍应作为后续功能单独实现；在此之前，agent 可用公开网页或用户提供数据补上下文，并必须标注置信度。
