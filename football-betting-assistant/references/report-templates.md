# Report Templates

Default report language is Chinese Betting Vocabulary. Keep math visible but concise.

## Single-Match Report

```markdown
## [主队] vs [客队]：赛前分析

### 1. 数据确认
| 项目 | 当前信息 | 来源/时间 | 置信度 |
|---|---|---|---|
| 比赛 | [赛事、轮次、开赛时间、主客/中立] | [来源] | 高/中/低 |
| 赔率/盘口 | [胜平负、让球、大小球/总进球] | [来源] | 高/中/低 |
| 近期状态 | [近5/近10场摘要] | [来源] | 高/中/低 |
| 攻防数据 | [xG/xGA 或进失球] | [来源] | 高/中/低 |
| 伤停/首发 | [已确认/预计/未确认] | [来源] | 高/中/低 |
| 天气/场地 | [天气、场地、旅途] | [来源] | 高/中/低 |
| 战意/赛制 | [出线、轮换、淘汰赛背景] | [来源] | 高/中/低 |
| 数据缺口 | [缺失或冲突项] | [来源] | 高/中/低 |

### 2. 赔率/盘口表
| 市场 | 盘口 | 赔率/范围 | 来源 | 观察时间 | 置信度 |
|---|---|---|---|---|---|
| 胜平负 | - | 主胜/平/客胜 | [bookmaker/aggregator] | [time] | 高/中/低 |
| 让球 | [line] | 主/客或让胜/让平/让负 | [bookmaker/aggregator] | [time] | 高/中/低 |
| 大小球 | [line] | 大/小 | [bookmaker/aggregator] | [time] | 高/中/低 |

### 3. 结论摘要
- 胜平负倾向：
- 让球胜平负倾向：
- 大小球/总进球倾向：
- 参考等级：A/B/C/Pass
- 模型置信度：高/中/低
- 数据置信度：高/中/低

### 4. 概率判断
| 市场 | 概率/区间 | 说明 |
|---|---:|---|
| 主胜 |  |  |
| 平局 |  |  |
| 客胜 |  |  |
| 大球 |  | 盘口： |
| 小球 |  | 盘口： |

### 5. 模型依据
- 预期进球：
- 泊松比分集中：
- 贝叶斯修正：
- 赔率价值：

### 6. 三个比分候选
- 主推比分：
- 次选比分：
- 冷门/风险比分：

### 7. 参考购买方案
- 胜平负/让球：
- 大小球/总进球：
- 比分覆盖：
- 不建议项：

### 8. 风险点
- 
```

## Portfolio Report

```markdown
## 四串一参考方案

### 1. 比赛确认
| 编号 | 比赛 | 时间 | 赛事 | 主客/中立 | 数据置信度 | 赔率/盘口来源 |
|---|---|---|---|---|---|---|

### 2. 赔率/盘口摘要
| 比赛 | 胜平负 | 让球 | 大小球 | 来源/时间 | 置信度 |
|---|---|---|---|---|---|

### 3. 每场简版结论
| 比赛 | 主要倾向 | 比分覆盖 | 等级 | 核心风险 |
|---|---|---|---|---|

### 4. 组合相关性检查
- 独立性/相关性：
- 共同风险：
- 不建议强行纳入的场次：

### 5. 分档参考购买方案
| 档位 | 注数组合 | 合计 | 每场选择 | 适用场景 | 风险 |
|---|---:|---:|---|---|---|
| 2 元档 | 1 注 | 2 元 | 每场 1 个方向 | 最低覆盖 |  |
| 16 元档 | 8 注 | 16 元 | 1 x 2 x 2 x 2 | 小额比分覆盖 |  |
| 32 元档 | 16 注 | 32 元 | 2 x 2 x 2 x 2 | 基础比分覆盖 |  |
| 48 元档 | 24 注 | 48 元 | 3 x 2 x 2 x 2 | 增强比分覆盖 |  |

### 6. 更多组合候选
| 组合 | 注数/金额 | 每场选择 | 使用条件 | 风险 |
|---|---:|---|---|---|

### 7. Pass / 排除项
- 
```

Portfolio rules:

- Support up to four matches.
- Provide 2 元, 16 元, 32 元, and 48 元 Ticket Tiers when enough data exists.
- Keep amount and unit count explicit. With the default 2 元/unit, 16 units equals 32 元, not 16 元.
- More Combination Candidates are optional alternatives, not extra mandatory purchases.
- Score Coverage may include up to four scores per match only when needed to produce the declared unit count.
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
