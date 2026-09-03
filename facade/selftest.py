"""离线自测:用真实请求样例验证 extractor 切分 + validator 校验(不调用 kimi)。

用法: python -m facade.selftest <A.json路径>
"""
import json
import sys

from . import extractor, validator


def _safe(s: str) -> str:
    return s.encode("gbk", errors="replace").decode("gbk")


def main() -> int:
    path = sys.argv[1]
    body = json.loads(open(path, encoding="utf-8").read(), strict=False)
    si = extractor.extract(body)
    print(f"[extract] 图片数量: {si.image_count}")
    print(f"[extract] 角色资料: {len(si.characters)} 字")
    print(f"[extract] 场景信息: {len(si.scene)} 字")
    print(f"[extract] 当前正文: {len(si.story)} 字")
    print(f"[extract] 正文开头: {_safe(repr(si.story[:60]))}")
    print(f"[extract] 正文结尾: {_safe(repr(si.story[-60:]))}")
    assert si.image_count > 0
    assert si.story, "正文为空"
    assert "玉衡" in si.characters or len(si.characters) > 50, "角色资料异常"

    # validator 烟测:构造一个合法输出和一个非法输出
    anchor = si.story.splitlines()[2][:20] if len(si.story.splitlines()) > 2 else si.story[:20]
    good = "\n\n".join(
        f"<image>\n<anchor>{anchor}</anchor>\n<prompt>1girl, solo, black hair, hanfu, indoors</prompt>\n</image>"
        for _ in range(si.image_count)
    )
    # 非法:anchor 重复会报错,所以用不同片段
    lines = [l for l in si.story.splitlines() if len(l) >= 12]
    good = "\n\n".join(
        f"<image>\n<anchor>{lines[i][:16]}</anchor>\n<prompt>1girl, solo, black hair, hanfu, indoors</prompt>\n</image>"
        for i in range(min(si.image_count, len(lines)))
    )
    blocks = validator.parse_blocks(good)
    errs = validator.validate(blocks, si.story, si.image_count)
    print(f"[validate] 合法样本错误: {errs or '无(通过)'}")

    bad = "<image>\n<anchor>这段正文里不存在的话</anchor>\n<prompt>玉衡, 1boy, ```markdown```</prompt>\n</image>"
    errs = validator.validate(validator.parse_blocks(bad), si.story, si.image_count)
    print(f"[validate] 非法样本应报错 {len(errs)} 项: {errs}")
    assert errs, "非法样本竟然通过了"
    print("selftest 全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
