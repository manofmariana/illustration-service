# illustration-service

给「酒馆 / 独立前端」用的**提示词中间层**。

它把自己伪装成一个 OpenAI / DeepSeek 接口。前端照常发聊天请求，它不聊天，而是把剧情正文交给一个本地 agent，由 agent 按固定的方法论写出画师能用的提示词，再经过硬校验，最后按约定的格式返回。前端拿到结果，自己丢给 ComfyUI 出图。

一个进程、一个端口，按 URL 前缀切四种模式；agent 后端可以在 DSH 与 KimiCode 之间切换。

---

## 为什么需要它

直接把「请根据这段剧情写生图提示词」丢给聊天模型，会稳定地产生三类问题：

1. **格式飘**。让它输出 `<images><image>…</image></images>`，它偏要加一句「好的，以下是…」，或者把标签名写错，插件的正则就抓不到。
2. **数量不对**。要 2 张给 3 张，或者把 2 张写成 1 张。
3. **画不对**。提示词跟正文脱节：人换了衣服、场景换了地方、画面里出现的角色正文里根本不在场。

这一层就是干这三件事的：**给料**（把请求里的素材切干净）、**绑方法**（让 agent 按技能文档的决策树和标签库干活）、**验收**（不合格就带着错误清单让它重写一次）。

---

## 一次请求发生了什么

以酒馆为例，假设你在正文里触发了生图：

1. 酒馆把你配置的预设渲染成一段文本，里面带 `<剧情原文>`、`<用户需求>`、`<生图数量>`、`<可用绘图角色列表>`、`<历史前文>` 这些标签，POST 到 `http://<你的IP>:8388/anima/v1/chat/completions`。
2. 网关看路径里的 `anima`，选中动画分支；把请求体里的标签逐段切出来，拼成一份「素材」。
3. 素材丢给 agent（DSH 或 KimiCode），并要求它先加载对应的技能文档（`.agents/skills/story-illustrator-st/SKILL.md`）。技能里写清楚了决策树、槽位顺序、标签库怎么查、输出长什么样。
4. agent 回一段 `<images><image>…</image></images>`。
5. 网关把它解析成结构化块，逐项校验：块数对不对、`<regex>` 是不是正文原句、`<size>` 合不合法、有没有禁用词、布局框有没有出界。
6. 校验不过就带着错误清单让它重写一次（`MAX_RETRIES`）。还不过就返回 502，并在日志里写清楚原因。
7. 通过后渲染成插件认识的样子返回（普通 JSON 或 SSE 流）。
8. 插件用 `%prompt%` / `%width%` / `%height%` / `%seed%` 做字符串替换，把你自己的 ComfyUI 工作流填好，提交出图。

网关全程不碰 ComfyUI，也不保存图片——出图完全在插件那一侧。

---

## 四种模式

| 模式 | 给谁用 | `<prompts>` 里是什么 | 插件里填的地址 |
|---|---|---|---|
| `anima` | 酒馆 · Anima 工作流 | Danbooru tag 串 | `http://<ip>:8388/anima/v1` |
| `moss` | 酒馆 · MOSS-Image（caption） | 英文单段散文 | `http://<ip>:8388/moss/v1` |
| `layout` | 酒馆 · MOSS-Image（layout） | 布局 JSON | `http://<ip>:8388/layout/v1` |
| `frz` | 凡人修仙传独立前端 | Danbooru tag 串 | `http://<ip>:8388/frz/v1` |

- 插件只认 `${自定义地址}/chat/completions`，所以**填到 `/v1` 为止**。
- 不带前缀的 `/v1/...` 走管理页当前选中的服务。
- 请求体里的 `"model": "moss"` 也能选模式，但**路径优先**。
- 名字对不上时：`st` → `anima`，`web` → `frz`，`moss-layout` → `layout`。

---

## 快速开始

**1. 装并登录 DSH**（后端见下一节，这是唯一推荐的路）

**2. 启动服务**

```bat
run_gateway.bat
```

默认监听 `0.0.0.0:8388`。浏览器打开 `http://127.0.0.1:8388/` 是管理页。

**3. 在管理页填两样**

- **DSH 的 API key**（`sk-…`）和模型名（默认 `deepseek-flash`）
- **服务 / harness** 两个下拉：前者决定不带前缀的请求走哪条分支，后者决定这条分支用哪个 agent

**4. 装酒馆插件并指向本服务**

插件：<https://github.com/damoshen123/st-chatu8>

- 生图后端地址填 `http://<你的局域网IP>:8388/anima/v1`（MOSS 换 `moss`/`layout`）
- **固定正面提示词留空**，固定负面提示词也可以留空（工作流里已经写死；cfg 1.0 时负面本来不参与计算）
- **「AI 自主分辨率」保持开启**，否则 `<size>` 不生效
- 模型下拉随便选一个非空项，它只用来过插件的空值校验，真正的模型写在你自己的工作流里

---

## 后端：只用 DSH

`facade/runtimes/` 下有两个实现，但**只推荐 DSH**。

### DSH（推荐）

每次请求起一个 `dsh --profile headless` 进程，stdout 就是最终文本，cwd 指向本仓库。

- **只需要一个 API key**，账号登录态在命令行里本来就不可用（会报 `ACCOUNT_SIGN_IN_REQUIRED`），填 key 即可。
- **技能和 MCP 与 KimiCode 共用同一份**：技能在 `.agents/skills/`（两边都原生扫描这个目录），MCP 清单在 `.kimi-code/mcp.json`。运行时生成的 `instance/dsh-agent.patch.yml` 只做两件事：钉模型、把 `mcp.json` 里的 stdio server 插成 `dsh-mcp-client` 条目。
- **技能不进提示词**：任务里只写「用 skill 工具加载 `<技能名>`」，agent 自己调 `skill` 拿正文、按需读 `rules/` 和 `tags/`。好处是省 token，也便于你在 DSH Desktop 里看它到底怎么想的。
- **能看全过程**：每次运行都会落成一个正常会话。在 DSH Desktop 打开 `illustration-service` 工作区，能看到思考、读了哪个 `rules/`、grep 了什么、最终输出。任务首行带 `# 任务:<模式> | <剧情开头>`。
- **会话会归位**：headless 自己不登记工作区，`facade/dsh_workspace.py` 会在每次运行后（以及启动时）把该目录下的会话补进 `workspace.json`。不想要就设 `DSH_LINK_WORKSPACE=0`。
- key 取用顺序：管理页保存的 `instance/settings.json` → 环境变量 `DEEPSEEK_API_KEY`。

### KimiCode（不推荐，除非你知道自己在改什么）

`runtime` 走本机的 `kimi web` 常驻服务（默认 `127.0.0.1:58627`），按技能名激活、每请求一个会话。

**别人的机器上大概率直接跑不通**，因为它绑死了一堆个人设置：

- `KIMI_MODEL` 默认是 `Deepseek/deepseek-flash`，这是作者 `~/.kimi-code/config.toml` 里的模型别名。你的配置里没有这个别名就用不了——改成你自己 `config.toml` 里的 alias，或者留空走全局默认模型。
- 需要先有 `kimi web` 在跑，且 token 在 `~/.kimi-code/server.token`（或用 `KIMI_TOKEN` 给）。
- 每个人的 provider、key、模型列表都不一样，抄过去必然要改。

所以：**只想开箱即用，就用 DSH。** 想用 KimiCode，请自己改好 `facade/config.py` 里的 `KIMI_MODEL` 和你的 `config.toml`，或者直接把这段交给 AI 让它帮你对一遍。

---

## 输出契约

### 凡人前端（`frz`）

请求体里是「在场角色完整外观资料 / 场景信息 / 当前正文 / 当前正文生图模式 / 固定输出 N 个」。返回：

```
<image>
<anchor>正文原句</anchor>
<prompt>英文 tag</prompt>
</image>
```

`anchor` 必须逐字命中正文、8–30 字、按剧情顺序。

### 酒馆三条分支（`anima` / `moss` / `layout`）

```
<images>
<image>
<regex>剧情原句，5-60 字，单行</regex>
<title_styled>标题，5-15 字中文</title_styled>
<Tag_think>60-100 字半文言</Tag_think>
<size>1024x1536</size>
<prompts>…</prompts>
</image>
</images>
```

- `anima` 的 `<prompts>` 是 tag 串。
- `moss` 的 `<prompts>` 是英文单段散文（MOSS 官方 Prompt Enhancer 规格：80–200 词，禁质量词、禁权重语法、禁下划线 tag；画面里的文字用原语言引用）。
- `layout` 的第五个标签在 agent 侧叫 `<layout>`，由网关编译成 `<prompts>`，见下。

### layout 的逗号转义

酒馆插件会把提示词送进 `deduplicateTags`，它按逗号切分去重——直接送布局 JSON 会被切碎：

```
DROPPED: ['{"label":"text"', '-12', '388]}]']
JSON VALID: NO -> Expecting ',' delimiter
```

所以网关把编译后 JSON 里的每个 `,` 换成了 `¦`（U+00A6）。整段没有逗号，插件就只看到一个分段，原样保留。

**这意味着你的 layout 工作流里必须有一个把 `¦` 换回 `,` 的节点**（ComfyUI 核心的 `StringReplace`，find `¦`，replace `,`），接在正面提示词前面。caption 分支不需要。

---

## ComfyUI 工作流：自己带

本仓库**不附带**工作流文件，因为每个人的模型、VAE、LoRA、采样设置都不一样。约定很简单：你的 API 格式工作流里留四个占位符，插件做纯字符串替换。

| 占位符 | 会被换成 |
|---|---|
| `%prompt%` | 上面 `<prompts>` 的内容 |
| `%width%` / `%height%` | `<size>` 拆出来的宽高 |
| `%seed%` | 插件的种子；填 `-1`/`0` 每次随机 |

其余全部写死在你自己的工作流里（模型、步数、CFG、负面提示词……）。

---

## 配置

| 环境变量 | 默认 | 说明 |
|---|---|---|
| `GATEWAY_PORT` | `8388` | 监听端口 |
| `DEFAULT_MODE` | `anima` | 不带前缀时走哪条分支（管理页保存的值优先） |
| `AGENT_BACKEND` | `kimi` | 全局后端；`AGENT_BACKEND_<MODE>` 可按模式覆盖 |
| `MAX_RETRIES` | `1` | 校验失败后的重写次数 |
| `AGENT_TIMEOUT` | `300` | 等 KimiCode 回合结束的秒数 |
| `DEEPSEEK_API_KEY` | — | DSH 的兜底 key |
| `ALLOW_REMOTE_ADMIN` | `0` | 设 `1` 才允许局域网访问管理页 |
| `DSH_ROOT` | `D:\DeepSeek Harness` | DSH 安装目录 |
| `DSH_AGENT_MODEL` | `deepseek-flash` | DSH 模型 |
| `DSH_TIMEOUT` | `420` | 单次 DSH 超时 |

管理页保存的东西写在 `instance/settings.json`，优先级高于环境变量。

> 别用 `DSH_PROFILE` 这个变量名——桌面端自己用它，会把 `desktop` profile 带进子进程。运行时也会主动剥掉 `DSH_PROFILE` / `DSH_SESSION_ID` / `DSH_WEB_URL` 等。

---

## 敏感信息

- 仓库里**没有任何 API key**。key 只存在两处：你本机的 `instance/settings.json`（已在 `.gitignore` 里），或环境变量 `DEEPSEEK_API_KEY`。
- 管理接口返回的 key 永远是打码的（`sk-1…abcd`），前端拿不到明文。
- `instance/`、`logs/`、`__pycache__/`、`Booru-Pictag-Get-MCP/`（第三方 MCP，含虚拟环境）都不入库。
- 管理页和管理接口默认**只允许本机**访问，局域网只能调生成接口。

---

## 技能与 MCP

- 技能只有一份：`.agents/skills/<name>/SKILL.md`（外加 `rules/`、`tags/`）。KimiCode 按名字激活，DSH 从同一个目录自动发现。改技能只动这里。
- `.kimi-code/mcp.json` 注册了 Booru-Pictag-Get（搜索 danbooru 标签），技能铁律限定**只用于同人/IP 角色**，每个角色最多 2 次。DSH 运行时把它翻成 `dsh-mcp-client` 条目，工具名以 `mcp__booru-pictag-get__*` 出现。
- 这个 MCP 的可执行文件路径是作者自己机器上的（`.venv/Scripts/booru-pictag-get-mcp.exe`），**换机器要改**。文件不存在时 DSH 照常跑，只是没有那几个工具。

---

## 目录结构

```
facade/
  gateway.py      唯一入口：路由、管理页、OpenAI 兼容响应、重试
  modes.py        模式注册表：一条分支 = 提取器 + 技能 + 解析 + 校验 + 渲染
  config.py       路径与所有可覆盖的默认值
  settings.py     instance/settings.json 的读写（key 在这里）
  ui.py           管理页 HTML
  extractor.py    凡人前端的素材提取 + 参数拼装
  st_extractor.py 酒馆的标签提取（<剧情原文> 等）
  validators…     frz / anima / moss / layout 各自的解析与校验
  moss_layout.py  布局草稿 → 官方编译格式（含 ¦ 转义）
  sse.py          OpenAI / DeepSeek 两种响应格式（流式与非流式）
  dsh_workspace.py DSH 会话补登记
  runtimes/       kimi.py / dsh.py / base.py
.agents/skills/   技能文档（agent 的方法论都在这里）
.kimi-code/       MCP 清单
instance/         本地设置（不入库）
```

---

## 自测

离线，不需要联网也不需要模型：

```bat
..\python_embeded\python.exe -m facade.st_selftest
..\python_embeded\python.exe -m facade.moss_selftest
```

`st_selftest` 覆盖酒馆标签提取：新旧预设、`<thinking>` 剥离、宏未渲染、空素材、图片数量兜底。
`moss_selftest` 覆盖 caption 规则、布局编译与居中换算、酒馆整链预演（追加尺寸 → 抽走尺寸 → 压平换行 → 去重 → 转义还原）、几何拦截。

---

## 排错

| 现象 | 原因 |
|---|---|
| `502 多次输出均未通过校验` | agent 反复不合格，日志里带着每次的错误清单 |
| `500` 且日志里有 `FileNotFoundError` | 改过代码没重启；`run_gateway.bat` 重启一次 |
| 酒馆报连接失败 | 插件地址没填到 `/v1`，或者防火墙挡了 8388 |
| 生图尺寸不对 | 插件「AI 自主分辨率」没开 |
| 一次出图很久 | MOSS 的 9B 文本编码器在 8G 显存上基本靠 offload；先降分辨率试 |
