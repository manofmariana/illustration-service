# illustration-service

手机网页 AI 对话生图链路的中间层:伪装 DeepSeek Responses API,把正文交给 Kimi Code agent(经 `story-illustrator` 技能)多轮设计提示词,硬校验后返回网页,网页再走原有 ComfyUI 流程。

## 架构

```
手机网页 ──POST /v1/responses──▶ facade (:8388)
                                   │ extractor:切出 角色/场景/正文/图片数
                                   ▼
                              kimi web (:58627,常驻)
                                   │ 每请求独立会话 → 激活 story-illustrator 技能
                                   │ agent 设计(Grep 查 tags/ 标签库)
                                   ▼
                              facade validator:块数/anchor逐字/禁词硬校验
                                   │ 失败 → 新会话带错误反馈重试(默认1次)
                                   ▼
                        DeepSeek Responses SSE ──▶ 手机网页
```

## 启动

1. 启动 kimi web(常驻 agent 平台):

```bat
kimi web --no-open --port 58627
```

启动横幅会打印 bearer token;设环境变量 `KIMI_TOKEN=<token>`,或执行过一次 `kimi web rotate-token`(facade 会自动读 `~/.kimi-code/server.token`)。

2. 启动 facade:

```bat
run_facade.bat
```

3. 手机网页端:把生图用的大模型 API 地址从 `https://api.deepseek.com` 改为 `http://<本机IP或穿透域名>:8388`。ComfyUI 地址不动。

facade 同时注册了四条路径,网页端填哪个都行:
- `/v1/responses` 和 `/responses`(Responses API 格式,input 数组)
- `/v1/chat/completions` 和 `/chat/completions`(Chat Completions 格式,messages 数组)

两种格式的请求体都能解析(以含「在场角色完整外观资料」的最长消息为准),响应自动按对应格式返回。

## 离线自测(不启动 kimi,只验证切分和校验)

```bat
..\python_embeded\python.exe -m facade.selftest <抓包的A.json路径>
```

## 配置(环境变量)

| 变量 | 默认 | 说明 |
|---|---|---|
| `KIMI_BASE_URL` | `http://127.0.0.1:58627` | kimi web 地址 |
| `KIMI_TOKEN` | 读 `~/.kimi-code/server.token` | kimi web bearer token |
| `KIMI_MODEL` | `Deepseek/deepseek-v4-flash-vision-exp` | agent 会话使用的模型别名(须与 `kimi provider list` 里的 alias key 精确一致;设为空字符串则用全局默认) |
| `FACADE_PORT` | `8388` | facade 监听端口 |
| `AGENT_TIMEOUT` | `300` | 等 agent 回合结束的秒数 |
| `MAX_RETRIES` | `1` | 校验失败重试次数 |

## 已知联调点

- **SSE 信封**:`facade/sse.py` 按 OpenAI Responses API 标准事件实现。若网页不认,抓一条 DeepSeek 真实响应流对照修改此文件即可,其他层不动。
- **超时**:agent 设计需几十秒到几分钟;网页端等待期间 facade 持有连接不发数据。若网页有短超时,需要确认其值并调 `AGENT_TIMEOUT`。
