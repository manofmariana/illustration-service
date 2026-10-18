"""MOSS-Image caption 分支的输出契约校验。

五子标签结构与 Anima 版一致,差别全在 <prompts>:
Anima 要 danbooru tag 串,MOSS 要英文单段散文 caption(官方 Prompt Enhancer 规格)。
所以这里额外拦三类会让下游出问题的东西:
  - 质量词/权重/下划线 tag —— 官方明确不要,且会污染 caption 风格
  - 换行、全角括号、$ 与保留字符 —— st-chatu8 的后处理会改坏
  - 按逗号分段重复 —— deduplicateTags 会静默删掉重复段
"""
import re

from .st_validator import CJK_RE, VALID_SIZES, parse_blocks, STBlock

WORD_RANGE = (60, 260)

QUALITY_RE = re.compile(
    r"\b(masterpiece|best quality|high quality|amazing quality|good quality|"
    r"very aesthetic|absurdres|highres|lowres|score_\d+|"
    r"8k|4k|uhd|highly detailed|ultra detailed|extremely detailed|"
    r"official art|artist name)\b",
    re.IGNORECASE,
)
WEIGHT_RE = re.compile(
    r"\(\s*[^()]{1,60}?\s*:\s*\d+(?:\.\d+)?\s*\)"   # (tag:1.2)
    r"|\[\s*[^\[\]]{1,40}?\s*:\s*\d+(?:\.\d+)?\s*\]"  # [tag:0.8]
    r"|\b[\w' -]{1,40}::\s*\d+(?:\.\d+)?",            # tag::2
)
FORBIDDEN_CHAR_RE = re.compile(r"(\*\*|```|`|<[a-zA-Z/][^>]*>|【|】|sāfe|\$)|\u00a6")
FULLWIDTH_BRACKET_RE = re.compile(r"[（）〔〕［］｛｝]")
SCENE_COMPOSITION_RE = re.compile(r"scene\s+composition", re.IGNORECASE)
UNDERSCORE_TAG_RE = re.compile(r"\b[a-z0-9]+(?:_[a-z0-9]+)+\b")
QUOTED_RE = re.compile(r"\"[^\"]*\"|\u201c[^\u201d]*\u201d")
LIGHT_RE = re.compile(
    r"\b(light|lights|lit|lighting|glow|glowing|sunlight|moonlight|daylight|"
    r"lamp|lamp light|neon|candle|candlelight|torchlight|fluorescent|tungsten|"
    r"shadow|shadows|backlit|rim light|silhouette|beam|beams|ray|rays|"
    r"dusk|dawn|twilight|sunset|sunrise|overcast|illuminated|illumination|"
    r"cast|casting|gleam|glimmer|flare|haze|mist)\b",
    re.IGNORECASE,
)

BASE_TAG_RULES = (
    (re.compile(r"^[\(\[\{<]+"), ""),
    (re.compile(r"[\)\]\}>]+$"), ""),
    (re.compile(r"^[\d.]+::"), ""),
    (re.compile(r"::$"), ""),
    (re.compile(r":(?:\d*\.\d+|\d+)$"), ""),
)


def _base_tag(tag: str) -> str:
    """复刻 st-chatu8 的 getBaseTag,用于预判分段去重会不会误删。"""
    base = tag.lower()
    prev = None
    while base != prev:
        prev = base
        for pattern, repl in BASE_TAG_RULES:
            base = pattern.sub(repl, base)
        base = base.strip()
    return base


def dedupe_collisions(prompt: str) -> list[str]:
    """返回会被下游去重删掉的重复分段(空列表表示安全)。"""
    seen: dict[str, str] = {}
    dropped: list[str] = []
    for raw in prompt.split(","):
        segment = raw.strip()
        if not segment:
            continue
        base = _base_tag(segment)
        if base in seen:
            dropped.append(segment)
        else:
            seen[base] = segment
    return dropped


def _word_count(text: str) -> int:
    return len([w for w in re.split(r"\s+", text.strip()) if w])


def _validate_prompt(prompt: str, index: int) -> list[str]:
    errors: list[str] = []
    tag = f"第{index}块"
    if not prompt:
        return [f"{tag}缺少 <prompts>"]
    # 换行在 parse_blocks 里已被压成空格(下游会把换行变成逗号),这里不再重复拦。
    words = _word_count(prompt)
    if not (WORD_RANGE[0] <= words <= WORD_RANGE[1]):
        errors.append(f"{tag} caption 词数 {words} 不在 {WORD_RANGE[0]}-{WORD_RANGE[1]} 区间")

    outside_quotes = QUOTED_RE.sub("", prompt)
    if CJK_RE.search(outside_quotes):
        errors.append(f"{tag} caption 主体必须是英文(引号内的画面文字除外)")
    if QUALITY_RE.search(prompt):
        errors.append(f"{tag} caption 含质量词: {QUALITY_RE.search(prompt).group(0)!r}")
    if WEIGHT_RE.search(prompt):
        errors.append(f"{tag} caption 含权重语法")
    pipe = FORBIDDEN_CHAR_RE.search(prompt)
    if pipe:
        errors.append(f"{tag} caption 含禁字符 {pipe.group(0)!r}")
    if FULLWIDTH_BRACKET_RE.search(prompt):
        errors.append(f"{tag} caption 含全角括号(下游会连同内容删除)")
    if SCENE_COMPOSITION_RE.search(prompt):
        errors.append(f"{tag} caption 含 'Scene Composition'(会触发插件分角色模式)")
    underscores = UNDERSCORE_TAG_RE.findall(prompt)
    if len(underscores) >= 3:
        errors.append(f"{tag} 出现 {len(underscores)} 个下划线 tag,看起来仍是 tag 串: {underscores[:3]}")
    if not LIGHT_RE.search(prompt):
        errors.append(f"{tag} caption 缺少光影描写")
    collisions = dedupe_collisions(prompt)
    if collisions:
        errors.append(f"{tag} caption 有重复分段会被下游静默删除: {collisions[:2]}")
    return errors


def validate(blocks: list[STBlock], story: str, expected: int) -> list[str]:
    errors: list[str] = []
    if len(blocks) != expected:
        errors.append(f"<image> 块数 {len(blocks)} != 要求 {expected}")
    seen: set[str] = set()
    for i, b in enumerate(blocks, 1):
        if not b.regex:
            errors.append(f"第{i}块缺少 <regex>")
        else:
            if b.regex in seen:
                errors.append(f"第{i}块 regex 重复: {b.regex[:20]}...")
            if b.regex not in story:
                errors.append(f"第{i}块 regex 未逐字命中剧情原文: {b.regex[:30]}...")
            if not (5 <= len(b.regex) <= 60):
                errors.append(f"第{i}块 regex 长度 {len(b.regex)} 不在 5-60 字范围")
        seen.add(b.regex)
        if not b.title:
            errors.append(f"第{i}块缺少 <title_styled>")
        elif not (4 <= len(b.title) <= 20):
            errors.append(f"第{i}块 title 长度 {len(b.title)} 异常(要求约5-15字)")
        if not b.think:
            errors.append(f"第{i}块缺少 <Tag_think>")
        elif not (20 <= len(b.think) <= 160):
            errors.append(f"第{i}块 Tag_think 长度 {len(b.think)} 异常(要求约60-100字)")
        if b.size not in VALID_SIZES:
            errors.append(f"第{i}块 size 非法: {b.size!r}(须为 {sorted(VALID_SIZES)})")
        errors.extend(_validate_prompt(b.prompts, i))
    positions = [story.find(b.regex) for b in blocks if b.regex and b.regex in story]
    if positions != sorted(positions):
        errors.append("regex 未按剧情顺序排列")
    return errors


def render(blocks: list[STBlock]) -> str:
    """caption 原样输出:不做下划线替换(MOSS 读的是自然英语)。"""
    inner = "\n\n".join(
        "<image>\n"
        f"<regex>{b.regex}</regex>\n"
        f"<title_styled>{b.title}</title_styled>\n"
        f"<Tag_think>{b.think}</Tag_think>\n"
        f"<size>{b.size}</size>\n"
        f"<prompts>{b.prompts}</prompts>\n"
        "</image>"
        for b in blocks
    )
    return f"<images>\n{inner}\n</images>"
