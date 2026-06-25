# 足球竞彩助手

`football-betting-assistant` 是一个面向中文足球竞彩分析的 agent skill。它用于胜平负、让球胜平负、比分、大小球、总进球、串关、四串一和赛后复盘等场景。

## 使用方式

把 `football-betting-assistant/` 放到 Codex 或其他 agent 的 skills 目录中。用户提出足球投注分析、竞彩、胜平负、让球胜平负、比分推荐、大小球、总进球、串关、四串一或赛后复盘相关请求时，这个 skill 应自动触发。

Skill 运行时主要读取：

- `SKILL.md`：触发规则、边界和默认流程。
- `references/`：数据源、模型、输出模板、降级规则和术语。
- `scripts/`：xG prior、泊松、隐含概率、评级、回测和输入校验。

仓库级 `examples/football_betting_assistant/` 和 `tests/fixtures/football_betting_assistant/` 只是开发样例和测试 fixture，不是用户使用 skill 的前置条件，也不是报告结果模板。真实输出格式以 `references/report-templates.md` 为准。

## 能做什么

- 根据自然语言请求确认比赛和玩法。
- 在工具可用时核验赛程、赔率、盘口、球队近况、伤停、首发、天气和赛事背景。
- 在中国竞彩模式下，默认尝试用内置 `sporttery` provider 采集当前/未来公开竞彩足球快照。
- 使用透明模型：预期进球、贝叶斯修正、泊松比分概率和赔率隐含概率对比。
- 输出单场分析、组合分析、比分覆盖、参考购买方案和赛后复盘。

默认范围是成年男足俱乐部和成年男足国家队比赛。青年队、年龄组比赛和女足比赛不生成正式参考购买方案；如果被数据源采到，会标记为 `unsupported` 并按 analysis-only 或 Pass 处理。

## 赔率获取途径

这个 skill 不会声称自己天然拥有当前盘口。赔率和盘口按下面优先级获取：

1. 本地标准足球快照，例如 `data/football/snapshots/` 下的 JSON。
2. 中国竞彩模式默认使用内置 `sporttery` provider，采集公开可见的竞彩足球赛程、可买玩法、盘口和赔率。
3. 用户提供的赔率、截图、表格、链接或结构化数据。
4. 运行环境中已配置的数据服务/API，例如 `THE_ODDS_API_KEY` 对应的 The Odds API 适配能力。
5. 公开网页、搜索或浏览器能核验到的公开/授权数据。
6. 无法确认时，向用户追问最少必要信息。

做赔率价值判断时，优先使用多来源核验。只有单一赔率来源时可以继续分析，但必须降低赔率置信度和参考等级。赔率、盘口、首发、伤停、天气等当前数据都应记录来源和观察时间。

明确不会做的事：

- 不登录投注平台账号。
- 不绕过验证码、地区限制、频率限制或付费访问限制。
- 不硬编码投注平台账号、数据源密钥或大模型 API key。
- 没有核验来源时，不声称拥有实时赔率。

更详细的数据源规则见 `references/data-sources.md`。

## 默认零操作用法

普通用户不需要先手动运行脚本。直接问：

```text
帮我看下北京时间明天的几场世界杯比赛，重点看胜平负、让球、总进球和比分。
```

在 `china-lottery` 模式下，assistant 应自动：

1. 检查本地 `data/football/snapshots/` 是否已有可用快照。
2. 必要时运行内置 `sporttery` 快照采集。
3. 从快照匹配今天/明天或用户指定的比赛。
4. 检查快照中确认可买的竞彩玩法，只使用可买玩法生成购买方案。
5. 生成自包含 HTML 报告，并保存对应的预测快照，方便以后赛后复盘和模型校准。
6. 赔率/盘口缺失时停止完整价值判断，只问用户补充最少字段。

`sporttery` provider 是公开页面/公开接口的 best-effort 采集器，不是中国体育彩票官方稳定 API。它不会登录、不会绕过验证码/WAF、不会突破访问限制。页面变化或访问被拦截时，报告必须降级或追问，而不能编造赔率。

## 数据服务/API 怎么配置

这个 skill 不自带 API key。可以在 agent 运行环境中配置数据能力，例如 MCP 工具、命令行工具、内部 HTTP 服务、本地 JSON/CSV 文件，或用户授权的第三方足球数据 API。

可选数据源方向：

- `sporttery`：内置默认 provider，适合中国竞彩公开赛程、可买玩法、盘口和赔率。它是 best-effort 公开数据采集，不保证所有日期和玩法都有数据。
- `The Odds API`：赔率聚合服务，适合查 `h2h`、`spreads`、`totals` 等市场。优先用于赔率和盘口。
- `API-Football`：足球数据服务，适合补赛程、球队、阵容、伤停、技术统计和部分赔率。
- `football-data.org`：适合补部分赛事的赛程、赛果、积分榜和基础比赛数据。
- `TheSportsDB` / `OpenLigaDB`：可作为低门槛公开 fallback，覆盖面和深度有限，不能当成完整赔率或阵容源。

### Provider 职责边界

| 配置 / Provider | 主要用途 | 是否可替代中国竞彩赔率 |
| --- | --- | --- |
| `sporttery` | `china-lottery` 模式下默认尝试获取中国竞彩公开赛程、可买玩法、盘口和赔率。 | 是默认竞彩公开数据来源，但不是官方稳定 API。 |
| `THE_ODDS_API_KEY` | 主要用于 `international-odds` 模式；在竞彩报告里只能作为国际市场参考。 | 不能替代中国竞彩可买赔率。 |
| `API_FOOTBALL_KEY` | 补球队近期战绩、阵容、伤停、积分榜、技术统计和部分赛程/赔率背景。 | 不能替代中国竞彩可买赔率，也不是默认竞彩赔率源。 |
| `FOOTBALL_DATA_API_KEY` | 补部分赛事的赛程、赛果和积分榜。 | 不能替代中国竞彩可买赔率。 |

配置第三方 API key 不会自动把中文竞彩请求切换成 `international-odds`。只要用户目标是“竞彩 / 中国体育彩票 / 四串一参考购买方案”，默认仍走 `china-lottery`，购买方案只能使用已确认的中国竞彩可买市场；第三方赔率最多作为国际市场参考或球队背景补充。

### 如何获取 API Key

下面这些第三方服务都需要用户自己注册并遵守对应服务条款。README 里只写获取入口和配置方式，不应写入真实 key。

- `API_FOOTBALL_KEY`：访问 <https://www.api-football.com/pricing> 或 <https://dashboard.api-football.com/>，注册账号后选择 Free/Pro/Ultra/Mega 等计划。API-Football 官方 pricing 页面说明 Free 计划可用且包含 fixtures、standings、lineups、injuries、pre-match odds 等端点，但有每日请求量限制；注册/订阅后在 dashboard 中查看或创建项目 API key。
- `FOOTBALL_DATA_API_KEY`：访问 <https://www.football-data.org/client/register> 注册账号。football-data.org 注册页说明注册成功后会获得 API Key；免费层包含部分赛事的 fixtures、results 和 league tables，并有调用频率限制。已有账号可从 <https://www.football-data.org/client/login> 登录，忘记 token 可在登录页使用 resend token。
- `THE_ODDS_API_KEY`：访问 <https://the-odds-api.com/> 或文档页 <https://the-odds-api.com/liveapi/guides/v4/>，选择 plans/get API key。The Odds API 文档说明入门流程是先通过邮箱获取 API key，然后用 `/v4/sports?apiKey=YOUR_API_KEY` 检查可用运动，再用 sport key 查询 odds。

拿到 key 后，只在本机 shell、部署平台 Secret、`.env`、1Password/Keychain 等安全位置配置。不要把真实 key 提交到 git，也不要贴进报告、issue、PR、README 或聊天记录。

临时环境变量示例：

```bash
export THE_ODDS_API_KEY="your_the_odds_api_key"
export API_FOOTBALL_KEY="your_api_football_key"
export FOOTBALL_DATA_API_KEY="your_football_data_key"
```

`.env` 示例：

```bash
THE_ODDS_API_KEY=your_the_odds_api_key
API_FOOTBALL_KEY=your_api_football_key
FOOTBALL_DATA_API_KEY=your_football_data_key
WEATHER_API_KEY=your_weather_api_key
```

不要把真实 key 写进 `README.md`、`SKILL.md`、`references/`、仓库级 `examples/` 或报告正文。

真实使用例子：

```bash
# API-Football：用于球队近期战绩、积分榜、伤停、阵容等增强信息
export API_FOOTBALL_KEY="xxxxxxxxxxxxxxxxxxxxxxxx"

# football-data.org：用于部分赛事的赛程、赛果和积分榜
export FOOTBALL_DATA_API_KEY="xxxxxxxxxxxxxxxxxxxxxxxx"

# The Odds API：用于 international-odds 模式或国际市场参考，不替代中国竞彩可买赔率
export THE_ODDS_API_KEY="xxxxxxxxxxxxxxxxxxxxxxxx"
```

没有这些 key 时，skill 仍可尝试用 `sporttery` 快照和公开网页做中国竞彩分析；球队近期数据、阵容和积分榜可能降级。

## 开发者调试快照

普通用户不需要运行命令。开发者可以手动生成快照排查采集问题：

```bash
python3 football-betting-assistant/scripts/fetch_match_data.py \
  --mode china-lottery \
  --provider sporttery \
  --football \
  --out data/football/snapshots
```

使用本地 raw fixture 做离线调试：

```bash
python3 football-betting-assistant/scripts/fetch_match_data.py \
  --mode china-lottery \
  --provider sporttery \
  --football \
  --raw-input tests/fixtures/football_betting_assistant/raw/sporttery-football-sample.json \
  --out data/football/snapshots
```

检查某个快照里每场比赛哪些玩法可买、哪些玩法缺赔率：

```bash
python3 football-betting-assistant/scripts/inspect_snapshot_markets.py \
  data/football/snapshots/sporttery-football-YYYYMMDDTHHMMSS+0800.json
```

按竞彩编号检查：

```bash
python3 football-betting-assistant/scripts/inspect_snapshot_markets.py \
  data/football/snapshots/sporttery-football-YYYYMMDDTHHMMSS+0800.json \
  --match-no 周四055
```

从标准快照生成 HTML 报告和预测快照：

```bash
python3 football-betting-assistant/scripts/build_snapshot_report.py \
  data/football/snapshots/sporttery-football-YYYYMMDDTHHMMSS+0800.json \
  --date tomorrow \
  --competition 世界杯 \
  --topic "明天世界杯竞彩分析" \
  --report-out-dir reports/football-betting \
  --data-out-dir data/football
```

输出包括：

- `reports/football-betting/*.html`：用户可直接打开的自包含 HTML 报告。
- `data/football/report-inputs/*.html-report.json`：HTML renderer 的结构化输入。
- `data/football/predictions/*.prediction.json`：带相同 `report_id` 的预测快照。

这些命令是开发者调试入口。正常使用 skill 时，agent 应自动完成快照采集、比赛选择、报告生成和预测快照保存，不要求用户手动运行命令。

离线 smoke 测试自然语言零操作路径：

```bash
python3 football-betting-assistant/scripts/zero_operation_smoke.py \
  tests/fixtures/football_betting_assistant/football-snapshot-sporttery.json \
  --request "帮我看下北京时间明天的几场世界杯比赛" \
  --report-out-dir reports/football-betting \
  --data-out-dir data/football
```

这个 smoke 测试使用 fixture 快照验证：自然语言请求、快照筛选、竞彩可买市场闸门、HTML 报告、prediction snapshot 和短聊天摘要。

快照、HTML 报告、报告输入和预测快照是生成物，默认不应提交。开发样例放在仓库级 `examples/football_betting_assistant/`；测试 fixture 放在 `tests/fixtures/football_betting_assistant/`；测试入口放在 `tests/football_betting_assistant/`。这些都不放进运行时 skill 目录。

## 未配置 API 时的默认行为

未配置第三方足球数据服务时，默认进入中国竞彩/公开网页优先模式：

1. 中国竞彩请求先尝试读取本地快照。
2. 无可用快照时，agent 自动尝试运行 `sporttery` provider。
3. 如果 agent 有搜索、浏览器或网页读取工具，再主动核验公开/授权网页上的赛程、赔率、盘口、首发、伤停、天气和球队数据。
4. 如果公开网页可访问，报告写明来源和观察时间；如果只有一个赔率来源，则降低赔率置信度。
5. 如果公开网页不可访问、需要登录、被验证码拦截、来源冲突或 agent 没有联网能力，再要求用户提供最少必要数据。
6. 如果仍没有赔率，只做概率分析，不做赔率价值判断或“值得买”的判断。

公开搜索可从这些关键词开始：

```text
[主队] [客队] odds
[主队] vs [客队] handicap
[赛事名] odds [比赛日期]
[主队] [客队] 赔率
[主队] [客队] 盘口
[主队] [客队] 让球 大小球
```

预测文章只能作为背景，不能当成真实即时赔率。

## 内置脚本

内置脚本分为数据采集、报告生成和确定性模型计算：

- `scripts/fetch_match_data.py`：采集当前/未来足球快照；中国竞彩模式默认使用内置 `sporttery` provider。
- `scripts/select_snapshot_matches.py`：按日期、竞彩编号、球队或赛事从快照中选择比赛。
- `scripts/inspect_snapshot_markets.py`：检查快照中哪些竞彩玩法可买、哪些缺失或不可用。
- `scripts/team_context_rules.py`：识别 `club`、`national`、`unknown`、`unsupported` 队伍类型，并给出参数池和置信度上限。
- `scripts/recent_form_to_xg.py`：把近期 xG/xGA 或进失球汇总转换成 xG prior 输入；只有进失球时自动降精度。
- `scripts/build_snapshot_report.py`：从标准足球快照生成 HTML 报告和同 `report_id` 的预测快照。
- `scripts/render_html_report.py`：从结构化报告 JSON 渲染自包含 HTML。
- `scripts/xg_prior_calculator.py`：计算基础 xG prior，并校验贝叶斯修正范围。
- `scripts/poisson_calculator.py`：计算胜平负概率、大小球概率和比分矩阵。
- `scripts/implied_probability.py`：把十进制赔率转成隐含概率和去水概率。
- `scripts/grade_calculator.py`：根据 edge、数据置信度、赔率置信度和风险标记输出参考等级。
- `scripts/market_grade_calculator.py`：按玩法分别计算隐含概率、去水概率、edge 和参考等级。
- `scripts/score_coverage_analyzer.py`：分析比分集中度、核心覆盖、增强覆盖和比分票是否适合进入主方案。
- `scripts/portfolio_builder.py`：根据可买市场、等级、数据置信度和比分集中度生成保守组合候选，不强行凑满 4 串或 8 串。
- `scripts/late_update_rules.py`：评估早盘等级上限、临场首发要求、赔率/盘口变化、停售和开赛后 stop rules。
- `scripts/post_match_review.py`：把赛后比分附加到 prediction snapshot，计算胜平负、让球、总进球和比分候选的基础复盘字段。
- `scripts/zero_operation_smoke.py`：离线验证“自然语言请求 -> 快照选择 -> HTML 报告 -> prediction snapshot”的零操作路径。
- `scripts/match_model_calculator.py`：读取单场 JSON，串联 xG、泊松、赔率去水和评级封顶。
- `scripts/validate_inputs.py`：校验结构化输入。
- `scripts/backtest_predictions.py`：计算历史样本命中率、Brier、log loss 和概率分桶。

手动计算示例：

```bash
python3 football-betting-assistant/scripts/xg_prior_calculator.py --home-xg-for 1.85 --home-xg-against 0.85 --away-xg-for 0.90 --away-xg-against 1.65 --venue-type neutral
python3 football-betting-assistant/scripts/grade_calculator.py --model-probability 0.55 --market-probability 0.52 --single-source-odds
python3 football-betting-assistant/scripts/match_model_calculator.py examples/football_betting_assistant/single-match-model-input.json
```

如果脚本不可用，agent 可以给区间或近似值，但必须标注为近似，不能伪装成精确计算。

## 数据不足时如何处理

当没有赔率时，skill 只能做概率分析，不能做赔率价值判断；当赛程、主客/中立场、首发、伤停或盘口存在关键缺口时，应降低数据置信度、参考等级，必要时给出 Pass。

### 严禁编造赔率和盘口

如果没有从中国竞彩、用户截图/文本、授权 API、公开网页或本地快照中核验到赔率和盘口，必须在聊天摘要和 HTML 报告顶部给出醒目提示：

```text
竞彩赔率/盘口状态：未获取或未验证
本报告只包含概率分析，不包含赔率价值判断，不提供正式参考购买方案。
```

这种情况下严禁：

- 编造胜平负、让球胜平负、比分、总进球或大小球赔率。
- 编造让球数、大小球盘口、总进球赔率或比分赔率。
- 用第三方国际赔率替代中国竞彩可买赔率。
- 把模型概率、历史均值、预测文章或盘口印象写成“当前竞彩赔率”。
- 输出“值得买”“赔率有价值”“可买方案已确认”等完整价值判断。

允许输出的内容仅限于：赛程确认、球队背景、数据缺口、概率倾向、比分候选、大小球倾向、风险点，以及需要用户补充的最少字段。若生成 HTML 报告，Data Status 应写为 `no-actual-odds-lines`，购买方案区只能写“概率参考结构 / 待赔率确认”，不能写成正式购买单。

如果用户目标是中国体育彩票竞彩购买方案，而 `sporttery` 快照、公开页面、配置 provider 和用户输入都没有提供可买玩法、赔率或盘口，skill 必须立刻停止完整价值判断，询问：

```markdown
请补充这场/这几场的竞彩可买玩法和赔率/盘口：
比赛：
玩法：胜平负 / 让球胜平负 / 比分 / 总进球 / 大小球
盘口：
赔率：
截图或文字都可以。
```

当没有联网、浏览器、API 或本地数据时，skill 应说明缺少哪些当前数据，要求用户补充最少信息，并避免从模型记忆中编造当前赛程、赔率、伤停或天气。

## 示例提问

### 运行模式怎么选择

`china-lottery` 是中文竞彩购买语境的默认模式；`international-odds` 只在用户明确要求海外/国际赔率时使用；`analysis-only` 用于没有可验证赔率、盘口或可买玩法时的纯概率分析。

`china-lottery` 示例：

```text
明天早上四场世界杯比赛，帮我做一个竞彩四串一参考购买方案，重点看比分和大小球。
```

这类请求会默认尝试读取本地快照，再运行 `sporttery` provider 获取中国竞彩公开赛程、可买玩法、盘口和赔率。购买方案只使用确认可买的竞彩市场。

`international-odds` 示例：

```text
用 The Odds API 或海外公司赔率分析今晚西班牙 vs 沙特，重点看 h2h、spreads 和 totals 的赔率价值。
```

这类请求才会把 `THE_ODDS_API_KEY` 对应的数据作为主要赔率源。输出应按国际赔率/盘口口径分析，不把结果伪装成中国竞彩可买方案。

`analysis-only` 示例：

```text
我不需要购买方案，也没有赔率。只看法国 vs 日本的比赛走势、比分概率和大小球倾向。
```

这类请求可以做概率分析和风险判断，但不做赔率价值判断，也不输出完整参考购买方案。

```text
帮我分析今晚西班牙 vs 沙特，给胜平负、让球、大小球和三个比分候选。
```

```text
明天早上四场世界杯比赛，帮我做一个四串一参考购买方案，重点看比分和大小球。
```

```text
现在不能联网。我给你赔率和球队近况，你按离线模式分析法国 vs 日本有没有价值。
```

```text
复盘一下我昨天买的四串一为什么没中，重点看模型偏差和数据偏差。
```

## 带盘口赔率的使用例子

用户可以直接贴赛程、盘口、赔率和球队信息：

```text
帮我分析西班牙 vs 沙特。

比赛时间：2026-06-23 08:00 CST
赛事：世界杯小组赛
场地：中立场

胜平负赔率：主胜 1.52，平 4.10，客胜 7.20
让球胜平负：西班牙 -1，胜 2.28，平 3.35，负 2.55
大小球：2.5 球，大 1.95，小 1.85

伤停/首发：西班牙主力前锋预计首发，沙特中卫一人伤疑；首发未确认。
近期状态：西班牙近 10 场进攻稳定；沙特面对强队时防线压力较大。

请给胜平负、让球、大小球、三个比分候选和风险点。
```

如果希望 agent 自己查公开数据：

```text
帮我查一下今晚西班牙 vs 沙特的公开赔率和盘口，再做胜平负、大小球和比分分析。只使用公开或授权来源，查不到就告诉我缺什么。
```

## 输入模板

当 agent 无法核验当前数据时，可以按下面模板补充信息：

```markdown
比赛：
开赛时间：
赛事：
主客/中立：
想看玩法：胜平负 / 让球胜平负 / 比分 / 大小球 / 四串一
赔率/盘口：
伤停/首发：
近期状态或数据：
```

## 输出内容

输出必须区分“概率分析”和“可买方案”。如果用户截图或数据源里某场没有普通胜平负，只显示让球胜平负、比分或总进球，则购买方案不得写普通胜平负。

单场报告通常包含：数据来源与比赛确认、基础面、盘口赔率、模型记录、概率判断、比分候选、参考购买方案和风险点。

多场串关报告默认用“经理人详版”：先给全场次结论，再给北京时间比赛清单、比赛大纲、小组/赛制背景、数据来源、玩法可买性、逐场分析、比分覆盖和组合候选。6、8、10 场或更多比赛也要逐场分析，不因出票限制省略比赛。组合金额必须按注数计算，例如 `2 x 2 x 2 x 2 = 16 注`，默认 `16 注 x 2 元/注 = 32 元`；不要固定套用 `2/16/32/48 元` 档位。

组合候选通常按玩法拆开写，包括 `模型最稳主单`、`让球/胜平负方向单`、`大小球/总进球单`、`比分4串1`、比分覆盖、`混合过关单`、`备选/替换` 和 `可选小组合`。不可买的普通胜平负只能作为概率分析，不能写进购买方案。精确比分串关最多 4 场；胜平负 / 让球胜平负最多 8 场；大小球 / 总进球最多 8 场。模型可以少选，不强行凑满。

完成赛前单场或多场分析时，默认生成一个自包含 HTML 报告，输出到当前工作目录下的 `reports/football-betting/YYYY-MM-DD-[slug]-[场次数]matches.html`。不再为完成的赛前分析生成 Markdown 报告。HTML 可直接用 Chrome 打开，不需要本地服务器；除非用户明确要求打开，否则只在聊天里返回 2-4 行摘要和路径。

如果未取得实际赔率/盘口，但赛程和球队上下文足够，仍生成 HTML 报告，并在报告顶部标注“无实际赔率/盘口”；购买方案降级为概率倾向和参考结构，不写完整赔率价值判断。`reports/` 是运行结果目录，不应提交。

## 回测和校准

如果目标是提高命中率，优先做历史回测，而不是把单场话术写得更确定。回测样本必须只包含赛前已经能看到的数据：赛程、赔率/盘口、球队上下文、模型概率、比分候选、参考等级、观察时间，以及赛后实际比分。

开发样例见 `examples/football_betting_assistant/backtest-sample.json`：

```bash
python3 football-betting-assistant/scripts/validate_inputs.py examples/football_betting_assistant/backtest-sample.json
python3 football-betting-assistant/scripts/backtest_predictions.py examples/football_betting_assistant/backtest-sample.json
```

回测会输出胜平负命中率、大小球命中率、比分 Top 1/Top 3/覆盖命中率、Brier、log loss、概率分桶和 `A/B/C/Pass` 等级表现。这些指标用于校准模型，不是未来保证。

## 本地校验

校验最小开发样例：

```bash
python3 football-betting-assistant/scripts/validate_inputs.py examples/football_betting_assistant/single-match-input.json
python3 football-betting-assistant/scripts/validate_inputs.py examples/football_betting_assistant/portfolio-input.json
python3 football-betting-assistant/scripts/validate_inputs.py examples/football_betting_assistant/backtest-sample.json
```

渲染 HTML 报告：

```bash
python3 football-betting-assistant/scripts/render_html_report.py path/to/report-input.json --out-dir reports/football-betting
```
