"""ST 提取层自测:不启动 agent,只验标签切分。

    ..\\python_embeded\\python.exe -m facade.st_selftest
"""
import sys

from . import st_extractor

STORY = "雨夜，她把手机推到我面前，屏幕上只有两个字：别走。窗外的霓虹在雨里晕开。"


def _body(*messages: str) -> dict:
    return {"messages": [{"role": "user", "content": m} for m in messages]}


def _new_preset_body() -> dict:
    return _body(
        "<生图数量>\n\n2\n\n</生图数量>",
        "<世界书条目>\n\n深渊教团的徽记是倒悬的黑塔。\n\n</世界书条目>",
        "<可用绘图角色列表>\n\n当前可用**绘图**特定角色列表：\n*****\n林月：黑长直，白毛衣\n*****\n\n</可用绘图角色列表>",
        "<历史前文>\n\n上一轮他们还在争论雨伞归谁。\n\n</历史前文>",
        f"<剧情原文>\n{STORY}\n</剧情原文>\n",
        "<用户需求>\n\n竖构图，要看清屏幕上的字\n\n</用户需求>",
    )


def main() -> int:
    failures: list[str] = []

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
