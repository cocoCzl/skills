# Football Betting Assistant Examples

这个目录放仓库级示例，不是运行时 skill 的必需内容。安装 skill 时只需要复制或安装顶层 `football-betting-assistant/` 目录。

## Natural-Language Examples

面向普通使用者的提问模板：

- [`prompts.md`](prompts.md)：中文竞彩、比分、大小球、四串一、半全场、赛后复盘等自然语言请求。
- [`provider-setup.md`](provider-setup.md)：可选数据源 key 的配置方式、用途和限制。

## Structured JSON Examples

这些 JSON 用于开发、校验和离线复现：

- `single-match-input.json`：单场分析结构化输入。
- `portfolio-input.json`：组合/串关结构化输入。
- `single-match-model-input.json`：模型计算链路输入。
- `backtest-sample.json`：历史回测样本。

常用校验：

```bash
python3 football-betting-assistant/scripts/validate_inputs.py examples/football_betting_assistant/single-match-input.json
python3 football-betting-assistant/scripts/validate_inputs.py examples/football_betting_assistant/portfolio-input.json
python3 football-betting-assistant/scripts/validate_inputs.py examples/football_betting_assistant/backtest-sample.json
```
