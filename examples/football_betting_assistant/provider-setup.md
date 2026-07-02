# Provider Setup Examples

`football-betting-assistant` 可以在没有第三方 key 的情况下用 Sporttery 公开快照做中国竞彩赛程和赔率/盘口核验；但球队近期状态、赛程密度、伤停、积分榜、赛果等上下文需要额外数据源、公开网页或用户提供数据。

## No-Key Mode

没有任何 API key 时也可以使用这个 skill：

- 中国竞彩请求默认先尝试 `sporttery` 公开快照，确认赛程、可买玩法、赔率和盘口。
- 如果运行环境支持联网或浏览器，agent 可以继续用公开网页核验球队近况、伤停、天气、赛程密度和赛事背景。
- 如果运行环境不能联网，用户需要自己提供截图、赔率文本、盘口、伤停、近期状态或赛程背景。
- 如果赔率/盘口没有被 Sporttery、公开网页、用户输入或授权 provider 核验，报告只能做概率分析，不能输出完整赔率价值判断或正式参考购买方案。

Sporttery 是 best-effort 公开采集来源，不是中国体育彩票官方稳定 API。页面结构变化、访问限制、限频、地区网络问题或字段缺失都会导致采集失败或报告降级。

## Environment Variables

在启动 Codex/agent 的 shell 中配置：

```bash
export THE_ODDS_API_KEY="your_the_odds_api_key"
export API_FOOTBALL_KEY="your_api_football_key"
export FOOTBALL_DATA_API_KEY="your_football_data_key"
```

重新启动 agent 会话，或确认运行环境能读取这些环境变量。

在字节、阿里或其他类似 Codex App 的软件里，如果不能直接 `export` 环境变量，就在该软件提供的“环境变量”“密钥管理”“项目配置”或“工具运行配置”里填同名变量。不要把真实 key 粘到系统提示词、README、知识库正文或聊天记录里。

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

第三方 provider 不能替代中国竞彩可买赔率。`THE_ODDS_API_KEY` 返回的国际 h2h、spreads、totals 赔率只能用于 `international-odds` 模式，或在竞彩报告中作为国际市场参考背景；不能写成中国竞彩购买方案。

## Third-Party Agent Notes

如果使用的不是 Codex，而是其他大模型软件：

- 原生支持 skills 时，安装整个 `football-betting-assistant/` 目录。
- 只支持自定义规则时，把 `football-betting-assistant/SKILL.md` 加入项目规则。
- 支持知识库或项目文件时，同时加入 `references/` 和本目录的示例文档。
- 支持本地命令时，允许 agent 在项目根目录调用 `football-betting-assistant/scripts/` 里的脚本。
- 不支持本地命令时，模型只能读规则并手动分析，无法自动生成标准快照、prediction snapshot 或 HTML 报告。

## Current Implementation Note

当前 skill 已有 Sporttery 快照采集、结构化校验、xG/泊松/赔率/评级脚本，以及赛后复盘 provider 逻辑。赛前 API-Football / football-data.org 的完整 team-context 自动采集器仍应作为后续功能单独实现；在此之前，agent 可用公开网页或用户提供数据补上下文，并必须标注置信度。
