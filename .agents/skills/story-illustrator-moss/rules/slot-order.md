## 4. 句子计划(SENTENCE PLAN)

Anima 版在这里排的是 tag 槽位;MOSS 版排的是**一段话里先说什么后说什么**。顺序本身就是权重,先说的事模型记得更牢。

```
① 媒介+主体 → ② 外观/服装 → ③ 动作/接触/表情 → ④ 场景/时辰/物件 → ⑤ 机位/构图 → ⑥ 光照/色彩 → ⑦ 细节/质感
```

### 4.1 跨段风格一致性

> ⚡ **同一段 caption 内世界观不能打架**:服装、场景、光照必须同属一个世界。古装配古建与烛光,赛博配霓虹与雨夜,日常配自然光。`hanfu` 站在赛博都市、`latex catsuit` 出现在古庙,都属于会画崩的矛盾组合。同一世界观内的混搭(如 `kimono` + 现代酒店房间)是合理的。

> ⚠️ **特殊主题速查**:NTR、束缚 BDSM、RBQ/物化、男娘 Futa、睡奸、过激、调戏猥亵、调教宠物、胁迫、偷窥展示、事后、另类日常、大车小孩、攻守反转——匹配到先在 `tags/14` 查配方,再决定 caption 里要写哪些可见要素。

### 4.2 词量预算(不是 tag 数)

| 场景复杂度 | caption 词数 | 说明 |
|---|---|---|
| 简单(单人展示/诱惑/暴露/自慰) | 80–140 | 外观+服装+姿态+场景+光 |
| 标准(双人性爱/前戏) | 120–200 | 加体位/接触点/反应/液体 |
| 复杂(多人/特殊主题/剧情主视觉) | 160–260 | 多角色外观分写 + 关系句 |

**分段建议预算**(按 ①~⑦ 分配,不是硬性):

| 段 | 占比 | 要点 |
|---|---|---|
| ① 媒介+主体 | 10% | 一句话定调:什么媒介、谁、几个、在干什么 |
| ② 外观/服装 | 25% | 头发2项+眼睛1项+体型+服装款式材质状态 |
| ③ 动作/接触/表情 | 25% | 核心动作1个+接触对象+表情强度 |
| ④ 场景/时辰 | 15% | 主场所+1~2个环境物件+时间天气 |
| ⑤ 机位/构图 | 10% | 景别+视角+左右前后关系 |
| ⑥ 光照/色彩 | 10% | **必写**,光源方向与性质+色温+主色 |
| ⑦ 细节/质感 | 5% | 布纹/汗光/雨滴/景深,可有可无 |

**原则**:服装与接触是信息密度最高的两处,多花词;其余保持精炼。**不要为了凑字数堆形容词**——官方明确反对"redundant quality tags"和空泛修饰。

### 4.3 视线方向

**单人**:除非素材明确写背影/背对/侧脸,默认让主体看向观者,例如 `looking straight at the viewer`。
**两人及以上**:不强制对视,按互动关系写清楚谁在看谁,例如 `the girl looks up at him`。

| 素材意图 | caption 写法 |
|---|---|
| 未指定/正面(单人) | `facing the viewer, eyes meeting the camera` |
| 回头 | `turning back over her shoulder, looking at the viewer` |
| 背对/远去 | `seen from behind, walking away` |
| 侧脸 | `in profile` |
| 角色间互动(多人) | `the girl gazes up at the boy` |

### 4.4 多人:用句子分人,不用 BREAK

**核心**:每个角色的外观必须**紧跟**该角色的动作,一个角色一句话或一个从句,读的人(和模型)才知道特征挂在谁身上。

```
❌ 错:`1girl, long purple hair, playful, 1boy, pink hair, embarrassed`
✅ 对:`On the left, a girl with long purple hair and violet eyes lifts the hem of her skirt with a mischievous smirk, while the boy beside her, pink-haired and flushed, looks away.`
```

- 一个角色一个从句,先写"谁+外观",再写"他/她在做什么";**同一句里只出现一个角色**,避免特征串味。
- 人称只用 `the girl` / `the boy` / `the woman` / `the man`,**不用 she/he/her/his**。
- 空间关系用 `on the left` / `behind her` / `facing each other` / `leaning over the bed` 这类词。
- 多人互动优先**第一人称视角**写法:只写 `a man's hands` / `a man's hips` 这类局部,把视觉重心留给女性角色。

### 4.5 观众关系(叙事性)

场景有剧情张力时,caption 末尾补一句观者关系,让画面"有对象感":

| 类型 | 末尾句示例 |
|---|---|
| 邀请/共犯 | `as if inviting the viewer to slip away with her` |
| 审判/对峙 | `her stare leveled at the viewer as if passing judgment` |
| 挑衅/诱惑 | `daring the viewer to come closer` |
| 求助/绝望 | `her eyes pleading with the viewer for help` |
| 羞耻/被注视 | `acutely aware of being watched` |
| 臣服/献身 | `offering herself entirely, head bowed` |

### 4.6 从 tag 思维翻译成句子(高频映射)

查库拿到的是 tag,落笔要变成英语描述。常见映射:

| 查到的 tag | caption 里写成 |
|---|---|
| `1girl, solo` | `A single young woman` |
| `long hair, black hair, blue eyes` | `with long black hair and blue eyes` |
| `school uniform, pleated skirt` | `wearing a navy school uniform with a pleated skirt` |
| `thighhighs, black thighhighs` | `black thigh-high stockings` |
| `partially undressed, shirt lift` | `her shirt rucked up, exposing her stomach` |
| `missionary, on back, spread legs` | `lying on her back with her legs apart as he moves above her` |
| `cowboy shot` | `framed from the thighs up` |
| `from above` | `seen from above` |
| `from behind` | `seen from behind` |
| `depth of field, blurry background` | `the background falling softly out of focus` |
| `backlighting, rim light` | `backlit, a bright rim outlining her shoulders` |

**要点**:tag 是名词索引,句子要补主语、动词、方位、材质;`masterpiece`/`best quality`/`score_7` 这类词**一个都不写**。

### 4.7 光影基调(必写,每张 1 处)

从 `tags/13` §13.5 取一个基调,写成一句话里的自然成分,不要生硬贴词:

- 黄昏逆光 → `warm dusk light spilling from behind her, edges glowing`
- 室内钨丝灯 → `a single warm tungsten bulb overhead`
- 雨夜霓虹 → `neon signs bleeding magenta and cyan across the wet street`
- 清晨窗光 → `soft morning light through a gauze curtain`
- 烛光 → `flickering candlelight from below`
- 冷白手术灯 → `flat clinical white light from directly overhead`

必须与时辰、情绪一致:深夜私密场景不要写"正午烈日",温馨场景不要写"惨白顶光"。

---

