## 4. SLOT ORDER

标签填充必须严格按以下槽位顺序。靠前的槽位权重更高，把最重要的视觉元素放在前面。

```
[count/gender] → [character/series] → [appearance] → [clothing/state] → [pose/action/sex] → [expression/reaction] → [camera/shot] → [scene/environment] → [detail/mood] → [natural language: 关系/动作/剧情补充]
```

### 4.1 风格一致性强调

> ⚡ **跨槽位风格一致性铁律**：clothing、scene、detail/mood 不能出现逻辑矛盾。基本原则——古风配古风（如 `hanfu` + `ancient shrine` + 水墨空灵），赛博配赛博（如 `latex bodysuit` + `cyberpunk city` + 数字故障），日常配日常（如 `school uniform` + `classroom` + 自然质感）。不要出现 `hanfu` 站在 `cyberpunk city` 里、`latex catsuit` 配 `ancient temple` 这类跨世界观的矛盾组合。同一世界观内不同场景的混搭（如 `kimono` + `love hotel`）属于合理。

> ⚠️ **特殊主题速查**：以下场景需额外参考 **§14 SPECIAL THEME** 获取跨槽位核心标签与专属氛围链——NTR、束缚 BDSM、RBQ/物化、男娘 Futa、睡奸、过激、调戏猥亵、调教宠物、胁迫、偷窥展示、事后、另类日常、大车小孩、攻守反转。匹配到特殊主题时，先在 §14 查配方，再按本槽位顺序逐槽填充。

### 4.2 TAG COUNT CONTROL

> 基于法典4345条实战prompt的统计：平均23.4标签，中位数21，P75=29，P90=36。

| 场景复杂度 | 总标签数 | 说明 |
|---|---|---|
| 简单（单人展示/诱惑/暴露/自慰） | 16-30 | 外貌+服装+姿态+场景，维度少 |
| 标准（双人性交/前戏） | 22-38 | 体位+表情+液体为核心，服装维度膨 |
| 复杂（多人/特殊主题/剧情主视觉） | 30-48 | 跨槽位多，服装改造+液体+混池 |

**每槽位标签数指引**：

| 槽位 | 最少 | 最多 | 说明 |
|---|---|---|---|
| count/gender | 2 | 4 | 固定格式，不可省略 |
| character/series | 0 | 2 | 仅 IP 角色使用 |
| appearance | 3 | 8 | 头发2+眼睛1+体型1+肤色1+非人特征/标记按需 |
| clothing/state | 2 | 10 | 基础服装+材质+1-3个改造维度+丝袜鞋类——本槽位天然标签多 |
| pose/action/sex | 2 | 8 | 核心体位2个+辅助动作+变体维度 |
| expression/reaction | 1 | 4 | 主表情1个+最多3个身体反应/液体 |
| camera/shot | 1 | 5 | 景别必填，角度/POV按需 |
| scene/environment | 2 | 6 | 主场所+环境元素+时辰/天气 |

**原则**：服装槽位天然标签多——基础服装+材质+改造维度（1-3方向可叠加）+丝袜鞋类。其他槽位保持精简，通过维度组合产生多样性，而非堆砌标签。靠前的槽位权重更高。同一身体部位不堆叠矛盾状态标签（见 §3.1 细节标签过度）。

### 4.3 视线方向默认规则

**单人场景**：除非用户明确要求「背影/背对/转身离开/侧脸/profile/from behind」，否则必须注入 `direct eye contact, facing viewer`。该标签放在 expression 槽末尾或 camera 槽开头均可。

**两人及以上场景**：不强制注入 `direct eye contact`。根据角色间互动关系选择合适的视线标签（如 `looking at another`），或由用户明确指定。

| 用户意图 | 适用 | 输出 |
|---|---|---|
| 未指定/正面（单人） | solo | `direct eye contact, facing viewer` |
| 回头（浪漫） | solo | `turning around, direct eye contact` |
| 回眸（肩头） | solo | `over shoulder, direct eye contact` |
| 背对/远去 | 通用 | `from behind, facing away` |
| 侧脸 | 通用 | `profile, from side` |
| 角色间互动（多人） | 2 人+ | `looking at another` |

### 4.4 自然语言使用场景及具体写法

**核心原则**：tag 为主，自然语言仅在 tag 无法准确表达时使用。**自然语言短句统一放在 prompt 末尾，所有 tag 之后。**

**必须使用自然语言的场景**：

| 场景 | 原因 | 示例（放在末尾） |
|---|---|---|
| 角色间动作关系 | 标签无法描述"谁对谁做什么" | `one reaches toward the viewer while the other watches in silence` |
| 复杂构图/空间关系 | 标签无法描述"谁在哪、面向谁" | `girl sitting on boy's lap facing him` |
| 特殊姿势组合 | 多个动作标签堆叠时主次不清 | `girl pinning wolf boy down while riding him` |
| 分镜/对比关系 | 标签无法表达时间或状态对比 | `left panel: dressed, right panel: nude` |

**格式规则**：
- 自然语言短句统一放在 prompt 末尾（所有 tag 之后），与 tag 用逗号分隔
- 保持简洁，一个短句解决一个歧义，不写长段落

### 4.5 观众关系（叙事性互动）

当场景具有剧情性时，除了视线方向，**必须**用自然语言（放末尾）描述角色与观众的叙事关系：

| 类型 | 末尾自然语言示例 |
|---|---|
| 邀请/共犯 | `as if inviting the viewer to escape together` |
| 审判/对峙 | `as if judging the viewer` |
| 托付/交接 | `as if handing the last hope to the viewer` |
| 挑衅/诱惑 | `as if daring the viewer to come closer` |
| 求助/绝望 | `as if begging the viewer for help` |
| 炫耀/NTR | `as if showing off to the viewer what they can't have` |
| 羞耻/被注视 | `as if aware of being watched by the viewer` |
| 臣服/献身 | `as if offering herself entirely to the viewer` |

### 4.6 多人场景角色规则

**极重要**：多人场景中，只写角色名而不补外观会导致模型混淆，**必须为每个角色补充关键外观描述**。

- 结构：人数 → 角色 A 的外观短语 → 角色 B 的外观短语 → 共享 tag（体位、镜头、场景等） → 关系/动作/剧情描述（自然语言，放末尾）
- 每个角色的外观用简短描述词组（`角色名 with 发色 + 瞳色 + 关键特征`），不要把动作表情混入
- 动作、关系、剧情等需要自然语言表达的内容，统一放在 prompt 末尾

**示例**：
- ❌ 错误：`raiden shogun, long purple hair, playful, yae miko, pink hair, embarrassed, skirt lift`（模型无法判断属性归属）
- ✅ 正确：`2girls, raiden shogun with long purple hair and purple eyes, yae miko with long pink hair and fox ears, skirt lift, shrine, one playfully lifting the other's skirt with a mischievous smirk while the other looks shy and embarrassed`

---

