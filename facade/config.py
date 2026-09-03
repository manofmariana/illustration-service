"""facade 配置:全部可用环境变量覆盖。"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent          # illustration-service/
SKILL_CWD = str(BASE_DIR)                                  # agent 工作目录(含 .kimi-code/skills)
SKILL_NAME = "story-illustrator"

KIMI_BASE_URL = os.environ.get("KIMI_BASE_URL", "http://127.0.0.1:58627")
KIMI_TOKEN = os.environ.get("KIMI_TOKEN", "")              # 留空则读 ~/.kimi-code/server.token
KIMI_TOKEN_FILE = Path.home() / ".kimi-code" / "server.token"
# kimi config.toml 里配置的模型别名(精确 alias key);留空则用全局 default_model
KIMI_MODEL = os.environ.get("KIMI_MODEL", "Deepseek/deepseek-v4-flash-vision-exp")

FACADE_HOST = os.environ.get("FACADE_HOST", "0.0.0.0")
FACADE_PORT = int(os.environ.get("FACADE_PORT", "8388"))

AGENT_TIMEOUT = float(os.environ.get("AGENT_TIMEOUT", "300"))   # 等 agent 回合结束的最长秒数
POLL_INTERVAL = float(os.environ.get("POLL_INTERVAL", "2"))
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "1"))           # 校验失败后的重试次数


def kimi_token() -> str:
    if KIMI_TOKEN:
        return KIMI_TOKEN
    if KIMI_TOKEN_FILE.exists():
        return KIMI_TOKEN_FILE.read_text(encoding="utf-8").strip()
    raise RuntimeError(
        "缺少 kimi web 的 bearer token:设环境变量 KIMI_TOKEN,或先运行一次 kimi web 生成 token"
    )
