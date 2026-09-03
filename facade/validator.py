"""<image> 输出块硬校验:数量、anchor 逐字命中、prompt 禁物。"""
import re
from dataclasses import dataclass

BLOCK_RE = re.compile(
    r"<image>\s*<anchor>(.*?)</anchor>\s*<prompt>(.*?)</prompt>\s*</image>",
    re.DOTALL,
)
# 正文中不允许出现在 prompt 里的内容
FORBIDDEN_PROMPT_RE = re.compile(
    r"(\*\*|```|negative prompt|col19|<<<|<anchor>|</|【|】)", re.IGNORECASE
)
CJK_RE = re.compile(r"[一-鿿]")  # prompt 必须全英文
# 人数上限 3:匹配 4girls/5boys 这类显式超员 tag
OVERCROWD_RE = re.compile(r"\b(?:[4-9]|\d{2,})\s*(?:girls?|boys?|guys?|women|men)\b", re.IGNORECASE)


@dataclass
class ImageBlock:
    anchor: str
    prompt: str


def parse_blocks(text: str) -> list[ImageBlock]:
    """从 agent 回复中解析 <image> 块;容忍块外有少量杂质(只取块)。"""
    return [
        ImageBlock(anchor=m.group(1).strip(), prompt=m.group(2).strip())
        for m in BLOCK_RE.finditer(text)
    ]


def validate(blocks: list[ImageBlock], story: str, expected: int) -> list[str]:
    """返回错误列表;空列表 = 通过。"""
    errors: list[str] = []
    if len(blocks) != expected:
        errors.append(f"<image> 块数 {len(blocks)} != 要求 {expected}")
    seen: set[str] = set()
    for i, b in enumerate(blocks, 1):
        if b.anchor in seen:
            errors.append(f"第{i}块 anchor 重复: {b.anchor[:20]}...")
        seen.add(b.anchor)
        if b.anchor not in story:
            errors.append(f"第{i}块 anchor 未逐字命中正文: {b.anchor[:30]}...")
        if not (8 <= len(b.anchor) <= 30):
            errors.append(f"第{i}块 anchor 长度 {len(b.anchor)} 不在 8-30 字范围")
        if not b.prompt:
            errors.append(f"第{i}块 prompt 为空")
        if CJK_RE.search(b.prompt):
            errors.append(f"第{i}块 prompt 含中文(角色姓名/ID 不得出现在 prompt)")
        if FORBIDDEN_PROMPT_RE.search(b.prompt):
            errors.append(f"第{i}块 prompt 含禁用内容(markdown/权重/col19 等)")
        if OVERCROWD_RE.search(b.prompt):
            errors.append(f"第{i}块 prompt 人数超过 3 人上限(含 4girls/5boys 类 tag)")
    # anchor 应按剧情顺序:在正文中的位置递增
    positions = [story.find(b.anchor) for b in blocks if b.anchor in story]
    if positions != sorted(positions):
        errors.append("anchor 未按剧情顺序排列")
    return errors


def render(blocks: list[ImageBlock]) -> str:
    """校验通过后渲染为最终返回文本(网页端契约格式)。"""
    return "\n\n".join(
        f"<image>\n<anchor>{b.anchor}</anchor>\n<prompt>{b.prompt}</prompt>\n</image>"
        for b in blocks
    )
