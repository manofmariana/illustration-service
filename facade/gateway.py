"""统一网关:一条进程服务全部模式,按 URL 前缀 / model 字段 / 默认模式选择。

    POST /<mode>/v1/chat/completions     酒馆填 http://<ip>:8388/moss/v1
    POST /<mode>/v1/responses            凡人前端填 http://<ip>:8388/frz/v1
    POST /v1/chat/completions            不带前缀 → DEFAULT_MODE(默认酒馆 Anima)
    GET  /                               管理页(选服务 / 选 harness / 填 key)
    GET  /api/status  /api/settings      管理接口(默认仅本机)
    GET  /healthz  /models               公开信息
"""
import json
import logging
import socket
import time

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response, StreamingResponse

from . import config, dsh_workspace, modes, settings, sse, ui
from .runtimes import BACKENDS, AgentError, make
from .runtimes.dsh import DshRuntime

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("gateway")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    linked = dsh_workspace.link(config.BASE_DIR)
    if linked:
        log.info("已把 %d 个 DSH 会话登记到 Desktop 工作区", linked)
    yield


app = FastAPI(title="illustration gateway", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_private_network=True,
)

SUFFIX_KINDS = {"chat/completions": "chat", "responses": "responses"}
_runtimes: dict[str, object] = {}


def runtime(name: str):
    if name not in BACKENDS:
        raise HTTPException(500, f"未知后端: {name}")
    if name not in _runtimes:
        _runtimes[name] = make(name)
    return _runtimes[name]


def backend_for(mode_key: str) -> str:
    cfg = settings.load()
    chosen = (
        str(cfg.get("backends", {}).get(mode_key) or "").strip()
        or config.backend_hint(mode_key)
        or config.AGENT_BACKEND
    )
    if chosen not in BACKENDS:
        log.warning("模式 %s 的后端 %r 不存在,回落 kimi", mode_key, chosen)
        return "kimi"
    if chosen == "dsh" and not settings.dsh_api_key():
        log.warning("模式 %s 指定 dsh 但没有 API key,本次回落 kimi", mode_key)
        return "kimi"
    return chosen


def _local_only(req: Request) -> None:
    if config.ALLOW_REMOTE_ADMIN:
        return
    host = req.client.host if req.client else ""
    if host not in ("127.0.0.1", "::1", "localhost"):
        raise HTTPException(403, "管理接口只允许本机访问")


def _error(status: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={
        "error": {"message": message, "type": "facade_error", "code": None}
    })


def _kimi_reachable() -> bool:
    url = config.KIMI_BASE_URL
    host_port = url.split("//")[-1].split("/")[0]
    host, _, port = host_port.partition(":")
    try:
        with socket.create_connection((host, int(port or 80)), timeout=0.6):
            return True
    except OSError:
        return False


def _resolve_path(full_path: str) -> tuple[modes.Mode | None, str]:
    """只解析路径:URL 前缀命中就返回模式,否则 None(交给 model 字段 / 默认模式)。"""
    path = full_path.strip("/")
    parts = path.split("/") if path else []
    by_prefix = modes.resolve(parts[0]) if parts else None
    rest = "/".join(parts[1:]) if by_prefix else path
    if rest.startswith("v1/"):
        rest = rest[3:]
    kind = SUFFIX_KINDS.get(rest)
    if not kind:
        raise HTTPException(404, f"未知接口路径: /{full_path}")
    return by_prefix, kind


async def _generate(mode: modes.Mode, body: dict) -> tuple[str, float]:
    """跑完整链路:提取 → agent(带校验重试)→ 渲染。返回最终文本与耗时。"""
    t0 = time.time()
    si = mode.extract(body)
    args = mode.build_args(si)
    backend = backend_for(mode.key)
    rt = runtime(backend)

    errors: list[str] = []
    for attempt in range(1 + config.MAX_RETRIES):
        attempt_args = args
        if errors:
            attempt_args += "\n\n[上次输出未通过校验,请修正后重新输出全部内容]\n" + "\n".join(
                f"- {e}" for e in errors
            )
        try:
            text = await rt.run(attempt_args, mode)
        except AgentError as e:
            errors = [f"agent 调用失败: {e}"]
            log.error("[%s/%s] 第%d次失败: %s", mode.key, backend, attempt + 1, e)
            continue

        blocks = mode.parse(text)
        errors = mode.validate(blocks, si.story, si.image_count)
        if not errors:
            elapsed = time.time() - t0
            log.info("[%s/%s] 完成 %.1fs, %d 块", mode.key, backend, elapsed, len(blocks))
            return mode.render(blocks), elapsed
        log.warning("[%s/%s] 校验失败(第%d次): %s", mode.key, backend, attempt + 1, errors[:3])

    raise AgentError("多次输出均未通过校验: " + "; ".join(errors[:4]))


@app.get("/", response_class=HTMLResponse)
async def admin_page(req: Request):
    _local_only(req)
    return HTMLResponse(ui.PAGE)


@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)


@app.get("/api/status")
async def status(req: Request):
    _local_only(req)
    cfg = settings.load()
    dsh_ok, dsh_reason = DshRuntime.available()
    return {
        "port": config.GATEWAY_PORT,
        "default_mode": cfg["default_mode"],
        "kimi": {"reachable": _kimi_reachable()},
        "dsh": {
            "ready": dsh_ok,
            "reason": dsh_reason,
            "model": cfg["dsh_model"],
            "key": settings.masked(settings.dsh_api_key()),
        },
        "modes": [
            {"key": m.key, "title": m.title, "backend": backend_for(m.key)}
            for m in modes.MODES.values()
        ],
    }


@app.get("/api/settings")
async def read_settings(req: Request):
    _local_only(req)
    cfg = settings.load()
    return {
        "default_mode": cfg["default_mode"],
        "backends": {m.key: backend_for(m.key) for m in modes.MODES.values()},
        "dsh_model": cfg["dsh_model"],
        "dsh_key_masked": settings.masked(settings.dsh_api_key()),
    }


@app.post("/api/settings")
async def write_settings(req: Request):
    _local_only(req)
    try:
        payload = json.loads((await req.body()).decode("utf-8"), strict=False)
    except Exception:
        raise HTTPException(400, "请求体不是合法 JSON")

    patch: dict = {}
    if "default_mode" in payload:
        mode = modes.resolve(str(payload["default_mode"]))
        if not mode:
            raise HTTPException(400, f"未知模式: {payload['default_mode']}")
        patch["default_mode"] = mode.key
    if "backends" in payload:
        clean = {}
        for key, value in dict(payload["backends"]).items():
            mode = modes.resolve(str(key))
            if not mode or str(value) not in BACKENDS:
                raise HTTPException(400, f"非法后端映射: {key}={value}")
            clean[mode.key] = str(value)
        merged = dict(settings.load().get("backends") or {})
        merged.update(clean)
        patch["backends"] = merged
    if "dsh_model" in payload and str(payload["dsh_model"]).strip():
        patch["dsh_model"] = str(payload["dsh_model"]).strip()
    if payload.get("clear_key"):
        patch["dsh_api_key"] = ""
    elif str(payload.get("dsh_api_key") or "").strip():
        patch["dsh_api_key"] = str(payload["dsh_api_key"]).strip()

    settings.save(patch)
    log.info("设置已更新: %s", sorted(patch))
    return await read_settings(req)


@app.get("/v1/models")
@app.get("/models")
async def models():
    return {"object": "list", "data": [
        {"id": m.key, "object": "model", "created": 0, "owned_by": "illustration-gateway"}
        for m in modes.MODES.values()
    ]}


@app.get("/healthz")
async def healthz():
    return {"ok": True, "modes": list(modes.MODES)}


# 必须最后注册:catch-all 会吞掉前面未声明的 POST 路径
@app.post("/{full_path:path}")
async def dispatch(full_path: str, req: Request):
    by_prefix, kind = _resolve_path(full_path)
    try:
        body = json.loads((await req.body()).decode("utf-8"), strict=False)
    except Exception:
        return _error(400, "请求体不是合法 JSON")

    # 路径前缀优先,其次请求里的 model 字段,最后默认模式
    mode = (
        by_prefix
        or modes.resolve(str(body.get("model") or ""))
        or modes.resolve(settings.load()["default_mode"])
        or modes.MODES["frz"]
    )

    try:
        text, _ = await _generate(mode, body)
    except ValueError as e:
        log.warning("[%s] 提取失败: %s", mode.key, e)
        return _error(400, f"无法从请求中提取素材: {e}")
    except AgentError as e:
        return _error(502, str(e))

    model = body.get("model") or mode.key
    if body.get("stream"):
        frames = (sse.chat_stream_events if kind == "chat" else sse.stream_events)(text, model)
        return StreamingResponse(
            iter(frames),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )
    if kind == "chat":
        return sse.chat_non_stream_response(text, model)
    return sse.non_stream_response(text, model)
