"""DSH 运行时:每次请求起一个 `dsh --profile headless` 进程,stdout 即结果。

headless 是 DSH 官方的一次性入口("answer one task, print the result, and exit")。
每次运行都会持久化成一个正常的 DSH 会话,可以在 DSH Desktop 里打开
`illustration-service` 这个工作区回看完整过程(思考、工具调用、输出)。

技能和 MCP 都不进提示词:技能放在项目根的 `.agents/skills`,kimi 与 dsh 都原生扫描;
`.kimi-code/mcp.json` 由运行时翻成 dsh 的 MCP 条目。两边共用同一批文件。

headless 只能用 API key 认证——桌面端的账号登录态依赖 authorization 服务,命令行里拿不到。
"""
import asyncio
import json
import logging
import os

from pathlib import Path

import yaml

from .. import config, dsh_workspace, settings
from .base import AgentError, AgentRuntime

log = logging.getLogger("gateway.dsh")

# 这些环境变量会把调用方(可能是一个 DSH 会话)的上下文带进子进程
SCRUBBED = ("DSH_PROFILE", "DSH_PROFILE_DIR", "DSH_SESSION_ID", "DSH_WEB_URL", "DSH_SHELL")

STORY_MARKER = "[剧情与设定素材]\n"


def _mcp_servers() -> list[dict]:
    """把 kimi 的 mcp.json 翻成 dsh-mcp-client 的条目(只接管 stdio,HTTP 的留给 kimi)。"""
    if not config.SHARED_MCP_JSON.exists():
        return []
    spec = json.loads(config.SHARED_MCP_JSON.read_text(encoding="utf-8")).get("mcpServers") or {}
    servers = []
    for name, server in spec.items():
        command = server.get("command")
        if not command:
            continue
        if os.path.isabs(command) and not Path(command).exists():
            # mcp.json 里可能是别人机器上的路径,不存在就跳过,别每次请求都去 spawn 一个空进程
            log.warning("MCP %s 的可执行文件不存在,本次跳过: %s", name, command)
            continue
        servers.append({
            "id": f"mcp-{name}",
            "name": "@deepseek-ai/dsh-mcp-client",
            "config": {
                "serverName": name,
                "transport": "stdio",
                "command": command,
                "args": server.get("args") or [],
                "env": server.get("env") or {},
            },
        })
    return servers


def _patch_entries(model: str) -> list[dict]:
    entries = [
        {
            "id": "agent-default-model",
            "name": "@deepseek-ai/dsh-agent-default-model",
            "config": {"provider": "deepseek-official", "model": model},
        },
    ]
    servers = _mcp_servers()
    if servers:
        entries.append({"insert": servers})
    return entries


def _headline(args: str, mode) -> str:
    """给会话起个能认的标题:模式 + 剧情开头(Desktop 的会话列表用得上)。"""
    start = args.find(STORY_MARKER)
    if start < 0:
        return mode.title
    snippet = args[start + len(STORY_MARKER):][:24].splitlines()[0].strip()
    return f"{mode.title} | {snippet}" if snippet else mode.title


class DshRuntime(AgentRuntime):
    name = "dsh"

    @staticmethod
    def _cli_reachable() -> bool:
        """cli.js 可能打在 app.asar 里,Python 看不见,只能检查归档文件本身在不在。"""
        if config.DSH_CLI.exists():
            return True
        for parent in config.DSH_CLI.parents:
            if parent.suffix == ".asar":
                return parent.exists()
        return False

    @staticmethod
    def available() -> tuple[bool, str]:
        if not config.DSH_EXE.exists():
            return False, f"找不到 DSH 可执行文件: {config.DSH_EXE}"
        if not DshRuntime._cli_reachable():
            return False, f"找不到 DSH cli.js: {config.DSH_CLI}"
        if not settings.dsh_api_key():
            return False, "未配置 DSH API key(在本页填写并保存,或设 DEEPSEEK_API_KEY)"
        return True, ""

    def _patch_file(self) -> str:
        path = config.INSTANCE_DIR / "dsh-agent.patch.yml"
        path.parent.mkdir(parents=True, exist_ok=True)
        model = str(settings.load().get("dsh_model") or config.DSH_AGENT_MODEL).strip()
        path.write_text(
            yaml.safe_dump(_patch_entries(model), allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        return str(path)

    def _compose_task(self, args: str, mode) -> str:
        return (
            f"# 任务:{_headline(args, mode)}\n\n"
            f"先用 skill 工具加载技能 `{mode.skill}`,再严格按它规定的「输出契约」完成本次任务。\n"
            f"- 技能目录: {mode.skill_dir}\n"
            f"- 工作目录: {config.BASE_DIR}\n"
            "- 需要查规则或标签库时,用只读方式读技能目录下的 rules/ 与 tags/,不要读其它路径。\n"
            "- 禁止写文件、禁止解释、禁止 markdown 代码围栏、禁止向用户提问。\n"
            "- 最终回复只放契约要求的内容,不要有任何前言或后记。\n\n"
            f"<素材>\n{args}\n</素材>\n"
        )

    async def run(self, args: str, mode) -> str:
        ok, reason = self.available()
        if not ok:
            raise AgentError(reason)

        env = os.environ.copy()
        for key in SCRUBBED:
            env.pop(key, None)
        env["ELECTRON_RUN_AS_NODE"] = "1"
        env["DEEPSEEK_API_KEY"] = settings.dsh_api_key()

        cmd = [
            str(config.DSH_EXE),
            "--expose-internals",
            str(config.DSH_CLI),
            "--profile",
            config.DSH_AGENT_PROFILE,
            "--patch",
            self._patch_file(),
        ]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(config.BASE_DIR),
                env=env,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except OSError as e:
            raise AgentError(f"启动 DSH 失败: {e}") from e

        task = self._compose_task(args, mode).encode("utf-8")
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(task), config.DSH_TIMEOUT)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            raise AgentError(f"DSH 超时({config.DSH_TIMEOUT:.0f}s)")

        text = stdout.decode("utf-8", "replace").strip()
        dsh_workspace.link(config.BASE_DIR)  # 把这次会话登记进 Desktop 的工作区
        if proc.returncode != 0:
            detail = stderr.decode("utf-8", "replace").strip()[-800:]
            raise AgentError(f"DSH 退出码 {proc.returncode}: {detail}")
        if not text:
            raise AgentError("DSH 没有输出任何内容")
        return text
