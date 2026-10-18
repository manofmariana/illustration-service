# 15. NSFW 场景符号 Tag(爱心 + 拟声词)——必要环节

> 数据来源:Danbooru 官方 tag(post_count 为实际使用量,已逐一验证存在性)。
> 使用场景:任何 NSFW 瞬间(第 5 步命中 09/14 类)在组装 prompt 时,**酌情加入本文件符号 tag**;
> 色情漫画里爱心与拟声词是氛围的必要环节,缺失会让画面像普通擦边图。

## 15.1 爱心符号(按使用场景选 1~2 个即可)

| 场景 | tag | post_count | 含义 |
|---|---|---|---|
| 画面中出现 ♥ 心形符号(漂浮/散落/背景) | `heart` | 900847 | 心形符号本体,最通用 |
| 台词气泡里冒爱心(娇喘/告白台词) | `spoken_heart` | 79190 | 说话内容里画心 |
| 用爱心打码(NSFW 专属画面处理) | `heart_censor` | 25864 | 马赛克是爱心形 |
| 画面布满爱心当背景 | `heart_background` | 9265 | 背景氛围化 |
| 眼里冒心形(被迷住/情欲上头) | `heart_in_eye` | 15041 | 瞳孔变色成心形 |
| 爱心瞳孔 | `heart-shaped_pupils` | 120056 | 同上,量大 |
| 爱心贴乳/爱心乳贴 | `heart_pasties` | 13186 | 服饰类,NSFW 实用 |

**注意**:`floating_hearts` / `heart_eyes` / `heart_sweat` 等常见猜想 **不是 tag**(post=0),禁止使用。

## 15.2 拟声词(主要形态 = `sound_effects` + 具体声音描述)

**核心写法(80% 场景就这么写)**:
```
sound_effects, <具体声音的英文/罗马音描述>
```
示例:`sound_effects, wet squishy sounds` / `sound_effects, loud moan sfx` / `sound_effects, squelching`。

| 场景 | tag | post_count | 说明 |
|---|---|---|---|
| 背景带拟声词文字(通用) | `sound_effects` | 52622 | 必带主 tag |
| 拟声词只出现在画面、无其他文字 | `sound_effects_only` | 1084 | 选带 |
| 拟声词被画成台词(人物在说拟声词) | `spoken_sound_effect` | 213 | 对话框式呻吟 |
| 非传统/自创拟声词 | `unconventional_sound_effect` | 1150 | 变形拼写类 |
| 口水吞咽/深喉吞液 | `gokkun` | 1566 | 口交系专用实词 |
| 软肉挤压/紧贴音(胸/臀/大腿) | `gyuu` | 56 | NSFW 高频音效实词 |

**NSFW 专用实词对照**(可作 `sound_effects` 后的描述词,均非独立 tag,勿裸用):
- 体液/黏液声:gushu(咕啾)、gusha(咕嚓)、pecho(湿滑)、moitchu(黏腻);
- 拍打/抽插声:pashi、pan、zubuu(噗嗤插);
- 舔吮声:pero、chuu(亲吻音)、gupo(吮吸);
- 吞咽声:gokkun、goku、guku;
- 呻吟/粗气:u-n、mmm、ngyaa(翻白眼式呻吟)等按正文语气转写。

**禁止**:`gao`、`kupaa`、`zzz`、`menacing (jojo)` 等萌系/通用音效词——非 NSFW 语境,不入选;romaji 假名拼写单独作为 tag 输出(如裸写 `gusha`)等于伪造 tag,一律 `sound_effects` + 描述。

## 15.3 组装规则(NSFW 必要环节)

1. **必须有**:每个 NSFW 瞬间至少从 15.1 任选 1 个(优先 `heart`),性情越强越带(`heart_censor`/`heart_shaped_pupils` 等进阶);
2. **必须有**:画面里有声音氛围感——按 §15.2 主形态写 `sound_effects` + 具体声音描述(如 `sound_effects, wet squishy sound`);声音很轻的静谧系场景(深夜独处)可豁免拟声词,但不能豁免爱心;
3. 位置:按槽位归入 `[detail/mood]` 槽,追加在场景 tag 后;自然语言描述音画效果放 prompt 末尾;
4. 爱心与拟声词属于「画面元素」,**不影响**角色槽位,不要写成角色特征(heart_hair_ornament 这类饰品才归 clothing 槽)。
