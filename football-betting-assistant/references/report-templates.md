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

### 2. 结论摘要
- 胜平负倾向：
- 让球胜平负倾向：
- 大小球/总进球倾向：
- 参考等级：A/B/C/Pass
- 模型置信度：高/中/低
- 数据置信度：高/中/低

### 3. 概率判断
| 市场 | 概率/区间 | 说明 |
|---|---:|---|
| 主胜 |  |  |
| 平局 |  |  |
| 客胜 |  |  |
| 大球 |  | 盘口： |
| 小球 |  | 盘口： |

### 4. 模型依据
- 预期进球：
- 泊松比分集中：
- 贝叶斯修正：
- 赔率价值：

### 5. 三个比分候选
- 主推比分：
- 次选比分：
- 冷门/风险比分：

### 6. 参考购买方案
- 胜平负/让球：
- 大小球/总进球：
- 比分覆盖：
- 不建议项：

### 7. 风险点
- 
```

## Portfolio Report

```markdown
## 四串一参考方案

### 1. 比赛确认
| 编号 | 比赛 | 时间 | 赛事 | 主客/中立 | 数据置信度 |
|---|---|---|---|---|---|

### 2. 每场简版结论
| 比赛 | 主要倾向 | 比分覆盖 | 等级 | 核心风险 |
|---|---|---|---|---|

### 3. 组合相关性检查
- 独立性/相关性：
- 共同风险：
- 不建议强行纳入的场次：

### 4. 主组合
- 玩法：
- 每场选择：
- 比分覆盖：
- 风险档位：
- 价值判断：

### 5. 保守替代
- 玩法：
- 每场选择：
- 比分覆盖：
- 风险档位：
- 适用场景：

### 6. 激进替代
- 玩法：
- 每场选择：
- 比分覆盖：
- 风险档位：
- 主要风险：

### 7. Pass / 排除项
- 
```

Portfolio rules:

- Support up to four matches.
- Provide main, conservative, and aggressive Portfolio Variants when enough data exists.
- Score Coverage may include up to three scores per match.
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

Do not include chase-loss, recovery-bet, or stake-size advice.
