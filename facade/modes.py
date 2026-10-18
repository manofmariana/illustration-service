"""模式注册表:一条分支 = 一套提取 / 技能 / 校验 / 渲染。

四条的差别只在"给 agent 什么料"和"怎么验收 agent 的输出",
路由、重试、SSE 全部共用。
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from . import (
    config,
    extractor,
    st_extractor,
    st_moss_layout_validator,
    st_moss_validator,
    st_validator,
    validator,
)

@dataclass(frozen=True)
class Mode:
    key: str
    title: str
    skill: str
    extract: Callable[[dict], Any]
    build_args: Callable[[Any], str]
    parse: Callable[[str], list]
    validate: Callable[[list, str, int], list[str]]
    render: Callable[[list], str]

    @property
    def skill_dir(self) -> Path:
        return config.SKILLS_DIR / self.skill


MODES: dict[str, Mode] = {
    m.key: m
    for m in (
        Mode(
            key="frz",
            title="凡人修仙传独立前端",
            skill="story-illustrator",
            extract=extractor.extract,
            build_args=extractor.build_skill_args,
            parse=validator.parse_blocks,
            validate=validator.validate,
            render=validator.render,
        ),
        Mode(
            key="anima",
            title="酒馆 · Anima",
            skill="story-illustrator-st",
            extract=st_extractor.extract,
            build_args=st_extractor.build_skill_args,
            parse=st_validator.parse_blocks,
            validate=st_validator.validate,
            render=st_validator.render,
        ),
        Mode(
            key="moss",
            title="酒馆 · MOSS caption",
            skill="story-illustrator-st-moss",
            extract=st_extractor.extract,
            build_args=st_extractor.build_skill_args,
            parse=st_moss_validator.parse_blocks,
            validate=st_moss_validator.validate,
            render=st_moss_validator.render,
        ),
        Mode(
            key="layout",
            title="酒馆 · MOSS layout",
            skill="story-illustrator-st-moss-layout",
            extract=st_extractor.extract,
            build_args=st_extractor.build_skill_args,
            parse=st_moss_layout_validator.parse_blocks,
            validate=st_moss_layout_validator.validate,
            render=st_moss_layout_validator.render,
        ),
    )
}

ALIASES = {"moss-layout": "layout", "st": "anima", "web": "frz"}


def resolve(key: str | None) -> Mode | None:
    if not key:
        return None
    key = key.strip().lower()
    return MODES.get(ALIASES.get(key, key))
