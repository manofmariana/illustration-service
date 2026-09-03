## 12. SCENE & ENVIRONMENT

> 对应槽位：`[scene/environment]`
> 场景不只是背景——它决定体位配合、风险感和情感氛围。本章按私密程度组织，每场景配适用体位提示。

### 12.0 世界风格锚定(必须)

> ⚡ **铁律**:每个 prompt 的 scene 槽位**第 1 个 tag 必须是世界风格锚定**(下表),写明是 现代/未来/蒸汽朋克/赛博朋克/科幻/东方武侠修仙/西方奇幻/中世纪/近代——风格不清是最大事故源,模型会把汉服画进霓虹都市。
> 锚定后必须与 clothing/建筑/detail 槽保持一致(见 slot-order §4.1),表内 "不存在" 的风格用自然语言短句锚定(放 prompt 末尾)。

| 世界风格 | 锚定 tag(已验证) | 配衬 tag |
|---|---|---|
| 现代/都市日常 | 无可靠 tag(`modern` 为 0 使用) → 自然语言 `modern city` / `modern apartment` / `suburban street` | `city` `skyscraper` `street` `apartment` |
| 未来/科幻 | `science_fiction`(59150) | `space_station` `space_ship` `mecha`(55421);`futuristic` 0 使用,勿用 |
| 蒸汽朋克 | `steampunk`(2094) | `victorian` `industrial`(663) `clockwork`(自然语言) |
| 赛博朋克 | `cyberpunk`(4379) | `cyberspace` `city, neon lights`(自然语言);`cyberpunk city` 不存在 |
| 东方武侠/修仙 | `wuxia`(63) | `hanfu` `chinese dress` `ancient shrine` `torii gate`(和风勿混);`xianxia`/`chinese_fantasy` 不存在 → + 自然语言 `chinese immortal sects` |
| 西方奇幻 | `fantasy`(20301) | `castle`(10455) `dungeon` `magic circle`;`high_fantasy`/`western_fantasy` 不存在 |
| 中世纪 | `medieval`(1502) | `castle` `knight armor` `village`;`medieval_fantasy` 不存在 |
| 近代(维多利亚/复古/工业) | `victorian`(1472) 或 `renaissance`(81) 或 `industrial`(663) | `dieselpunk`(64) 柴油朋克 |
| 末世/废土 | `post-apocalyptic`(0 使用) → 自然语言 `destroyed city` | `ruins` `sandstorm` `rubble` |

**推断顺序**:正文场景信息(朝代/灵力/机甲/魔法/末世)→ 角色资料(仙侠服装/军装/机娘)→ 正文环境描写;三处矛盾时以正文场景信息为准,但需用锚定 tag 统一到同一风格。

### 12.1 场所速查

#### 私密空间（低风险，可尽情发挥）

| 场所 | 核心标签 | 适用体位 |
|---|---|---|
| 卧室 | `bedroom, on bed, bed sheet, pillow` | 所有体位通用 |
| 浴室 | `bathroom, shower, bathtub, wet floor, tiled wall, steam` | 站立压墙/坐位/素股 |
| 酒店 | `love hotel, hotel room, luxury hotel` | NTR/偷情/事后 |
| 地牢 | `dungeon, stone wall, chains` | 束缚BDSM/过激/调教 |

#### 半公开空间（中风险，随时可能被发现）

| 场所 | 核心标签 | 适用体位 |
|---|---|---|
| 客厅/沙发 | `couch, sofa, living room` | 坐位/骑乘/半公开匆忙 |
| 厨房 | `kitchen, counter` | 站立后入/裸体围裙/日常 |
| 办公室 | `office, desk, office chair, after hours` | 桌上正身/职场胁迫/桌下口交 |
| 车内 | `in car, car interior, backseat` | 坐位/口交/素股 |
| 教室 | `classroom, school desk, chalkboard` | 桌上/自慰/师生 |
| 窗边 | `against window, glass, city view, exposed` | 后入压窗/暴露刺激 |

#### 公共空间（高风险，羞耻+禁忌）

| 场所 | 核心标签 | 适用体位 |
|---|---|---|
| 电车/公交 | `train, crowded train, handrail, train interior` | 痴汉/站立/暴露 |
| 电梯 | `elevator` | 快速暴露/闪露/时间压力 |
| 楼梯间 | `stairwell, emergency stairs, concrete wall` | 快速后入/死角紧迫 |
| 公园/长椅 | `park, park bench, outdoors` | 暴露露出/无内短裙 |
| 试衣间 | `fitting room, curtain, mirror` | 偷情/暴露/更衣 |
| 电影院 | `cinema, dark, movie theater, seats` | 暗中口交/手交/隐蔽 |
| 餐厅/居酒屋 | `restaurant, izakaya, table` | 餐桌坐位/桌下服务 |
| 海滩/泳池 | `beach, swimming pool, ocean` | 泳装露出/暴露 |

#### 特殊场景

| 场所 | 核心标签 | 适用主题 |
|---|---|---|
| 教堂 | `cathedral, stained glass, pews, confessional` | 修女亵渎/堕落 |
| 神社/寺庙 | `ancient shrine, torii gate, shouji, tatami` | 巫女破戒/和风 |
| 废墟/战后 | `ruins, destroyed building, rubble, collapsed` | 战败/俘虏/过激 |
| 实验室 | `laboratory, sci-fi, culture tank` | 机械/催眠/改造 |
| 温泉 | `onsen, hot spring, steam, wooden bath` | 共浴/素股/手交 |

### 12.2 场景心理

**四要素公式**：`场所选择 + 体位配合 + 风险元素 + 情感氛围 = 完整场景叙事`

**场所风险矩阵**：

| 场所 | 私密程度 | 风险等级 | 核心张力 |
|---|---|---|---|
| 卧室/酒店 | ⭐⭐⭐⭐⭐ | 低 | 经典安全，可尽情发挥 |
| 浴室/厨房/客厅 | ⭐⭐⭐⭐ | 中 | 日常突破+半公开紧张 |
| 车内 | ⭐⭐⭐ | 中 | 空间创意+车震显眼 |
| 窗边/阳台 | ⭐⭐ | 高 | 暴露刺激+被看到的风险 |
| 办公室/教室 | ⭐⭐⭐ | 高 | 职场/校园禁忌+随时有人回来 |
| 楼梯间 | ⭐⭐ | 极高 | 死角隐蔽+脚步声压迫 |
| 电梯 | ⭐ | 极高 | 时间倒计时+门开恐惧 |
| 试衣间/电影院 | ⭐⭐ | 高 | 半私密+周围有陌生人 |
| 电车/公交 | ⭐ | 极高 | 人群中被围+无法逃脱 |
| 教堂/废墟 | ⭐⭐⭐ | 中 | 神圣亵渎/战后苍凉 |

**场景心理关键词**：
- 安全温柔 → `bedroom, gentle, tender, pillow, soft lighting`
- 湿滑挑战 → `shower, bathroom, wet, steam, against wall, soap`
- 日常突破 → `kitchen, counter, cooking, interrupted, casual`
- 匆忙激情 → `couch, quickie, clothes on, pants down, skirt up, open fly`
- 暴露刺激 → `window, against glass, exposed, curtains open, from outside`
- 职场禁忌 → `office, desk, after hours, overtime, coworker risk`
- 时间压力 → `elevator, stairwell, urgent, quick, footsteps, risk of discovery`
- 神圣亵渎 → `cathedral, stained glass, confessional, corrupted, fallen, blasphemy`

### 12.3 天气/时辰

> 光线/光影/色调标签禁止输出（lora已内置）。以下仅允许环境天气和时辰描写。

| 类型 | 可选标签 |
|---|---|
| 晴/昼 | `day, sunlight, afternoon, morning` |
| 雨 | `rain, rainy night, wet pavement, rain droplets, rainy cityscape` |
| 雪 | `snow, snowfall, snowfield, blizzard` |
| 雾 | `fog, mist, dense fog, morning mist, steam, condensation` |
| 夜 | `night, dark, moonlight, night cityscape, starry sky` |
| 黄昏/黎明 | `sunset, twilight, golden hour` |
| 室内氛围 | `dim lighting, dark room, candlelight, ambient light` |

### 12.4 场景细节

让画面有故事感的锚点道具，按需选1-3个即可。

| 类别 | 标签 |
|---|---|
| 衣物散落 | `scattered clothes, clothes on floor, unworn panties, crumpled sheets, shoes removed` |
| 避孕套 | `used condom, condom wrapper, condom box, many used condoms, condom belt` |
| 事后痕迹 | `cum on sheets, cum pool, pussy juice stain, sweat stain, used tissue` |
| 道具散落 | `sex toy nearby, vibrator on bed, dildo on floor, anal beads on table` |
| 饮食物品 | `wine glass, beer mug, coffee mug, cigarette, ashtray, candle` |
| 电子设备 | `smartphone, laptop, big computer screen, webcam, recording` |
| 空间细节 | `wooden floor, carpet, tatami, curtain, mirror, window, picture frame` |

---

