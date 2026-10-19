"""SillyTavern 请求提取。

预设(ComfyUI Agent生图)把每段素材放进独立标签、各自一条消息,直接按标签取:

    <生图数量> 2 </生图数量>
    <世界书条目> … </世界书条目>
    <可用绘图角色列表> … </可用绘图角色列表>
    <历史前文> … </历史前文>
    <剧情原文> … </剧情原文>
    <用户需求> … </用户需求>

旧预设的 `{@setvar::生图数量::3-4@}` / 「至少N张」仍作兜底。
"""
import json
import re
import time
from dataclasses import dataclass

from . import config

STORY = "剧情原文"
USER_REQUEST = "用户需求"
CHARACTERS = "可用绘图角色列表"
HISTORY = "历史前文"
WORLDBOOK = "世界书条目"
COUNT = "生图数量"

DEFAULT_IMAGE_COUNT = 2
SETVAR_RE = re.compile(r"\{@setvar::生图数量::([\d\-~～]+)@\}")
COUNT_RES = [
    re.compile(r"至少\s*(\d+)\s*张"),
    re.compile(r"(\d+)\s*[-~～]\s*(\d+)\s*张"),
    re.compile(r"(\d+)\s*张"),
]
UNRENDERED_RE = re.compile(r"\{\{正文\}\}")
MACRO_ONLY_RE = re.compile(r"^\{\{[^{}]*\}\}$")

# 酒馆正文/历史中常注入的思维链与摘要块,对生图素材隐藏
HIDDEN_BLOCK_RE = re.compile(
    r"<(think|thinking|update|summary)\b[^>]*>.*?</\1\s*>",
    re.IGNORECASE | re.DOTALL,
)
HIDDEN_OPEN_RE = re.compile(
    r"<(think|thinking|update|summary)\b[^>]*>.*$",
    re.IGNORECASE | re.DOTALL,
)


@dataclass
class STInput:
    story: str         # 最新剧情原文(regex 校验基准)
    user_request: str  # 用户需求(可空)
    characters: str    # <可用绘图角色列表>(可空,角色 DNA/外观锚点)
    history: str       # <历史前文>(可空,聊天历史)
    worldbook: str     # <世界书条目>(可空)
    image_count: int


def _strip_hidden(text: str) -> str:
    """剥离 <think>/<thinking>/<update>/<summary> 包裹的内容;未闭合时剥到末尾(流式截断)。"""
    text = HIDDEN_BLOCK_RE.sub("", text)
    return HIDDEN_OPEN_RE.sub("", text).strip()


def _dump_request(body: dict) -> None:
    try:
        config.LOG_DIR.mkdir(parents=True, exist_ok=True)
        path = config.LOG_DIR / f"st-{int(time.time())}.json"
        path.write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass  # 落盘失败不影响主流程


def _iter_texts(body: dict):
    for msg in body.get("input") or body.get("messages") or []:
        content = msg.get("content") if isinstance(msg, dict) else None
        if isinstance(content, list):
            content = "".join(p.get("text", "") for p in content if isinstance(p, dict))
        if isinstance(content, str):
            yield content


def _tag_content(texts: list[str], tag: str) -> str:
    """取第一个命中的标签内容;没有闭合标签时取到该条消息末尾。"""
    open_tag, close_tag = f"<{tag}>", f"</{tag}>"
    for text in texts:
        start = text.find(open_tag)
        if start < 0:
            continue
        start += len(open_tag)
        end = text.find(close_tag, start)
        content = text[start:end if end >= 0 else len(text)].strip()
        return "" if MACRO_ONLY_RE.match(content) else content
    return ""


def _parse_count(texts: list[str]) -> int | None:
    raw = _tag_content(texts, COUNT)
    if raw:
        nums = re.findall(r"\d+", raw)
        if nums:
            return int(nums[0])  # 区间取下限(速度优先)
    for text in texts:
        match = SETVAR_RE.search(text)
        if match:
            nums = re.findall(r"\d+", match.group(1))
            if nums:
                return int(nums[0])
        for pattern in COUNT_RES:
            match = pattern.search(text)
            if match:
                return int(match.group(1))
    return None


def extract(body: dict) -> STInput:
    _dump_request(body)
    texts = list(_iter_texts(body))
    if not texts:
        raise ValueError("messages 中没有可用文本内容")
    if any(UNRENDERED_RE.search(t) for t in texts):
        raise ValueError("插件宏未渲染:请求中仍含 {{正文}},请检查插件变量替换")

    story = _strip_hidden(_tag_content(texts, STORY))
    if not story:  # 兜底:无预设标记时取最长消息(手动测试/其他预设)
        story = _strip_hidden(max(texts, key=len))

    image_count = _parse_count(texts)
    if image_count is None or not (1 <= image_count <= 6):
        image_count = DEFAULT_IMAGE_COUNT

    return STInput(
        story=story,
        user_request=_tag_content(texts, USER_REQUEST),
        characters=_tag_content(texts, CHARACTERS),
        history=_strip_hidden(_tag_content(texts, HISTORY)),
        worldbook=_strip_hidden(_tag_content(texts, WORLDBOOK)),
        image_count=image_count,
    )


def build_skill_args(si: STInput) -> str:
    """组装传给技能 args,与 SKILL.md 输入契约一致(历史与世界书合并成一段背景)。"""
    parts = []
    if si.characters:
        parts.append("[可用绘图角色列表]\n" + si.characters)
    background = "\n\n".join(x for x in (si.history, si.worldbook) if x)
    if background:
        parts.append("[历史前文与世界书]\n" + background)
    parts.append("[剧情与设定素材]\n" + si.story)
    if si.user_request:
        parts.append("[用户需求]\n" + si.user_request)
    parts.append(f"[图片数量 N]\n{si.image_count}")
    return "\n\n".join(parts)
