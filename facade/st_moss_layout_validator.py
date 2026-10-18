"""MOSS-Image Layout 分支的输出契约校验。

与 caption 版共用 <regex>/<title_styled>/<Tag_think>/<size> 四个子标签,
第五个是 <layout>(草稿 JSON)而不是 <prompts>。校验通过后由本模块把它编译成
模型侧布局 prompt、做逗号转义,再渲染成客户端真正需要的 <prompts>。
"""
import json
import re
from dataclasses import dataclass

from . import moss_layout
from .st_validator import BLOCK_RE, CJK_RE

LAYOUT_RE = re.compile(r"<layout>(.*?)</layout>", re.DOTALL)
SIZE_RE = re.compile(r"<regex>(.*?)</regex>", re.DOTALL)
TITLE_RE = re.compile(r"<title_styled>(.*?)</title_styled>", re.DOTALL)
THINK_RE = re.compile(r"<Tag_think>(.*?)</Tag_think>", re.DOTALL)
SIZE_TAG_RE = re.compile(r"<size>(.*?)</size>", re.DOTALL)

# 官方只要求 16 的正整数倍、总像素 1M/1.5M/2M 为佳(可外推 0.25M~4M),
# 所以这里不锁死尺寸档位,只锁格式、16 倍数与像素区间。
SIZE_PATTERN = re.compile(r"^(\d{2,4})x(\d{2,4})$")
PIXEL_RANGE = (800_000, 2_200_000)


@dataclass
class LayoutBlock:
    regex: str
    title: str
    think: str
    size: str
    draft: dict | None
    layout_raw: str


def _sub(pattern, inner: str) -> str:
    match = pattern.search(inner)
    return match.group(1).strip() if match else ""


def parse_blocks(text: str) -> list[LayoutBlock]:
    blocks: list[LayoutBlock] = []
    for match in BLOCK_RE.finditer(text):
        inner = match.group(1)
        raw = _sub(LAYOUT_RE, inner)
        draft: dict | None = None
        if raw:
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    draft = parsed
            except json.JSONDecodeError:
                draft = None
        blocks.append(LayoutBlock(
            regex=_sub(SIZE_RE, inner),
            title=_sub(TITLE_RE, inner),
            think=_sub(THINK_RE, inner),
            size=_sub(SIZE_TAG_RE, inner),
            draft=draft,
            layout_raw=raw,
        ))
    return blocks


def _validate_common(block: LayoutBlock, index: int, story: str, seen: set[str]) -> list[str]:
    errors: list[str] = []
    tag = f"第{index}块"
    if not block.regex:
        errors.append(f"{tag}缺少 <regex>")
    else:
        if block.regex in seen:
            errors.append(f"{tag} regex 重复: {block.regex[:20]}...")
        if block.regex not in story:
            errors.append(f"{tag} regex 未逐字命中剧情原文: {block.regex[:30]}...")
        if not (5 <= len(block.regex) <= 60):
            errors.append(f"{tag} regex 长度 {len(block.regex)} 不在 5-60 字范围")
    if not block.title:
        errors.append(f"{tag}缺少 <title_styled>")
    elif not (4 <= len(block.title) <= 20):
        errors.append(f"{tag} title 长度 {len(block.title)} 异常(要求约5-15字)")
    if not block.think:
        errors.append(f"{tag}缺少 <Tag_think>")
    elif not (20 <= len(block.think) <= 160):
        errors.append(f"{tag} Tag_think 长度 {len(block.think)} 异常(要求约60-100字)")
    if not SIZE_PATTERN.match(block.size):
        errors.append(f"{tag} size 格式非法: {block.size!r}(须为 <宽>x<高>,如 1024x1536)")
    return errors


def _validate_layout(block: LayoutBlock, index: int) -> list[str]:
    tag = f"第{index}块"
    if not block.layout_raw:
        return [f"{tag}缺少 <layout>"]
    if block.draft is None:
        return [f"{tag} <layout> 不是合法 JSON 对象"]
    draft = block.draft
    try:
        compiled = moss_layout.compile_draft(draft)
    except moss_layout.LayoutError as e:
        return [f"{tag} 布局草稿非法: {e}"]

    errors: list[str] = []
    width, height = draft.get("width"), draft.get("height")
    expected_size = f"{width}x{height}"
    if block.size != expected_size:
        errors.append(f"{tag} <size> {block.size} 与布局画布 {expected_size} 不一致")
    if isinstance(width, int) and isinstance(height, int):
        pixels = width * height
        if not (PIXEL_RANGE[0] <= pixels <= PIXEL_RANGE[1]):
            errors.append(f"{tag} 画布 {pixels} 像素超出建议区间 {PIXEL_RANGE[0]}-{PIXEL_RANGE[1]}")
    items = draft.get("items") or []
    if not (3 <= len(items) <= 12):
        errors.append(f"{tag} 元素框数量 {len(items)} 不在 3-12 之间")
    summary = draft.get("summary") or {}
    caption = str(summary.get("caption", ""))
    if CJK_RE.search(caption):
        errors.append(f"{tag} summary.caption 必须是英文")
    errors.extend(_validate_transport(compiled, tag))
    return errors


def _validate_transport(compiled: str, tag: str) -> list[str]:
    """预演一遍转义+回转,确保送到插件手里的 JSON 一定能被还原。"""
    try:
        moss_layout.verify_transport(moss_layout.escape_commas(compiled))
    except moss_layout.LayoutError as e:
        return [f"{tag} 布局编译失败: {e}"]
    return []


def validate(blocks: list[LayoutBlock], story: str, expected: int) -> list[str]:
    errors: list[str] = []
    if len(blocks) != expected:
        errors.append(f"<image> 块数 {len(blocks)} != 要求 {expected}")
    seen: set[str] = set()
    for i, block in enumerate(blocks, 1):
        errors.extend(_validate_common(block, i, story, seen))
        seen.add(block.regex)
        errors.extend(_validate_layout(block, i))
    positions = [story.find(b.regex) for b in blocks if b.regex and b.regex in story]
    if positions != sorted(positions):
        errors.append("regex 未按剧情顺序排列")
    return errors


def render(blocks: list[LayoutBlock]) -> str:
    """把草稿编译成 <prompts>。注意:不做下划线替换,abs_centralized 必须原样保留。"""
    parts = []
    for block in blocks:
        payload = moss_layout.compile_for_transport(block.draft or {})
        parts.append(
            "<image>\n"
            f"<regex>{block.regex}</regex>\n"
            f"<title_styled>{block.title}</title_styled>\n"
            f"<Tag_think>{block.think}</Tag_think>\n"
            f"<size>{block.size}</size>\n"
            f"<prompts>{payload}</prompts>\n"
            "</image>"
        )
    return "<images>\n" + "\n\n".join(parts) + "\n</images>"
