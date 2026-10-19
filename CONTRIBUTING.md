# 参与贡献

## 可以贡献什么

| 类型 | 说明 |
|---|---|
| 新增模式 | 接一个新模型或新的插件分支，需要 SKILL + 校验器 + 注册 |
| 接入其他插件 | 对齐请求端的标签与服务端的返回格式 |
| 新增 Harness | 适配另一个 agent 的会话调用方式 |
| 修 bug / 改文档 | 直接提 PR |

新增模式与 Harness 的具体步骤写在 README 的「参与贡献」一节，这里只讲流程与边界。

## 提交流程

1. Fork 本仓库，从 `main` 切一个分支。
2. 只改与目的相关的文件，不要顺手改格式或重排文档。
3. 提 PR，写明改了什么、为什么改。

## 新增一个模式时的最小改动

| 文件 | 内容 |
|---|---|
| `.agents/skills/story-illustrator-<模式名>/SKILL.md` | frontmatter 的 `name` 与目录同名；正文写铁律、决策树、槽位顺序、输出契约 |
| `facade/<名字>_validator.py` | `parse_blocks()` / `validate()` / `render()` 三个函数 |
| `facade/modes.py` | 在 `MODES` 里注册一条 `Mode(...)` |
| 提取器 | 请求端标签与现在不同时才需要新写，能复用 `st_extractor` 就不要另起一套 |

改动越小越好：能复用现有提取器、校验器或渲染器，就不要复制一份。

## 不要提交的东西

- `instance/`、`logs/`，以及任何 `sk-` 开头的 key
- 自己机器上的绝对路径（MCP 可执行文件路径请留空或写占位符）
- 第三方目录，例如 `Booru-Pictag-Get-MCP/`（已在 `.gitignore` 里）
