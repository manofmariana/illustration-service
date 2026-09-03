"""facade 入口:伪装 DeepSeek Responses API,把生图请求转给 kimi agent。

POST /v1/responses
  → extractor 切分素材
  → kimi_client 驱动 story-illustrator 技能(带校验重试)
  → validator 硬校验
  → sse 包装返回
"""
import json
import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from . import config, extractor, sse, validator
from .kimi_client import KimiClient, KimiError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("facade")

app = FastAPI(title="story-illustrator facade")

# 网页端在浏览器里 fetch 本服务,跨域时必须应答预检(OPTIONS),否则浏览器报 "Failed to fetch"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_private_network=True,  # Chrome PNA:局域网/公网页面访问 127.0.0.1 需要,否则预检 400 → Failed to fetch
)
_kimi: KimiClient | None = None


def get_kimi() -> KimiClient:
    global _kimi
    if _kimi is None:
        _kimi = KimiClient()
    return _kimi


def _error(status: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={
        "error": {"message": message, "type": "facade_error", "code": None}
    })


@app.post("/v1/responses")
@app.post("/responses")
@app.post("/v1/chat/completions")
@app.post("/chat/completions")
async def responses(req: Request):
    t0 = time.time()
    try:
        body = json.loads((await req.body()).decode("utf-8"), strict=False)
    except Exception:
        return _error(400, "请求体不是合法 JSON")

    try:
        si = extractor.extract(body)
    except ValueError as e:
        log.warning("提取失败: %s", e)
        return _error(400, f"无法从请求中提取正文素材: {e}")

    log.info("收到生图请求: %d 张图, 正文 %d 字", si.image_count, len(si.story))
    args = extractor.build_skill_args(si)

    # agent 循环 + 校验重试:失败时把错误列表反馈给新会话
    last_errors: list[str] = []
    final_text = ""
    for attempt in range(1 + config.MAX_RETRIES):
        attempt_args = args
        if last_errors:
            attempt_args += (
                "\n\n[上次输出未通过校验,请修正后重新输出全部内容]\n"
                + "\n".join(f"- {e}" for e in last_errors)
            )
        try:
            text = await get_kimi().run_skill(attempt_args)
        except KimiError as e:
            log.error("kimi 调用失败(第%d次): %s", attempt + 1, e)
            last_errors = [f"agent 调用失败: {e}"]
            continue

        blocks = validator.parse_blocks(text)
        last_errors = validator.validate(blocks, si.story, si.image_count)
        if not last_errors:
            final_text = validator.render(blocks)
            log.info("完成: %.1fs, %d 块", time.time() - t0, len(blocks))
            break
        log.warning("校验失败(第%d次): %s", attempt + 1, last_errors)
    else:
        pass  # 循环正常结束(最后一次也没过)

    if not final_text:
        return _error(502, "agent 多次输出均未通过格式校验: " + "; ".join(last_errors[:5]))

    model = body.get("model", "story-illustrator")
    api_kind = "chat" if req.url.path.endswith("chat/completions") else "responses"
    if body.get("stream"):
        frames = (sse.chat_stream_events if api_kind == "chat" else sse.stream_events)(final_text, model)
        return StreamingResponse(
            iter(frames),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )
    if api_kind == "chat":
        return sse.chat_non_stream_response(final_text, model)
    return sse.non_stream_response(final_text, model)


@app.get("/v1/models")
@app.get("/models")
async def models():
    """网页端可能探测模型列表,给个最小响应。"""
    return {"object": "list", "data": [
        {"id": "story-illustrator", "object": "model", "created": 0, "owned_by": "facade"}
    ]}


@app.get("/healthz")
async def healthz():
    return {"ok": True}
