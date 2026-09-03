"""清理本项目的 kimi 归档会话:扫描 ~/.kimi-code/sessions/wd_illustration-service_*/,
删除 state.json 中 archived=true 的 session_* 目录。只动本项目工作区,不影响其他会话。
用法: ../python_embeded/python.exe clean_archived_sessions.py [--dry-run]
"""
import json
import shutil
import sys
from pathlib import Path

SESSIONS_ROOT = Path.home() / ".kimi-code" / "sessions"


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    targets = sorted(SESSIONS_ROOT.glob("wd_illustration-service_*/session_*"))
    removed = skipped = 0
    for sess in targets:
        state = sess / "state.json"
        archived = False
        try:
            archived = bool(json.loads(state.read_text(encoding="utf-8")).get("archived"))
        except Exception:
            pass
        if not archived:
            skipped += 1
            print(f"[跳过] {sess.name}(未归档)")
            continue
        if dry_run:
            print(f"[待删] {sess.name}")
        else:
            shutil.rmtree(sess, ignore_errors=True)
            print(f"[已删] {sess.name}")
        removed += 1
    print(f"\n归档会话 {removed} 个{'(未执行,去掉 --dry-run 生效)' if dry_run else '已清理'},跳过未归档 {skipped} 个")


if __name__ == "__main__":
    main()
