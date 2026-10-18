"""facade 配置:全部可用环境变量覆盖。"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent          # illustration-service/
SKILL_CWD = str(BASE_DIR)                                  # agent 工作目录(含 .agents/skills)
SKILL_NAME = "story-illustrator"
# 技能只有一份,放 .agents/skills:kimi 与 dsh 都原生扫描这个目录(.agents 是两者共用的约定)
SKILLS_DIR = BASE_DIR / ".agents" / "skills"
SHARED_MCP_JSON = BASE_DIR / ".kimi-code" / "mcp.json"

KIMI_BASE_URL = os.environ.get("KIMI_BASE_URL", "http://127.0.0.1:58627")
KIMI_TOKEN = os.environ.get("KIMI_TOKEN", "")              # 留空则读 ~/.kimi-code/server.token
KIMI_TOKEN_FILE = Path.home() / ".kimi-code" / "server.token"
# kimi config.toml 里配置的模型别名(精确 alias key);留空则用全局 default_model
KIMI_MODEL = os.environ.get("KIMI_MODEL", "Deepseek/deepseek-flash")

# 网关:一条进程服务全部模式,按路径前缀或 model 字段选择
GATEWAY_HOST = os.environ.get("GATEWAY_HOST", os.environ.get("FACADE_HOST", "0.0.0.0"))
GATEWAY_PORT = int(os.environ.get("GATEWAY_PORT", os.environ.get("FACADE_PORT", "8388")))
DEFAULT_MODE = os.environ.get("DEFAULT_MODE", "anima")
# 管理页/设置接口默认只允许本机访问(局域网里只能生图,不能改 key)
ALLOW_REMOTE_ADMIN = os.environ.get("ALLOW_REMOTE_ADMIN", "0") == "1"

# 后端选择:kimi | dsh(环境变量给默认值,网页里的设置优先)
AGENT_BACKEND = os.environ.get("AGENT_BACKEND", "kimi")

# DSH 一次性任务入口。用 exe + cli.js 直接启动,绕开 dsh.cmd 的引号问题。
DSH_ROOT = Path(os.environ.get("DSH_ROOT", r"D:\DeepSeek Harness"))
DSH_EXE = Path(os.environ.get("DSH_EXE", str(DSH_ROOT / "DeepSeek Harness.exe")))
DSH_CLI = Path(os.environ.get(
    "DSH_CLI",
    str(DSH_ROOT / "resources/app.asar/dsh/node_modules/@deepseek-ai/dsh-desktop-host/lib/cli.js"),
))
# 注意不能用 DSH_PROFILE:那是桌面端自己的环境变量,会把 desktop profile 带进来
DSH_AGENT_PROFILE = os.environ.get("DSH_AGENT_PROFILE", "headless")
DSH_AGENT_MODEL = os.environ.get("DSH_AGENT_MODEL", "deepseek-flash")
DSH_TIMEOUT = float(os.environ.get("DSH_TIMEOUT", "420"))

LOG_DIR = BASE_DIR / "logs"          # 原始请求抓包存放(联调用)
INSTANCE_DIR = BASE_DIR / "instance"  # 本地设置(含 API key),不入库

AGENT_TIMEOUT = float(os.environ.get("AGENT_TIMEOUT", "300"))   # 等 agent 回合结束的最长秒数
POLL_INTERVAL = float(os.environ.get("POLL_INTERVAL", "2"))
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "1"))           # 校验失败后的重试次数


def backend_hint(mode_key: str) -> str | None:
    """环境变量层面的按模式后端覆盖,如 AGENT_BACKEND_MOSS=dsh。"""
    return os.environ.get(f"AGENT_BACKEND_{mode_key.upper().replace('-', '_')}")


def kimi_token() -> str:
    if KIMI_TOKEN:
        return KIMI_TOKEN
    if KIMI_TOKEN_FILE.exists():
        return KIMI_TOKEN_FILE.read_text(encoding="utf-8").strip()
    raise RuntimeError(
        "缺少 kimi web 的 bearer token:设环境变量 KIMI_TOKEN,或先运行一次 kimi web 生成 token"
    )
