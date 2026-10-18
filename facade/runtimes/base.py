"""agent 运行时抽象:同一个技能可以跑在 kimi web 上,也可以跑在 DSH 上。"""


class AgentError(RuntimeError):
    """运行时失败(连不上、超时、退出码非零)。"""


class AgentRuntime:
    name = ""

    async def run(self, args: str, mode) -> str:
        """执行一次技能,返回 agent 的最终文本。失败抛 AgentError。"""
        raise NotImplementedError
