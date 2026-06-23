# Report Templates

Default report language is Chinese Betting Vocabulary. Keep math visible but concise. Prefer a rich analysis report over a thin table-only response when data and tools are available.

## Single-Match Report

```markdown
## [主队] vs [客队]：赛前分析

### 1. 数据来源与比赛确认
| 项目 | 当前信息 | 来源/时间 | 置信度 |
|---|---|---|---|
| 比赛 | [赛事、轮次、开赛时间、主客/中立] | [来源] | 高/中/低 |
| 赔率/盘口 | [胜平负、让球、大小球/总进球] | [来源] | 高/中/低 |
| 近期状态 | [近5/近10场摘要] | [来源] | 高/中/低 |
| 攻防数据 | [xG/xGA 或进失球] | [来源] | 高/中/低 |
| 伤停/首发 | [已确认/预计/未确认] | [来源] | 高/中/低 |
| 天气/场地 | [天气、场地、旅途] | [来源] | 高/中/低 |
| 战意/赛制 | [出线、净胜球、排名路线、轮换、潜在淘汰赛对手] | [来源] | 高/中/低 |
| 数据缺口 | [缺失或冲突项] | [来源] | 高/中/低 |

> 数据来源说明：[用中文说明引用了哪些来源，例如官方赛程、赔率聚合源/单一公司、球队新闻、数据站、天气源、用户提供截图；可以不贴 URL，但必须写来源名和观察时间。]

### 2. 基础面分析
- 近期状态：
- 攻防结构：
- 伤停/首发：
- 天气/场地/赛程：
- 战意/赛制：[小组赛第 3 轮需说明出线形势、净胜球、排名路线、轮换概率、潜在淘汰赛对手；"避强队/选路线"只能作为动机修正，不能当作确定行为]

### 3. 赔率/盘口表
| 市场 | 盘口 | 赔率/范围 | 来源 | 观察时间 | 置信度 |
|---|---|---|---|---|---|
| 胜平负 | - | 主胜/平/客胜 | [bookmaker/aggregator] | [time] | 高/中/低 |
| 让球 | [line] | 主/客或让胜/让平/让负 | [bookmaker/aggregator] | [time] | 高/中/低 |
| 大小球 | [line] | 大/小 | [bookmaker/aggregator] | [time] | 高/中/低 |

### 4. 数学模型
- 基础 xG prior：
- 贝叶斯修正：
- 最终 xG：
- 泊松比分集中：
- 赔率隐含概率/去水概率：
- 模型记录：[脚本计算 / 手算近似 / 数据不足无法计算]

### 5. 结论摘要
- 胜平负倾向：
- 让球胜平负倾向：
- 大小球/总进球倾向：
- 参考等级：A/B/C/Pass
- 模型置信度：高/中/低
- 数据置信度：高/中/低

### 6. 概率判断
| 市场 | 概率/区间 | 说明 |
|---|---:|---|
| 主胜 |  |  |
| 平局 |  |  |
| 客胜 |  |  |
| 大球 |  | 盘口： |
| 小球 |  | 盘口： |

### 7. 比分排序
| 排名 | 比分 | 概率层级 | 使用场景 |
|---:|---|---|---|
| 1 |  | 最高/高/中 | 主推/覆盖/风险 |
| 2 |  | 高/中 |  |
| 3 |  | 中/冷门 |  |

### 8. 参考购买方案
- 胜平负/让球：
- 大小球/总进球：
- 比分覆盖：
- 不建议项：

### 9. 风险点
- 
```

## Portfolio Report

```markdown
## 四串一参考方案

### 1. 今天四场先看结论
| 比赛 | 胜平负倾向 | 大小球/总进球 | 比分主区间 | 稳度 | 最大风险 |
|---|---|---|---|---|---|

稳度排序：[从高到低列出]
主线方向：[用一句话说明四串一方向]
比分思路：[说明是偏小比分、强弱分明、还是有一两场可能打穿]

### 2. 比赛大纲 / 今日赛程确认
| 编号 | 比赛 | 时间 | 赛事 | 主客/中立 | 数据置信度 | 赔率/盘口来源 |
|---|---|---|---|---|---|---|

### 3. 数据来源总览
| 类别 | 使用来源 | 观察时间 | 说明 |
|---|---|---|---|
| 赛程 |  |  |  |
| 赔率/盘口 |  |  |  |
| 球队状态/伤停 |  |  |  |
| 天气/场地 |  |  |  |

### 4. 逐场分析

#### [编号]. [主队] vs [客队]
- 数据依据：[来源名 + 时间；不需要默认贴链接]
- 基础面：[用 1-2 段自然语言说明状态、攻防、伤停、场地、战意]
- 比赛剧本：[谁会控球、谁会收缩、早进球/久攻不下/红牌或换人会怎样影响比分]
- 数学模型：[prior xG -> 贝叶斯修正 -> final xG；泊松比分集中]
- 胜平负概率：[主胜/平/客胜区间 + 首选]
- 大小球/总进球：[盘口或总进球倾向 + 为什么]
- 比分分布：[按顺序列 3-5 个候选；区分主推、覆盖、补防]
- 等级/风险：[A/B/C/Pass + 关键风险]

### 5. 胜平负与大小球汇总
| 比赛 | 胜平负 | 让球 | 大小球 | 来源/时间 | 置信度 |
|---|---|---|---|---|---|

### 6. 比分覆盖建议
| 比赛 | 核心比分 | 增强覆盖 | 漏洞/补防 | 不建议 |
|---|---|---|---|---|

### 7. 四串一参考购买方案
| 类型 | 注数组合 | 合计 | 每场选择 | 适用场景 | 风险 |
|---|---:|---:|---|---|---|
| 稳健方向单 | [例如 1 x 1 x 1 x 1 = 1 注] | [N x 2 元/unit] | [胜平负/让球/大小球组合] | [不想强压比分] |  |
| 基础比分覆盖 | [例如 2 x 2 x 2 x 2 = 16 注] | [N x 2 元/unit] | [每场比分] | [核心比分区间] |  |
| 增强比分覆盖 | [按实际选择数量计算] | [N x 2 元/unit] | [给高波动场次加比分] | [提高容错] |  |
| 补洞单 | [按实际选择数量计算] | [N x 2 元/unit] | [覆盖最大漏防路径] | [已买主单或想补关键漏洞] |  |
| 搏冷/高赔率小单 | [按实际选择数量计算] | [N x 2 元/unit] | [低概率但可解释剧本] | [只作可选参考] | 高方差 |

### 8. 如果用户已有购买方案
- 这组合理的地方：
- 最大漏防：
- 最该补的比分/方向：
- 已买后可考虑的补洞单：

### 9. 组合相关性检查
- 独立性/相关性：
- 共同风险：
- 不建议强行纳入的场次：

### 10. 更多组合候选
| 组合 | 注数/金额 | 每场选择 | 使用条件 | 风险 |
|---|---:|---|---|---|

### 11. Pass / 排除项
- 
```

Portfolio rules:

- Support up to four matches.
- Do not hard-code 2/16/32/48 元 plans. Pick the coverage widths from the score probabilities and user intent, then calculate units and amount.
- Keep amount and unit count explicit. With the default 2 元/unit, 16 units equals 32 元, not 16 元.
- More Combination Candidates are optional alternatives, not extra mandatory purchases.
- Score Coverage may include up to four scores per match only when the football case supports wider coverage.
- When the user provides a proposed ticket, evaluate their ticket first before suggesting replacement plans.
- Exclude matches that are Pass or have severe data gaps.

## Post-Match Review

```markdown
## 赛后复盘：[比赛或组合]

### 1. 赛前判断回顾

### 2. 实际结果与关键转折

### 3. 模型偏差

### 4. 数据偏差

### 5. 下次调整
```

Do not include chase-loss, recovery-bet, bankroll allocation, Kelly sizing, or personalized stake-size advice. Ticket-tier amounts are allowed only as unit-count totals requested by the user.
