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

## 15.2 拟声词(优先元类 tag)

| 场景 | tag | post_count | 含义 |
|---|---|---|---|
| 背景带拟声词文字(通用) | `sound_effects` | 52622 | 画面中有音效文字就用它 |
| 拟声词只出现在画面、无其他文字 | `sound_effects_only` | 1084 | 加强 |
| 拟声词被画成台词(人物在说拟声词) | `spoken_sound_effect` | 213 | 对话框式的"嗯哼" |
| 非传统/自创拟声词 | `unconventional_sound_effect` | 1150 | 变形拼写类 |
| 睡眠(zzz) | `zzz` | 15862 | 通用 |
| 口水吞咽/深喉吞液 | `gokkun` | 1566 | 口交系专用,唯一高频实词 |
| 挤压/紧贴(胸/臀/软肉挤在一起) | `gyuu` | 56 | 软肉挤压音 |
| 咕咚/咕噜喝咽 | `gao` / `kupaa` | 1219/712 | 口腔音 |
| 压迫感气场音 | `menacing (jojo)` | 1111 | 威慑氛围 |

**关键结论**:具体拟声词(gusha 咕嚓、gushu 咕啾、pero 舔、pashi 啪、pecho 湿滑、zubu 噗噗等)在 Danbooru **均不是独立 tag**,统一由 `sound_effects` 承载。
→ 库里查不到具体词时,写 `sound_effects` + 自然语言描述声音(如 `sound_effects, wet squishy sound`),**禁止把 romaji 假名拼写当 tag 用**。

## 15.3 组装规则(NSFW 必要环节)

1. **必须有**:每个 NSFW 瞬间至少从 15.1 任选 1 个(优先 `heart`),性情越强越带(`heart_censor`/`heart_shaped_pupils` 等进阶);
2. **必须有**:画面里有声音氛围感(`sound_effects` 系任选 1 个);声音很轻的静谧系场景(深夜独处)可豁免拟声词,但不能豁免爱心;
3. 位置:按槽位归入 `[detail/mood]` 槽,追加在场景 tag 后;自然语言描述音画效果放 prompt 末尾;
4. 爱心与拟声词属于「画面元素」,**不影响**角色槽位,不要写成角色特征(heart_hair_ornament 这类饰品才归 clothing 槽)。
