"""运行时设置:DSH API key、各模式后端、默认模式。

敏感项只写 `instance/settings.json`(已在 .gitignore 里),不进仓库、不回显。
环境变量作为兜底,方便容器或 CI 部署。
"""
import json
import os

from . import config

DEFAULTS = {
    "default_mode": config.DEFAULT_MODE,
    "backends": {},
    "dsh_api_key": "",
    "dsh_model": config.DSH_AGENT_MODEL,
}


def _path():
    return config.INSTANCE_DIR / "settings.json"


def load() -> dict:
    data = dict(DEFAULTS)
    try:
        raw = json.loads(_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raw = {}
    if isinstance(raw, dict):
        for key in DEFAULTS:
            if key in raw:
                data[key] = raw[key]
    if not isinstance(data.get("backends"), dict):
        data["backends"] = {}
    return data


def save(patch: dict) -> dict:
    data = load()
    for key, value in patch.items():
        if key in DEFAULTS:
            data[key] = value
    if not isinstance(data["backends"], dict):
        data["backends"] = {}
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return data


def dsh_api_key() -> str:
    """网页保存的 key 优先,其次环境变量。"""
    key = str(load().get("dsh_api_key") or "").strip()
    return key or os.environ.get("DEEPSEEK_API_KEY", "").strip()


def masked(key: str) -> str:
    if not key:
        return ""
    if len(key) <= 8:
        return "*" * len(key)
    return f"{key[:3]}…{key[-4:]}"
