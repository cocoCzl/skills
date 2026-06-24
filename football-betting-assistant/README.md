# 足球竞彩助手

`football-betting-assistant` 是一个面向中文足球竞彩分析的 agent skill。它用于胜平负、让球胜平负、比分、大小球、总进球、串关、四串一和赛后复盘等场景。

## 使用方式

把 `football-betting-assistant/` 放到 Codex 或其他 agent 的 skills 目录中。用户提出足球投注分析、竞彩、胜平负、让球胜平负、比分推荐、大小球、总进球、串关、四串一或赛后复盘相关请求时，这个 skill 应自动触发。

Skill 运行时主要读取：

- `SKILL.md`：触发规则、边界和默认流程。
- `references/`：数据源、模型、输出模板、降级规则和术语。
- `scripts/`：xG prior、泊松、隐含概率、评级、回测和输入校验。

`examples/` 只是开发和测试用的最小 JSON 样例，不是用户使用 skill 的前置条件，也不是报告结果模板。真实输出格式以 `references/report-templates.md` 为准。

## 能做什么

- 根据自然语言请求确认比赛和玩法。
- 在工具可用时核验赛程、赔率、盘口、球队近况、伤停、首发、天气和赛事背景。
- 使用透明模型：预期进球、贝叶斯修正、泊松比分概率和赔率隐含概率对比。
- 输出单场分析、组合分析、比分覆盖、参考购买方案和赛后复盘。

## 赔率获取途径

这个 skill 不内置实时赔率库，也不会声称自己天然拥有当前盘口。赔率和盘口按下面优先级获取：

1. 用户提供的赔率、截图、表格、链接或结构化数据。
2. 运行环境中已配置的数据服务/API，例如 `THE_ODDS_API_KEY` 对应的 The Odds API 适配能力。
3. 公开网页、搜索或浏览器能核验到的公开/授权数据。
4. 无法确认时，向用户追问最少必要信息。

做赔率价值判断时，优先使用多来源核验。只有单一赔率来源时可以继续分析，但必须降低赔率置信度和参考等级。赔率、盘口、首发、伤停、天气等当前数据都应记录来源和观察时间。

明确不会做的事：

- 不登录投注平台账号。
- 不绕过验证码、地区限制、频率限制或付费访问限制。
- 不硬编码投注平台账号、数据源密钥或大模型 API key。
- 没有核验来源时，不声称拥有实时赔率。

更详细的数据源规则见 `references/data-sources.md`。

## 数据服务/API 怎么配置

这个 skill 不自带 API key。可以在 agent 运行环境中配置数据能力，例如 MCP 工具、命令行工具、内部 HTTP 服务、本地 JSON/CSV 文件，或用户授权的第三方足球数据 API。

可选数据源方向：

- `The Odds API`：赔率聚合服务，适合查 `h2h`、`spreads`、`totals` 等市场。优先用于赔率和盘口。
- `API-Football`：足球数据服务，适合补赛程、球队、阵容、伤停、技术统计和部分赔率。

临时环境变量示例：

```bash
export THE_ODDS_API_KEY="your_the_odds_api_key"
export API_FOOTBALL_KEY="your_api_football_key"
```

`.env` 示例：

```bash
THE_ODDS_API_KEY=your_the_odds_api_key
API_FOOTBALL_KEY=your_api_football_key
WEATHER_API_KEY=your_weather_api_key
```

不要把真实 key 写进 `README.md`、`SKILL.md`、`references/`、`examples/` 或报告正文。

## 未配置 API 时的默认行为

未配置足球数据服务时，默认进入公开网页优先模式：

1. 如果 agent 有搜索、浏览器或网页读取工具，先主动核验公开/授权网页上的赛程、赔率、盘口、首发、伤停、天气和球队数据。
2. 如果公开网页可访问，报告写明来源和观察时间；如果只有一个赔率来源，则降低赔率置信度。
3. 如果公开网页不可访问、需要登录、被验证码拦截、来源冲突或 agent 没有联网能力，再要求用户提供最少必要数据。
4. 如果仍没有赔率，只做概率分析，不做赔率价值判断或“值得买”的判断。

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

## 数学计算引擎

内置脚本只做确定性计算，不抓取外部数据：

- `scripts/xg_prior_calculator.py`：计算基础 xG prior，并校验贝叶斯修正范围。
- `scripts/poisson_calculator.py`：计算胜平负概率、大小球概率和比分矩阵。
- `scripts/implied_probability.py`：把十进制赔率转成隐含概率和去水概率。
- `scripts/grade_calculator.py`：根据 edge、数据置信度、赔率置信度和风险标记输出参考等级。
- `scripts/match_model_calculator.py`：读取单场 JSON，串联 xG、泊松、赔率去水和评级封顶。
- `scripts/validate_inputs.py`：校验结构化输入。
- `scripts/backtest_predictions.py`：计算历史样本命中率、Brier、log loss 和概率分桶。

手动计算示例：

```bash
python3 football-betting-assistant/scripts/xg_prior_calculator.py --home-xg-for 1.85 --home-xg-against 0.85 --away-xg-for 0.90 --away-xg-against 1.65 --venue-type neutral
python3 football-betting-assistant/scripts/grade_calculator.py --model-probability 0.55 --market-probability 0.52 --single-source-odds
python3 football-betting-assistant/scripts/match_model_calculator.py football-betting-assistant/examples/single-match-model-input.json
```

如果脚本不可用，agent 可以给区间或近似值，但必须标注为近似，不能伪装成精确计算。

## 数据不足时如何处理

当没有赔率时，skill 只能做概率分析，不能做赔率价值判断；当赛程、主客/中立场、首发、伤停或盘口存在关键缺口时，应降低数据置信度、参考等级，必要时给出 Pass。

当没有联网、浏览器、API 或本地数据时，skill 应说明缺少哪些当前数据，要求用户补充最少信息，并避免从模型记忆中编造当前赛程、赔率、伤停或天气。

## 示例提问

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

四串一或串关报告默认用“经理人详版”：先给总方案，再给北京时间比赛清单、比赛大纲、小组/赛制背景、数据来源、玩法可买性、逐场分析、比分覆盖和组合候选。组合金额必须按注数计算，例如 `2 x 2 x 2 x 2 = 16 注`，默认 `16 注 x 2 元/注 = 32 元`；不要固定套用 `2/16/32/48 元` 档位。

组合候选通常按玩法拆开写，包括 `让球/胜平负方向单`、`大小球/总进球单`、比分覆盖和 `混合过关单`。不可买的普通胜平负只能作为概率分析，不能写进购买方案。

如果用户要求生成 Markdown、HTML 或保存报告，输出到 `reports/football-betting/YYYY-MM-DD-[slug].md` 和 `reports/football-betting/YYYY-MM-DD-[slug].html`。`reports/` 是运行结果目录，不应提交。

## 回测和校准

如果目标是提高命中率，优先做历史回测，而不是把单场话术写得更确定。回测样本必须只包含赛前已经能看到的数据：赛程、赔率/盘口、球队上下文、模型概率、比分候选、参考等级、观察时间，以及赛后实际比分。

开发样例见 `examples/backtest-sample.json`：

```bash
python3 football-betting-assistant/scripts/validate_inputs.py football-betting-assistant/examples/backtest-sample.json
python3 football-betting-assistant/scripts/backtest_predictions.py football-betting-assistant/examples/backtest-sample.json
```

回测会输出胜平负命中率、大小球命中率、比分 Top 1/Top 3/覆盖命中率、Brier、log loss、概率分桶和 `A/B/C/Pass` 等级表现。这些指标用于校准模型，不是未来保证。

## 开发检查

运行脚本单测：

```bash
python3 football-betting-assistant/tests/test_scripts.py
```

校验最小开发样例：

```bash
python3 football-betting-assistant/scripts/validate_inputs.py football-betting-assistant/examples/single-match-input.json
python3 football-betting-assistant/scripts/validate_inputs.py football-betting-assistant/examples/portfolio-input.json
python3 football-betting-assistant/scripts/validate_inputs.py football-betting-assistant/examples/backtest-sample.json
```

运行验收检查：

```bash
python3 football-betting-assistant/scripts/run_acceptance_checks.py
```
