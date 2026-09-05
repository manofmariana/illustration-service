"""SillyTavern 插件请求提取(暂定策略,待真实抓包后细化)。

ST 侧没有网页端那样的固定锚点模板,注入内容由插件模板决定(通常是
角色卡 + 世界书 + 最近若干楼对话 + 生图指令,混在 messages 里)。
暂定策略:
  1. 原始请求体落盘 logs/st/(联调期保留,方便按真实格式细化)
  2. 取 input/messages 中最长的一条文本作为「剧情与设定素材」
  3. 图片数量从常见表述中解析(固定输出 N 个 / N 张 / 生成 N),默认 1
"""
import json
import re
import time
from dataclasses import dataclass

from . import config

COUNT_RES = [
    re.compile(r"固定输出\s*(\d+)\s*个"),
    re.compile(r"(\d+)\s*张"),
    re.compile(r"生成\s*(\d+)"),
    re.compile(r"输出\s*(\d+)\s*个"),
    re.compile(r"<\s*image\s*>?\s*[x×*]?\s*(\d+)", re.IGNORECASE),
]


@dataclass
class STInput:
    material: str     # 剧情与设定素材(角色/场景/正文混合,由 skill 自建台账)
    image_count: int


def _dump_request(body: dict) -> None:
    try:
        config.LOG_DIR.mkdir(parents=True, exist_ok=True)
        path = config.LOG_DIR / f"st-{int(time.time())}.json"
        path.write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass  # 落盘失败不影响主流程


def extract(body: dict) -> STInput:
    _dump_request(body)
    messages = body.get("input") or body.get("messages") or []
    best = ""
    for msg in messages:
        content = msg.get("content") if isinstance(msg, dict) else None
        if isinstance(content, list):
            content = "".join(p.get("text", "") for p in content if isinstance(p, dict))
        if isinstance(content, str) and len(content) > len(best):
            best = content
    if not best.strip():
        raise ValueError("messages 中没有可用文本内容")

    image_count = 1
    for rx in COUNT_RES:
        m = rx.search(best)
        if m and 0 < int(m.group(1)) <= 6:
            image_count = int(m.group(1))
            break
    return STInput(material=best.strip(), image_count=image_count)


def build_skill_args(si: STInput) -> str:
    """组装传给 story-illustrator-st 的 args,与 ST 技能输入契约一致。"""
    return (
        "[剧情与设定素材]\n" + si.material + "\n\n"
        f"[图片数量 N]\n{si.image_count}"
    )
