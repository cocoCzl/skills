# Contributing

感谢你改进这个 skills 合集。这个仓库的目标是让别人 clone 后可以直接理解、安装和验证每个 skill，而不是依赖某个人本地的 agent 运行态目录。

## 添加新 Skill

每个 skill 应放在仓库顶层的独立目录中：

```text
skill-name/
  SKILL.md
  README.md
```

推荐按需添加：

```text
references/
examples/
schemas/
scripts/
tests/
evals/
```

`SKILL.md` 应包含清晰的触发描述、执行边界、需要读取的参考文件和输出要求。`README.md` 应面向人类使用者说明安装、配置、示例和测试方式。

## 不要提交的内容

不要提交：

- 真实 API key、token、密码、cookie 或私有配置。
- `.agent/`、`.agents/`、`.claude/`、`.pi/`、`skills-lock.json` 等本地运行态文件。
- `.env`、IDE 配置、系统缓存、`.DS_Store`、`__pycache__/`、测试缓存。
- 只能在个人机器上生效的绝对路径或个人用户名。

如果示例需要配置，请使用占位符，例如：

```bash
THE_ODDS_API_KEY=your_api_key
```

## 检查要求

提交前运行：

```bash
python3 scripts/check_all_skills.py
```

如果只改了一个 skill，也可以运行该 skill 自带的验收脚本，例如：

```bash
python3 football-betting-assistant/scripts/run_acceptance_checks.py
```

## 文档要求

新增或修改 skill 时，请同步更新：

- skill 自己的 `README.md`
- 示例输出或输入
- eval 描述或验收脚本
- 仓库根目录 `README.md` 的 skill 列表

## 安全和合规

Skill 可以指导用户配置外部服务，但不能内置凭据、绕过访问限制、抓取未授权数据，或暗示拥有未验证的实时数据能力。涉及投注、医疗、法律、金融等高风险领域时，应保留清晰的限制说明和风险提示。
