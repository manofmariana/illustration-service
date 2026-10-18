"""MOSS-Image Layout 草稿的校验与编译(官方规格移植)。

对应 OpenMOSS/MOSS-Image 的 skills/moss-image-prompt-enhancer/scripts/compile_prompt.py
与 ComfyUI 的 MOSSImageLayoutPrompt 节点,两者产出的模型侧格式完全一致:

  {"summary":{...},"items":[{"label":..,"caption":..,"bbox":[y0,x0,y1,x1],..}],
   "bbox_coord_space":"abs_centralized","bbox_format":"yxyx"}

草稿坐标是画布左上原点的像素 xyxy;编译时先向像素边界取整,再减去画布中心。
"""
import json
import math

DRAFT_ROOT_FIELDS = {"width", "height", "bbox_coord_space", "bbox_format", "summary", "items"}
SUMMARY_FIELDS = {"caption", "meta", "canvas", "palette"}
ITEM_FIELDS = {"label", "caption", "bbox", "text", "tags", "palette"}
LABELS = {"object", "character", "text"}
CANVAS_KINDS = {"single", "multi_panel", "collage"}

# 编译后 prompt 里的逗号替换符。必须是 st-chatu8 的 deduplicateTags 不会切开、
# 且 caption 里几乎不可能出现的字符;workflow 侧用 StringReplace 换回逗号。
COMMA_ESCAPE = "\u00a6"


class LayoutError(ValueError):
    pass


def _require(cond: bool, message: str) -> None:
    if not cond:
        raise LayoutError(message)


def _check_fields(value, allowed, required, where: str) -> None:
    _require(isinstance(value, dict), f"{where} 必须是对象")
    unknown = set(value) - allowed
    missing = required - set(value)
    _require(not unknown, f"{where} 有未知字段 {sorted(unknown)}")
    _require(not missing, f"{where} 缺少字段 {sorted(missing)}")


def _nonempty_text(value, where: str) -> None:
    _require(isinstance(value, str) and bool(value.strip()), f"{where} 必须是非空字符串")


def _string_list(value, where: str) -> None:
    _require(isinstance(value, list), f"{where} 必须是数组")
    for i, item in enumerate(value):
        _nonempty_text(item, f"{where}[{i}]")


def _centered_box(box, width: int, height: int, where: str) -> list[int]:
    _require(isinstance(box, list) and len(box) == 4, f"{where} 必须是 [x1,y1,x2,y2]")
    _require(
        all(type(v) in (int, float) and math.isfinite(v) for v in box),
        f"{where} 必须是四个有限数字",
    )
    x1, y1, x2, y2 = box
    _require(x1 < x2 and y1 < y2, f"{where} 必须有正的宽和高")
    _require(
        0 <= x1 < x2 <= width and 0 <= y1 < y2 <= height,
        f"{where} 超出 {width}x{height} 画布",
    )
    result = [
        math.floor(round(y1, 9)) - height // 2,
        math.floor(round(x1, 9)) - width // 2,
        math.ceil(round(y2, 9)) - height // 2,
        math.ceil(round(x2, 9)) - width // 2,
    ]
    _require(
        result[0] < result[2] and result[1] < result[3],
        f"{where} 在该精度下太小,导出后退化",
    )
    return result


def compile_draft(draft: dict) -> str:
    """把草稿编译成模型侧布局 prompt(未做逗号转义)。失败抛 LayoutError。"""
    _check_fields(draft, DRAFT_ROOT_FIELDS, DRAFT_ROOT_FIELDS, "Layout 草稿")

    width, height = draft["width"], draft["height"]
    for name, value in (("width", width), ("height", height)):
        _require(
            type(value) is int and value > 0 and value % 16 == 0,
            f"{name} 必须是 16 的正整数倍",
        )
    _require(draft["bbox_coord_space"] == "abs", "bbox_coord_space 必须是 \"abs\"")
    _require(draft["bbox_format"] == "xyxy", "bbox_format 必须是 \"xyxy\"")

    summary = draft["summary"]
    _check_fields(summary, SUMMARY_FIELDS, {"caption"}, "summary")
    _nonempty_text(summary["caption"], "summary.caption")
    if "canvas" in summary:
        _require(summary["canvas"] in CANVAS_KINDS,
                 "summary.canvas 必须是 single / multi_panel / collage")
    for key in ("meta", "palette"):
        if key in summary:
            _string_list(summary[key], f"summary.{key}")

    items = draft["items"]
    _require(isinstance(items, list) and bool(items), "items 必须是非空扁平数组")
    compiled_items = []
    for index, item in enumerate(items):
        where = f"items[{index}]"
        _check_fields(item, ITEM_FIELDS, {"label", "caption", "bbox"}, where)
        label = item["label"]
        _require(label in LABELS, f"{where}.label 必须是 object / character / text")
        _nonempty_text(item["caption"], f"{where}.caption")
        if label == "text":
            _require("text" in item, f"{where} 是 text 项,必须带 text 字段")
        if "text" in item:
            _nonempty_text(item["text"], f"{where}.text")
        for key in ("tags", "palette"):
            if key in item:
                _string_list(item[key], f"{where}.{key}")
        compiled_items.append({
            key: (_centered_box(value, width, height, f"{where}.bbox") if key == "bbox" else value)
            for key, value in item.items()
        })

    result = {
        "summary": summary,
        "items": compiled_items,
        "bbox_coord_space": "abs_centralized",
        "bbox_format": "yxyx",
    }
    return json.dumps(result, ensure_ascii=False, separators=(",", ":"))


def escape_commas(prompt: str) -> str:
    """把分隔逗号换成分隔符占位,绕过 st-chatu8 的 deduplicateTags。"""
    if COMMA_ESCAPE in prompt:
        raise LayoutError(f"布局内容里不能包含保留字符 {COMMA_ESCAPE!r}")
    return prompt.replace(",", COMMA_ESCAPE)


def unescape_commas(prompt: str) -> str:
    return prompt.replace(COMMA_ESCAPE, ",")


def compile_for_transport(draft: dict) -> str:
    """编译 + 逗号转义,得到最终塞进 <prompts> 的单行字符串。"""
    return escape_commas(compile_draft(draft))


def verify_transport(prompt: str) -> dict:
    """回转校验:把 <prompts> 内容还原成 JSON 并确认结构完好。失败抛 LayoutError。"""
    try:
        data = json.loads(unescape_commas(prompt))
    except json.JSONDecodeError as e:
        raise LayoutError(f"布局 prompt 不是合法 JSON: {e}") from e
    _require(data.get("bbox_coord_space") == "abs_centralized",
             "布局 prompt 的 bbox_coord_space 必须是 abs_centralized")
    _require(data.get("bbox_format") == "yxyx", "布局 prompt 的 bbox_format 必须是 yxyx")
    _require(isinstance(data.get("items"), list) and bool(data["items"]), "布局 prompt 缺少 items")
    return data
