"""ST 输出契约硬校验与渲染:<images><image>…regex:…image###tags###…</image></images>。

与网页端契约(<anchor>/<prompt>)完全隔离,本模块只认 ST 格式:
  <images>
  <image>
  regex:正文原句
  image###英文tag###
  </image>
  ...重复 N 个...
  </images>
"""
import re
from dataclasses import dataclass

BLOCK_RE = re.compile(r"<image>(.*?)</image>", re.DOTALL)
ANCHOR_RE = re.compile(r"regex[:：]\s*(.+)")
TAGS_RE = re.compile(r"image###(.*?)###", re.DOTALL)
CJK_RE = re.compile(r"[一-鿿]")
FORBIDDEN_TAGS_RE = re.compile(r"(\*\*|```|negative prompt|<anchor>|</|【|】)", re.IGNORECASE)


@dataclass
class STBlock:
    anchor: str
    tags: str


def parse_blocks(text: str) -> list[STBlock]:
    blocks: list[STBlock] = []
    for m in BLOCK_RE.finditer(text):
        inner = m.group(1)
        am = ANCHOR_RE.search(inner)
        tm = TAGS_RE.search(inner)
        blocks.append(STBlock(
            anchor=am.group(1).strip() if am else "",
            tags=" ".join(tm.group(1).split()) if tm else "",
        ))
    return blocks


def validate(blocks: list[STBlock], story: str, expected: int) -> list[str]:
    errors: list[str] = []
    if len(blocks) != expected:
        errors.append(f"<image> 块数 {len(blocks)} != 要求 {expected}")
    seen: set[str] = set()
    for i, b in enumerate(blocks, 1):
        if not b.anchor:
            errors.append(f"第{i}块缺少 regex: 行")
        elif b.anchor in seen:
            errors.append(f"第{i}块 regex 重复: {b.anchor[:20]}...")
        elif b.anchor not in story:
            errors.append(f"第{i}块 regex 未逐字命中素材原文: {b.anchor[:30]}...")
        seen.add(b.anchor)
        if b.anchor and not (8 <= len(b.anchor) <= 30):
            errors.append(f"第{i}块 regex 长度 {len(b.anchor)} 不在 8-30 字范围")
        if not b.tags:
            errors.append(f"第{i}块缺少 image###tags### 行")
        elif CJK_RE.search(b.tags):
            errors.append(f"第{i}块 tags 含中文")
        elif FORBIDDEN_TAGS_RE.search(b.tags):
            errors.append(f"第{i}块 tags 含禁用内容(markdown/xml 标签等)")
    positions = [story.find(b.anchor) for b in blocks if b.anchor and b.anchor in story]
    if positions != sorted(positions):
        errors.append("regex 未按剧情顺序排列")
    return errors


def render(blocks: list[STBlock]) -> str:
    inner = "\n\n".join(
        f"<image>\nregex:{b.anchor}\nimage###{b.tags}###\n</image>" for b in blocks
    )
    return f"<images>\n{inner}\n</images>"
