"""ST 提取层自测:不启动 agent,只验标签切分。

素材直接取自仓库里的智绘姬预设(`presets/正文生图LLM预设.json`),宏用样例值填掉。
预设里改了标签名或删了某一条,这里会跟着红,不会出现"测试通过但线上提取不到"。

    ..\\python_embeded\\python.exe -m facade.st_selftest
"""
import json
import sys

from . import config, st_extractor

STORY = "雨夜，她把手机推到我面前，屏幕上只有两个字：别走。窗外的霓虹在雨里晕开。"

PRESET = config.BASE_DIR / "presets" / "正文生图LLM预设.json"

# 预设里的宏 → 样例值
MACROS = {
    "{{正文}}": STORY,
    "{{用户需求}}": "竖构图，要看清屏幕上的字",
    "{{上下文}}": "上一轮他们还在争论雨伞归谁。",
    "{{世界书触发}}": "深渊教团的徽记是倒悬的黑塔。",
    "{{角色启用列表}}": "林月：黑长直，白毛衣",
    "{{通用角色启用列表}}": "",
    "{{通用服装启用列表}}": "",
}

# 提取器认识的六个标签,预设里缺一个就说明两边不同步了
TAGS = ("剧情原文", "用户需求", "生图数量", "可用绘图角色列表", "历史前文", "世界书条目")


def _body(*messages: str) -> dict:
    return {"messages": [{"role": "user", "content": m} for m in messages]}


def _preset_messages() -> list[str]:
    data = json.loads(PRESET.read_text(encoding="utf-8"))
    entries = next(iter(data.values()))["entries"]
    messages = []
    for entry in entries:
        if not entry.get("enabled", True):
            continue
        text = entry["content"]
        for macro, value in MACROS.items():
            text = text.replace(macro, value)
        messages.append(text)
    return messages


def _new_preset_body() -> dict:
    return _body(*_preset_messages())



def main() -> int:
    failures: list[str] = []

    blob = "".join(_preset_messages())
    missing = [tag for tag in TAGS if f"<{tag}>" not in blob]
    if missing:
        failures.append(f"预设里缺标签(与提取器不同步): {missing}")

    si = st_extractor.extract(_new_preset_body())
    if STORY not in si.story:
        failures.append(f"正文没切出来: {si.story[:40]!r}")
    if "<剧情原文>" in si.story:
        failures.append("正文里混进了标签")
    if si.image_count != 2:
        failures.append(f"数量应是 2,实得 {si.image_count}")
    if "林月" not in si.characters:
        failures.append("角色列表没切出来")
    if "雨伞" not in si.history:
        failures.append("历史前文没切出来")
    if "黑塔" not in si.worldbook:
        failures.append("世界书没切出来")
    if "屏幕" not in si.user_request:
        failures.append("用户需求没切出来")

    args = st_extractor.build_skill_args(si)
    for header in ("[可用绘图角色列表]", "[历史前文与世界书]", "[剧情与设定素材]", "[用户需求]", "[图片数量 N]"):
        if header not in args:
            failures.append(f"skill args 缺 {header}")
    if "2" not in args.rsplit("[图片数量 N]", 1)[-1]:
        failures.append("skill args 的数量不对")

    # 宏没渲染:历史/世界书应视为空
    blank = st_extractor.extract(_body(
        "<历史前文>\n\n{{上下文}}\n\n</历史前文>",
        "<世界书条目>\n\n{{世界书触发}}\n\n</世界书条目>",
        f"<剧情原文>\n{STORY}\n</剧情原文>\n",
    ))
    if blank.history or blank.worldbook:
        failures.append("未渲染的宏没被丢弃")

    # {{正文}} 没渲染必须报错,不能拿别的消息兜底
    try:
        st_extractor.extract(_body("<剧情原文>\n{{正文}}\n</剧情原文>\n", "很长的角色列表" * 50))
    except ValueError:
        pass
    else:
        failures.append("{{正文}} 未渲染时没有报错")

    # 旧预设的 setvar 仍能读数量(区间取下限)
    old = st_extractor.extract(_body(
        "<剧情原文>\n" + STORY + "\n</剧情原文>\n",
        "{@setvar::生图数量::3-4@}",
    ))
    if old.image_count != 3:
        failures.append(f"旧 setvar 数量应为 3,实得 {old.image_count}")

    # 没有任何数量标签时用默认值
    bare = st_extractor.extract(_body("<剧情原文>\n" + STORY + "\n</剧情原文>\n"))
    if bare.image_count != st_extractor.DEFAULT_IMAGE_COUNT:
        failures.append(f"缺数量标签时应回默认 {st_extractor.DEFAULT_IMAGE_COUNT}")

    # 思维链块必须剥掉
    hidden = st_extractor.extract(_body(
        f"<剧情原文>\n<thinking>内心戏</thinking>{STORY}\n</剧情原文>\n"))
    if "内心戏" in hidden.story:
        failures.append("正文里的 <thinking> 没剥掉")

    if failures:
        print("ST 提取自测失败:")
        for line in failures:
            print(f"  - {line}")
        return 1
    print("ST 提取自测通过:六个标签、宏兜底、旧 setvar、思维链剥离全部正常")
    return 0


if __name__ == "__main__":
    sys.exit(main())
