"""从网页端 Responses API 请求体中切分出 agent 需要的四段素材。

网页请求 input 是消息数组;有效载荷在含「在场角色完整外观资料」的那条 user 消息里,
由固定模板组装,锚点稳定:
  在场角色完整外观资料：... 场景信息：... 当前正文：... 当前正文生图模式：xxx
  ... 任务：固定输出 N 个 <image> ...
"""
import re
from dataclasses import dataclass

CHARS_ANCHOR = "在场角色完整外观资料"
SCENE_ANCHOR = "场景信息"
STORY_ANCHOR = "当前正文"
STORY_END_ANCHOR = "当前正文生图模式"
COUNT_RE = re.compile(r"固定输出\s*(\d+)\s*个")


@dataclass
class StoryInput:
    characters: str   # 在场角色完整外观资料
    scene: str        # 场景信息
    story: str        # 当前正文(原文,anchor 校验以此为基准)
    image_count: int  # 需要输出的 <image> 块数


def _slice(text: str, start: str, end: str | None) -> str:
    i = text.find(start)
    if i < 0:
        raise ValueError(f"锚点缺失: {start}")
    i += len(start)
    # 跳过锚点后紧跟的冒号(中文/英文)
    if i < len(text) and text[i] in "：:":
        i += 1
    j = text.find(end, i) if end else len(text)
    if j < 0:
        raise ValueError(f"锚点缺失: {end}")
    return text[i:j].strip()


def extract(body: dict) -> StoryInput:
    """从请求体提取素材,兼容 Responses API(input)与 Chat Completions API(messages)。
    找不到有效载荷时抛 ValueError。"""
    messages = body.get("input") or body.get("messages") or []
    payload = None
    for msg in messages:
        content = msg.get("content")
        if isinstance(content, list):  # 两种 API 都允许 content 分块
            content = "".join(p.get("text", "") for p in content if isinstance(p, dict))
        if isinstance(content, str) and CHARS_ANCHOR in content and STORY_ANCHOR in content:
            # 多条命中时取最长者(固定注入的自检消息也会同时含两个锚点,但体量小)
            if payload is None or len(content) > len(payload):
                payload = content
    if payload is None:
        raise ValueError("input/messages 中未找到含「在场角色完整外观资料」的消息")

    characters = _slice(payload, CHARS_ANCHOR, SCENE_ANCHOR)
    scene = _slice(payload, SCENE_ANCHOR, STORY_ANCHOR)
    story = _slice(payload, STORY_ANCHOR, STORY_END_ANCHOR)

    m = COUNT_RE.search(payload)
    if not m:
        raise ValueError("无法从请求中解析图片数量(缺少「固定输出 N 个」)")
    image_count = int(m.group(1))
    if image_count <= 0:
        raise ValueError(f"图片数量非法: {image_count}")

    return StoryInput(characters=characters, scene=scene, story=story, image_count=image_count)


def build_skill_args(si: StoryInput) -> str:
    """组装传给 story-illustrator-frz 技能的 args,顺序与 SKILL.md 输入契约一致。"""
    return (
        "[在场角色完整外观资料]\n" + si.characters + "\n\n"
        "[场景信息]\n" + si.scene + "\n\n"
        "[当前正文]\n" + si.story + "\n\n"
        f"[图片数量 N]\n{si.image_count}"
    )
