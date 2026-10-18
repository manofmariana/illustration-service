## 10. EXPRESSION & REACTION

> 对应槽位：`[expression/reaction]`
> 表情、身体反应、液体是互相关联的叠加层——同一体位可叠加不同强度。本章不拆分独立子节，而是按**强度递进**组织，AI 根据用户描述的关键词自动匹配对应梯级。

### 10.1 表情维度

按情绪光谱分类。每类选 1-2 个标签，不可跨类矛盾（如 `smile` + `crying` 通常矛盾，除非刻意营造破灭感）。

| 情绪类型 | 核心标签 |
|---|---|
| 诱惑/邀请 | `seductive smile, half-closed eyes, looking at viewer, heavy-lidded eyes, licking lips, parted lips, come hither, naughty face` |
| 服从/献身 | `submissive, devoted, obedient, looking up, kneeling, closed eyes, peaceful, light smile` |
| 主导/得意 | `smug, smirk, confident, dominant, evil smile, looking down, sadistic, cool, composed` |
| 抗拒/痛苦 | `scared, reluctant, crying, tears, streaming tears, struggling, frown, clenched teeth, pain, wavy mouth` |
| 失神/崩坏 | `ahegao, tongue out, drooling, rolling eyes, fucked silly, mind break, heart-shaped pupils, torogao, cross-eyed, empty eyes` |
| 羞耻/内疚 | `embarrassed, blush, ashamed, guilty, humiliated, covering face, looking away, nervous` |
| 平静/中性 | `expressionless, emotionless, bored, sleepy, yawning, looking at phone, closed eyes, calm` |
| 惊讶/好奇 | `surprised, wide-eyed, @_@, nervous sweatdrop, curious, o_o` |

### 10.2 强度映射

根据用户描述中的情绪关键词，自动匹配对应标签等级。**同一 prompt 中表情标签不超过 3 个**，选最能代表当前强度的。

| 用户描述关键词 | 强度 | 表情标签 | 身体反应 |
|---|---|---|---|
| 有点害羞/微红/不好意思 | Lv1 轻度 | `blush, shy, slight smile` | `slight trembling` |
| 喘气/忍不住/舒服 | Lv2 中度 | `moaning, panting, heavy breathing, blush` | `trembling, sweat` |
| 快哭了/受不了/要坏了 | Lv3 高度 | `ahegao, tears, tongue out, drooling, crying` | `arched back, toes curling, shaking, body blush` |
| 彻底坏掉/崩溃/失神 | Lv4 极限 | `fucked silly, mind break, heart-shaped pupils, rolling eyes` | `convulsing, limp body, foaming at the mouth, squirting` |
| 得意/主导/享受 | 主导型 | `smug, smirk, confident, seductive smile` | 无明显生理失控 |
| 害怕/不情愿/被迫 | 抗拒型 | `scared, reluctant, crying, tears` | `struggling, trembling, clenched fists` |
| 认命/顺从/放弃抵抗 | 屈服型 | `empty eyes, submissive, defeated, expressionless` | `limp body, no resistance, twitching` |
| 困倦/无力/睡眠中 | 无意识型 | `closed eyes, sleeping, zzz, expressionless` | `limp body, no reaction, relaxed face` |

**使用规则**：用户未明确描述情绪时，根据场景默认取 Lv2。强制/胁迫场景默认取"抗拒型"，除非用户指定已屈服。Lv3 以上必须搭配至少 1 个身体反应标签。

### 10.3 身体反应

| 类型 | 核心标签 |
|---|---|
| 生理反应 | `trembling, goosebumps, flush, sweat, shaking, steaming body, sweat drops, full-face blush, body blush, nose blush` |
| 高潮反应 | `orgasm, arched back, toes curling, legs shaking, convulsing, squirting, female ejaculation, head back, trembling` |
| 抵抗/顺从 | `struggling, grabbing sheets, clinging, limp body, twitching, no resistance, arms at sides` |
| 体力消耗 | `sweat, sweaty, sweating profusely, greasy skin, heavy breathing, panting, exhausted, collapsed` |

**使用规则**：生理反应和高潮反应可叠加（`trembling + arched back + orgasm`）。抵抗/顺从二选一。体力消耗按场景强度递增。每类选 1-2 个标签，总数不超过 3 个身体反应标签。

### 10.4 液体层次

从轻到重的递进光谱。不互斥，可按场景强度叠加 2-3 级。

| 层级 | 标签 | 适用场景 |
|---|---|---|
| 轻度湿润 | `pussy juice` / `wet` / `shiny skin` | 前戏/自慰/诱惑 |
| 中度液体 | `sweat` / `saliva` / `saliva trail` / `drooling` | 口交/深喉/过激 |
| 射精 | `precum` → `cum` → `cum inside` / `creampie` | 插入性爱 |
| 大量溢出 | `cum overflow` → `cum drip` → `cum string` → `cum pool` | 多人/种付/后入 |
| 极限精浴 | `excessive cum` → `cum bath` → `bukkake` | 轮奸/群交/RBQ |
| 女方潮喷 | `female ejaculation` / `squirting` / `pussy juice pool` | 高潮/过激/自慰 |

**使用规则**：不同角色可叠加不同液体（女方 pussy juice + 男方 cum）。液体层次选 1-2 级，不跨越超过 2 级（不要同时写 `pussy juice` 和 `bukkake`，除非刻意制造极端对比）。

### 10.5 身体痕迹

| 类型 | 核心标签 |
|---|---|
| 吻痕/咬痕 | `hickey, bite marks, lipstick mark, kiss mark` |
| 绳痕/束缚痕 | `rope marks, red marks, skindentation, bound wrists marks` |
| 掌印/击打痕 | `handprint, slap mark, spank mark, red ass` |
| 淤青/伤痕 | `bruise, bruise on face, scars, scratch marks, whip marks, cuts, blood on face` |
| 书写/标记 | `body writing, tally marks, tattoo, number tattoo, barcode tattoo, lipstick mark on body` |
| 体液痕迹 | `cum on body, cum on face, cum on breasts, cum on hair, cum on clothes, pussy juice stain, sweat stain` |

**使用规则**：痕迹隐含了前序动作，选 1-2 个能暗示剧情的即可。绳痕暗示束缚，掌印暗示打屁股，书写暗示调教/RBQ。不要同时堆叠所有痕迹标签。

---

