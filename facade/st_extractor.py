"""SillyTavern 插件请求提取(按 st_chatu8_all_test_contexts_new2.json 预设实证)。

预设结构(184 entries × comfyui/nai 两变体,注入位置一致):
  - 剧情正文:某条 user 消息内 `<剧情原文>…<剧情原文>`(作者笔误,闭合标签同形)
  - 用户需求:同一条消息内 `<用户需求>…</用户需求>`
  - 图片数量:entry0 `{@setvar::生图数量::3-4@}`(默认 3-4),或文中「至少N张」
  - 噪声(忽略):<文生图_Tag库>/<文生图_Tag模板库>/{{roll}}/<宇宙法则>/assistant 假确认
  - 隐藏(剥离):正文/历史中注入的 <think>/<thinking>/<update>/<summary> 块
"""
import json
import re
import time
from dataclasses import dataclass

from . import config

STORY_OPEN = "<剧情原文>"
CHARS_OPEN = "<可用绘图角色列表>"
CHARS_CLOSE = "</可用绘图角色列表>"
HIST_OPEN = "<历史前文>"
HIST_CLOSE = "</历史前文>"
NEED_RE = re.compile(r"<用户需求>(.*?)</用户需求>", re.DOTALL)
SETVAR_RE = re.compile(r"\{@setvar::生图数量::([\d\-~～]+)@\}")
COUNT_RES = [
    re.compile(r"至少\s*(\d+)\s*张"),
    re.compile(r"(\d+)\s*[-~～]\s*(\d+)\s*张"),
    re.compile(r"(\d+)\s*张"),
]
UNRENDERED_RE = re.compile(r"\{\{正文\}\}")

# 酒馆正文/历史中常注入的思维链与摘要块,对生图素材隐藏
HIDDEN_BLOCK_RE = re.compile(
    r"<(think|thinking|update|summary)\b[^>]*>.*?</\1\s*>",
    re.IGNORECASE | re.DOTALL,
)
HIDDEN_OPEN_RE = re.compile(
    r"<(think|thinking|update|summary)\b[^>]*>.*$",
    re.IGNORECASE | re.DOTALL,
)


def _strip_hidden(text: str) -> str:
    """剥离 <think>/<thinking>/<update>/<summary> 包裹的内容;未闭合时剥到末尾(流式截断)。"""
    text = HIDDEN_BLOCK_RE.sub("", text)
    return HIDDEN_OPEN_RE.sub("", text).strip()


@dataclass
class STInput:
    story: str         # 最新剧情原文(regex 校验基准)
    user_request: str  # 用户需求(可空)
    characters: str    # <可用绘图角色列表> 内容(可空,角色 DNA/外观锚点)
    history: str       # <历史前文> 内容(可空,聊天历史+世界书条目,仅背景参考)
    image_count: int


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


def _parse_count(text: str) -> int | None:
    m = SETVAR_RE.search(text)
    if m:
        nums = re.findall(r"\d+", m.group(1))
        if nums:
            return int(nums[0])  # 区间取下限(速度优先)
    for rx in COUNT_RES:
        m = rx.search(text)
        if m:
            return int(m.group(1))
    return None


def extract(body: dict) -> STInput:
    _dump_request(body)
    texts = list(_iter_texts(body))
    if not texts:
        raise ValueError("messages 中没有可用文本内容")

    story = user_request = ""
    for t in texts:
        if STORY_OPEN in t:
            if UNRENDERED_RE.search(t):
                raise ValueError("插件宏未渲染:请求中仍含 {{正文}},请检查插件变量替换")
            i = t.find(STORY_OPEN) + len(STORY_OPEN)
            j = t.find(STORY_OPEN, i)  # 闭合标签与开放标签同形(预设笔误),按第二次出现切
            story = _strip_hidden(t[i:j if j > 0 else len(t)])
            m = NEED_RE.search(t)
            if m:
                user_request = m.group(1).strip()
            break

    if not story:  # 兜底:无预设标记时取最长消息(手动测试/其他插件)
        story = _strip_hidden(max(texts, key=len))
        if UNRENDERED_RE.search(story):
            raise ValueError("插件宏未渲染:请求中仍含 {{正文}}")

    characters = ""
    for t in texts:
        if CHARS_OPEN in t:
            i = t.find(CHARS_OPEN) + len(CHARS_OPEN)
            j = t.find(CHARS_CLOSE, i)
            characters = t[i:j if j > 0 else len(t)].strip()
            break

    history = ""
    for t in texts:
        if HIST_OPEN in t:
            i = t.find(HIST_OPEN) + len(HIST_OPEN)
            j = t.find(HIST_CLOSE, i)
            history = _strip_hidden(t[i:j if j > 0 else len(t)])
            if "{{上下文}}" in history and len(history) < 100:
                history = ""  # 宏未渲染且没有实际内容
            break

    image_count = 0
    for t in texts:
        n = _parse_count(t)
        if n:
            image_count = n
            break
    if not (1 <= image_count <= 6):
        image_count = 3  # 预设默认 3-4,取下限

    return STInput(story=story, user_request=user_request,
                   characters=characters, history=history, image_count=image_count)


def build_skill_args(si: STInput) -> str:
    """组装传给 story-illustrator-st 的 args,与 ST 技能输入契约一致。"""
    parts = []
    if si.characters:
        parts.append("[可用绘图角色列表]\n" + si.characters)
    if si.history:
        parts.append("[历史前文与世界书]\n" + si.history)
    parts.append("[剧情与设定素材]\n" + si.story)
    if si.user_request:
        parts.append("[用户需求]\n" + si.user_request)
    parts.append(f"[图片数量 N]\n{si.image_count}")
    return "\n\n".join(parts)
