"""MOSS 分支离线自测:不启动 kimi,只跑校验、编译与酒馆插件的去重预演。

    ..\\python_embeded\\python.exe -m facade.moss_selftest

`_plugin_dedupe` / `_plugin_pipeline` 是智绘姬(st-chatu8)后处理的复刻。
插件升级后需要人工对照它源码里的 deduplicateTags、processCharacterPrompt、
sizeRegex、parsePromptsContent 是否还和自己一致,这里不会自动发现。
"""
import json
import re
import sys

from . import moss_layout, st_moss_layout_validator, st_moss_validator

STORY = (
    "她把杯子推到窗台边,玻璃上的水汽被手指抹出一道痕。"
    "窗外的霓虹在雨里晕开,映得她侧脸发青。"
    "手机屏幕亮起来,上面只有两个字。"
)


def _caption_block(regex: str, prompt: str) -> str:
    return (
        "<image>\n"
        f"<regex>{regex}</regex>\n"
        "<title_styled>窗边的人</title_styled>\n"
        "<Tag_think>夜雨敲窗，人影独立，霓虹映面而生寒，杯沿余温未散。</Tag_think>\n"
        "<size>1024x1536</size>\n"
        f"<prompts>{prompt}</prompts>\n"
        "</image>"
    )


GOOD_CAPTION = (
    "A quiet illustration of a young woman leaning by a rain-streaked window at night, "
    "seen from the side in a medium shot. She has straight black hair falling past her "
    "shoulders and pale skin, wearing an oversized cream knit sweater whose sleeves are "
    "pulled over her palms. One fingertip has wiped a clear streak through the condensation "
    "on the glass, and a half-finished cup of tea sits on the sill beside her hand. Outside, "
    "neon signs dissolve into the wet street, and the light bleeding through the water "
    "paints a cold cyan edge along her cheek while the room behind her stays in warm dim "
    "tungsten shadow. A phone lights up in her other hand, its screen displaying the words "
    "\"别走\" in plain white type."
)


def _check_caption() -> list[str]:
    failures: list[str] = []
    text = f"<images>{_caption_block('她把杯子推到窗台边', GOOD_CAPTION)}</images>"
    blocks = st_moss_validator.parse_blocks(text)
    errors = st_moss_validator.validate(blocks, STORY, 1)
    if errors:
        failures.append(f"合格 caption 被误判: {errors}")

    bad_cases = {
        "tag 串": "1girl, solo, black hair, blue eyes, window, night, cinematic lighting, "
                  "masterpiece, best quality",
        "中文主语": "一位黑发少女站在窗边看着雨，霓虹映在她的脸上，房间里有暖色的灯光。",
        "权重语法": GOOD_CAPTION.replace("pale skin", "(pale skin:1.3)"),
        "缺光影": (
            "The woman stands beside the window holding a cup. She wears a cream sweater and "
            "looks toward the glass. Rain runs down the pane in long streaks, and the street "
            "beyond is crowded with passing cars and bright shop signs. Her phone rests in her "
            "other hand, showing two characters on a white screen. The room around her is plain, "
            "with a table, a chair, and a folded towel on the sill near her wrist. Nothing else "
            "moves in the frame."
        ),
    }
    for name, prompt in bad_cases.items():
        blocks = st_moss_validator.parse_blocks(
            f"<images>{_caption_block('她把杯子推到窗台边', prompt)}</images>")
        errors = st_moss_validator.validate(blocks, STORY, 1)
        if not errors:
            failures.append(f"非法 caption 未被拦下: {name}")

    wrapped = GOOD_CAPTION.replace("She has", "She has\nand", 1)
    blocks = st_moss_validator.parse_blocks(
        f"<images>{_caption_block('她把杯子推到窗台边', wrapped)}</images>")
    if "\n" in blocks[0].prompts:
        failures.append("caption 里的换行没有被压成空格")
    return failures


def _layout_draft() -> dict:
    return {
        "width": 1024,
        "height": 1536,
        "bbox_coord_space": "abs",
        "bbox_format": "xyxy",
        "summary": {
            "meta": ["illustration"],
            "canvas": "single",
            "caption": "A rain-soaked night interior with a woman by the window and a lit phone screen.",
        },
        "items": [
            {"label": "character", "caption": "A young woman in a cream sweater, seen in profile.",
             "bbox": [180, 260, 640, 1180]},
            {"label": "object", "caption": "A tea cup on the sill, steam barely visible.",
             "bbox": [660, 1020, 880, 1180]},
            {"label": "text", "caption": "Small white interface text on a glowing phone screen.",
             "text": "别走", "bbox": [640, 640, 940, 760]},
        ],
    }


def _layout_block(draft: dict, size: str | None = None) -> str:
    size = size or f"{draft['width']}x{draft['height']}"
    return (
        "<image>\n"
        "<regex>手机屏幕亮起来</regex>\n"
        "<title_styled>屏幕上两个字</title_styled>\n"
        "<Tag_think>屏光映掌，二字在目，雨声不闻，唯余此念。</Tag_think>\n"
        f"<size>{size}</size>\n"
        f"<layout>{json.dumps(draft, ensure_ascii=False)}</layout>\n"
        "</image>"
    )


def _plugin_dedupe(prompt: str) -> tuple[str, list[str]]:
    """预演 st-chatu8 的 deduplicateTags(复刻在本仓库 validator 里的那份)。

    只复刻「按逗号切 + 按 base tag 去重」这两步,插件里的其它处理不在范围内。
    """
    seen: dict[str, str] = {}
    order: list[str] = []
    dropped: list[str] = []
    for raw in prompt.split(","):
        segment = raw.strip()
        if not segment:
            continue
        base = st_moss_validator._base_tag(segment)
        if base not in seen:
            seen[base] = segment
            order.append(base)
        else:
            dropped.append(segment)
    return ", ".join(seen[b] for b in order), dropped


def _plugin_pipeline(payload: str, size: str) -> tuple[str, list[str], str]:
    """按 st-chatu8 的完整顺序走一遍:追加尺寸 → 抽走尺寸 → 换行压平 → 去重 → 拼固定词。"""
    text = f"{payload},{size}"                       # parsePromptsContent 追加 sizeResolution
    match = re.search(r",?\s*(\d{2,4})x(\d{2,4})(?=[;\s]|$)", text)
    if not match:
        return text, [], ""
    text = text[:match.start()] + text[match.end():]  # generateComfyUIImage 的 sizeRegex
    resolved = (match.group(1), match.group(2))
    text = re.sub(r"\r?\n", ", ", text)               # processCharacterPrompt
    text, dropped = _plugin_dedupe(text)              # deduplicateTags
    return text, dropped, f"{resolved[0]}x{resolved[1]}"


def _check_pipeline(payload: str, size: str) -> list[str]:
    failures: list[str] = []
    survived, dropped, resolved = _plugin_pipeline(payload, size)
    if dropped:
        failures.append(f"整链预演里去重删了分段: {dropped[:2]}")
    if resolved != size:
        failures.append(f"整链预演取到的尺寸是 {resolved},不是 {size}")
    if "," in survived:
        failures.append("整链预演后仍出现裸逗号")
    restored = json.loads(survived.replace(moss_layout.COMMA_ESCAPE, ","))
    if len(restored["items"]) != 3:
        failures.append(f"整链预演后 items 数量变了: {len(restored['items'])}")
    if restored["items"][2].get("text") != "别走":
        failures.append("整链预演后中文文字项损坏")
    return failures


def _check_layout() -> list[str]:
    failures: list[str] = []
    draft = _layout_draft()
    blocks = st_moss_layout_validator.parse_blocks(f"<images>{_layout_block(draft)}</images>")
    errors = st_moss_layout_validator.validate(blocks, STORY, 1)
    if errors:
        failures.append(f"合格布局被误判: {errors}")
        return failures

    rendered = st_moss_layout_validator.render(blocks)
    match = re.search(r"<prompts>(.*?)</prompts>", rendered, re.DOTALL)
    if not match:
        failures.append("渲染结果里没有 <prompts>")
        return failures
    payload = match.group(1)

    if "," in payload:
        failures.append("布局 payload 里仍有裸逗号,会被 deduplicateTags 切开")
    if "_" not in payload:
        failures.append("布局 payload 里的 abs_centralized 下划线被替换了")

    survived, dropped = _plugin_dedupe(payload)
    if dropped:
        failures.append(f"预演去重会删掉分段: {dropped[:2]}")
    try:
        restored = json.loads(moss_layout.unescape_commas(survived))
    except json.JSONDecodeError as e:
        failures.append(f"过完插件去重后 JSON 已损坏: {e}")
    else:
        if restored.get("bbox_coord_space") != "abs_centralized":
            failures.append("还原后 bbox_coord_space 不对")
        boxes = [item["bbox"] for item in restored["items"]]
        if boxes[0] != [-508, -332, 412, 128]:
            failures.append(f"居中坐标换算不对: {boxes[0]}")

    failures.extend(_check_pipeline(payload, "1024x1536"))

    bad_cases = {
        "框越界": lambda d: d["items"][0].__setitem__("bbox", [180, 260, 1200, 1180]),
        "框退化": lambda d: d["items"][0].__setitem__("bbox", [180, 300, 180, 900]),
        "画布非16倍数": lambda d: d.__setitem__("width", 1000),
        "size不一致": None,
        "缺 text 字段": lambda d: d["items"][2].pop("text"),
    }
    for name, mutate in bad_cases.items():
        broken = _layout_draft()
        size = None
        if mutate is None:
            size = "1536x1024"
        else:
            mutate(broken)
        blocks = st_moss_layout_validator.parse_blocks(
            f"<images>{_layout_block(broken, size)}</images>")
        errors = st_moss_layout_validator.validate(blocks, STORY, 1)
        if not errors:
            failures.append(f"非法布局未被拦下: {name}")
    return failures


def main() -> int:
    failures = _check_caption() + _check_layout()
    if failures:
        print("MOSS 自测失败:")
        for line in failures:
            print(f"  - {line}")
        return 1
    print("MOSS 自测通过:caption 校验、布局编译、去重预演、几何拦截全部正常")
    return 0


if __name__ == "__main__":
    sys.exit(main())
