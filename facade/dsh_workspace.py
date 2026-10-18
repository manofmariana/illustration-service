"""把 headless 跑出来的 DSH 会话登记到对应工作区,免得在 Desktop 里落到「未分组」。

DSH 的会话目录按 cwd 命名(`--D-ComfyUI_windows_portable-illustration-service--`),
而 Desktop 的分组看 `storages/workspace.json` 里的 sessionIds;headless 不会登记,
所以它的会话会落在「未分组」。这里在每次运行后补一次登记。

写的是另一个程序的状态文件,所以:只改名册、读回再写、原子替换、可用环境变量关掉。
"""
import json
import os
from pathlib import Path

from . import config

SESSIONS_DIR = Path.home() / ".dsh" / "sessions"
WORKSPACE_STORE = Path.home() / ".dsh" / "storages" / "workspace.json"


def enabled() -> bool:
    return os.environ.get("DSH_LINK_WORKSPACE", "1") != "0"


def cwd_key(path: Path) -> str:
    """复刻 DSH 的会话目录命名:冒号去掉,分隔符变 -,空格变 ~0020,外层包 --。"""
    raw = str(path.resolve())
    raw = raw.replace(":", "").replace("\\", "-").replace("/", "-").replace(" ", "~0020")
    return f"--{raw}--"


def local_session_ids(base: Path) -> list[str]:
    folder = SESSIONS_DIR / cwd_key(base)
    if not folder.is_dir():
        return []
    return sorted(p.name for p in folder.iterdir() if p.is_dir() and p.name.startswith("session-"))


def link(base: Path = config.BASE_DIR) -> int:
    """把该工作目录下的会话补登记进对应工作区,返回新登记的数量。"""
    if not enabled() or not WORKSPACE_STORE.exists():
        return 0
    try:
        data = json.loads(WORKSPACE_STORE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return 0

    workspaces = data.get("tables", {}).get("workspaces", {})
    target = str(base.resolve()).rstrip("\\/").lower()
    entry = next(
        (w for w in workspaces.values() if str(w.get("path", "")).rstrip("\\/").lower() == target),
        None,
    )
    if entry is None:
        return 0

    existing = list(entry.get("sessionIds") or [])
    known = set(existing)
    missing = [sid for sid in local_session_ids(base) if sid not in known]
    if not missing:
        return 0

    entry["sessionIds"] = existing + missing
    try:
        tmp = WORKSPACE_STORE.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, WORKSPACE_STORE)
    except OSError:
        return 0
    return len(missing)
