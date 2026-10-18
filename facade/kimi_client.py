"""驱动 kimi web 常驻服务:每请求独立会话,激活技能,等待回合结束,取回复,归档。

流程:
  POST /api/v1/sessions            建会话(metadata.cwd 指向技能目录)
  POST .../profile                 permission_mode=auto(全自动,防卡住)
  POST .../skills/{name}:activate  args = 素材(即发起回合)
  轮询 GET .../status              直到 busy=false
  GET  .../messages                取最后一条 assistant 消息文本
  POST ...:archive                 归档,丢弃上下文
"""
import asyncio

import httpx

from . import config


class KimiError(RuntimeError):
    pass


class KimiClient:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=config.KIMI_BASE_URL,
            headers={"Authorization": f"Bearer {config.kimi_token()}"},
            timeout=httpx.Timeout(30.0),
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def _data(self, resp: httpx.Response):
        if resp.status_code != 200:
            raise KimiError(f"HTTP {resp.status_code}: {resp.text[:300]}")
        body = resp.json()
        if body.get("code") != 0:
            raise KimiError(f"kimi api code={body.get('code')} msg={body.get('msg')}")
        return body.get("data")

    async def run_skill(self, args: str, skill_name: str | None = None) -> str:
        """跑一次指定技能,返回 agent 最终文本。失败抛 KimiError。"""
        skill_name = skill_name or config.SKILL_NAME
        data = await self._data(await self._client.post(
            "/api/v1/sessions", json={"metadata": {"cwd": config.SKILL_CWD}}
        ))
        sid = data["id"]
        try:
            agent_config: dict = {"permission_mode": "auto"}
            if config.KIMI_MODEL:
                agent_config["model"] = config.KIMI_MODEL
            await self._data(await self._client.post(
                f"/api/v1/sessions/{sid}/profile",
                json={"agent_config": agent_config},
            ))
            await self._data(await self._client.post(
                f"/api/v1/sessions/{sid}/skills/{skill_name}:activate",
                json={"args": args},
                timeout=httpx.Timeout(60.0),
            ))
            await self._wait_idle(sid)
            return await self._last_assistant_text(sid)
        finally:
            try:
                await self._client.post(f"/api/v1/sessions/{sid}:archive")
            except Exception:
                pass  # 归档失败不影响主流程

    async def _wait_idle(self, sid: str) -> None:
        deadline = asyncio.get_event_loop().time() + config.AGENT_TIMEOUT
        while True:
            data = await self._data(await self._client.get(f"/api/v1/sessions/{sid}/status"))
            if not data.get("busy"):
                return
            if asyncio.get_event_loop().time() > deadline:
                try:
                    await self._client.post(f"/api/v1/sessions/{sid}:abort")
                except Exception:
                    pass
                raise KimiError(f"agent 超时({config.AGENT_TIMEOUT}s)")
            await asyncio.sleep(config.POLL_INTERVAL)

    async def _last_assistant_text(self, sid: str) -> str:
        data = await self._data(await self._client.get(
            f"/api/v1/sessions/{sid}/messages",
            params={"role": "assistant", "page_size": 10},
        ))
        for msg in data.get("items", []):  # newest first
            parts = [p.get("text", "") for p in msg.get("content", [])
                     if isinstance(p, dict) and p.get("type") == "text"]
            text = "".join(parts).strip()
            if text:
                return text
        raise KimiError("会话中没有 assistant 文本回复")
