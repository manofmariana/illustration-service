"""kimi web 运行时:每请求一个独立会话,按技能名激活。"""
from ..kimi_client import KimiClient, KimiError
from .base import AgentError, AgentRuntime


class KimiRuntime(AgentRuntime):
    name = "kimi"

    def __init__(self) -> None:
        self._client: KimiClient | None = None

    def _get(self) -> KimiClient:
        if self._client is None:
            self._client = KimiClient()
        return self._client

    async def run(self, args: str, mode) -> str:
        try:
            return await self._get().run_skill(args, skill_name=mode.skill)
        except KimiError as e:
            raise AgentError(str(e)) from e
