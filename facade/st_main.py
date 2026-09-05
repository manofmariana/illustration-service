"""ST(SillyTavern)专用伪装服务:与网页端 facade 完全隔离。

POST /v1/chat/completions(:8389)
  → st_extractor 切分素材(暂定策略,原始请求落盘 logs/st/)
  → kimi_client 驱动 story-illustrator-st 技能(带校验重试)
  → st_validator 硬校验(ST 契约)
  → 渲染 <images><image>regex:/image###tags###</image></images> 返回
"""
import json
import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from . import config, sse, st_extractor, st_validator
from .kimi_client import KimiClient, KimiError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("facade-st")

app = FastAPI(title="story-illustrator-st facade")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_private_network=True,
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


@app.post("/v1/chat/completions")
@app.post("/chat/completions")
@app.post("/v1/responses")
@app.post("/responses")
async def st_generate(req: Request):
    t0 = time.time()
    try:
        body = json.loads((await req.body()).decode("utf-8"), strict=False)
    except Exception:
        return _error(400, "请求体不是合法 JSON")

    try:
        si = st_extractor.extract(body)
    except ValueError as e:
        log.warning("ST 提取失败: %s", e)
        return _error(400, f"无法从请求中提取剧情素材: {e}")

    log.info("收到 ST 生图请求: %d 张图, 素材 %d 字", si.image_count, len(si.material))
    args = st_extractor.build_skill_args(si)

    last_errors: list[str] = []
    final_text = ""
    for attempt in range(1 + config.MAX_RETRIES):
        attempt_args = args
        if last_errors:
            attempt_args += (
                "\n\n[上次输出未通过 ST 格式校验,请修正后重新输出全部内容]\n"
                + "\n".join(f"- {e}" for e in last_errors)
            )
        try:
            text = await get_kimi().run_skill(attempt_args, skill_name=config.ST_SKILL_NAME)
        except KimiError as e:
            log.error("kimi 调用失败(第%d次): %s", attempt + 1, e)
            last_errors = [f"agent 调用失败: {e}"]
            continue

        blocks = st_validator.parse_blocks(text)
        last_errors = st_validator.validate(blocks, si.material, si.image_count)
        if not last_errors:
            final_text = st_validator.render(blocks)
            log.info("ST 完成: %.1fs, %d 块", time.time() - t0, len(blocks))
            break
        log.warning("ST 校验失败(第%d次): %s", attempt + 1, last_errors)

    if not final_text:
        return _error(502, "agent 多次输出均未通过 ST 格式校验: " + "; ".join(last_errors[:5]))

    model = body.get("model", "story-illustrator-st")
    api_kind = "chat" if "chat/completions" in req.url.path else "responses"
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
    return {"object": "list", "data": [
        {"id": "story-illustrator-st", "object": "model", "created": 0, "owned_by": "facade"}
    ]}


@app.get("/healthz")
async def healthz():
    return {"ok": True, "service": "st"}
