"""ST 输出契约硬校验与渲染(按预设实证格式)。

每个 <image> 块固定 5 个子标签,整体 <images> 包裹:
  <images>
  <image>
  <regex>正文原句(单行)</regex>
  <title_styled>图片标题,5-15字中文</title_styled>
  <Tag_think>60-100字剧情浓缩,仅视觉可见元素</Tag_think>
  <size>832x1216|1216x832|1024x1024</size>
  <prompts>英文tag,逗号分隔</prompts>
  </image>
  ...
  </images>
不输出预设里的越狱噪声:sāfe& 前缀、<safe>/<sāfe&end> 尾块、end 截断。
"""
import re
from dataclasses import dataclass

BLOCK_RE = re.compile(r"<image>(.*?)</image>", re.DOTALL)
SUB_RE = {
    "regex": re.compile(r"<regex>(.*?)</regex>", re.DOTALL),
    "title": re.compile(r"<title_styled>(.*?)</title_styled>", re.DOTALL),
    "think": re.compile(r"<Tag_think>(.*?)</Tag_think>", re.DOTALL),
    "size": re.compile(r"<size>(.*?)</size>", re.DOTALL),
    "prompts": re.compile(r"<prompts>(.*?)</prompts>", re.DOTALL),
}
VALID_SIZES = {"1024x1536", "1536x1024", "1280x1280"}
CJK_RE = re.compile(r"[一-鿿]")
FORBIDDEN_TAGS_RE = re.compile(r"(\*\*|```|negative prompt|<\w+>|【|】|sāfe)", re.IGNORECASE)


@dataclass
class STBlock:
    regex: str
    title: str
    think: str
    size: str
    prompts: str


def parse_blocks(text: str) -> list[STBlock]:
    blocks: list[STBlock] = []
    for m in BLOCK_RE.finditer(text):
        inner = m.group(1)
        def sub(key: str) -> str:
            sm = SUB_RE[key].search(inner)
            return sm.group(1).strip() if sm else ""
        blocks.append(STBlock(
            regex=sub("regex"), title=sub("title"), think=sub("think"),
            size=sub("size"), prompts=" ".join(sub("prompts").split()),
        ))
    return blocks


def validate(blocks: list[STBlock], story: str, expected: int) -> list[str]:
    errors: list[str] = []
    if len(blocks) != expected:
        errors.append(f"<image> 块数 {len(blocks)} != 要求 {expected}")
    seen: set[str] = set()
    for i, b in enumerate(blocks, 1):
        if not b.regex:
            errors.append(f"第{i}块缺少 <regex>")
        else:
            if "\n" in b.regex:
                errors.append(f"第{i}块 regex 必须单行")
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
        if not b.prompts:
            errors.append(f"第{i}块缺少 <prompts>")
        elif CJK_RE.search(b.prompts):
            errors.append(f"第{i}块 prompts 含中文")
        elif FORBIDDEN_TAGS_RE.search(b.prompts):
            errors.append(f"第{i}块 prompts 含禁用内容(markdown/xml/sāfe 等)")
    positions = [story.find(b.regex) for b in blocks if b.regex and b.regex in story]
    if positions != sorted(positions):
        errors.append("regex 未按剧情顺序排列")
    return errors


def render(blocks: list[STBlock]) -> str:
    """prompts 中下划线统一替换为空格(同网页端:danbooru 下划线 tag 生图模型无法辨认)。"""
    inner = "\n\n".join(
        "<image>\n"
        f"<regex>{b.regex}</regex>\n"
        f"<title_styled>{b.title}</title_styled>\n"
        f"<Tag_think>{b.think}</Tag_think>\n"
        f"<size>{b.size}</size>\n"
        f"<prompts>{b.prompts.replace('_', ' ')}</prompts>\n"
        "</image>"
        for b in blocks
    )
    return f"<images>\n{inner}\n</images>"
