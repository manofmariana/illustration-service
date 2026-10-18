## 3. FINAL SELF-CHECK

prompt 组装完成后，提交前必须过以下清单：

| # | 检查项 | 通过标准 |
|---|---|---|
| 1 | **人数一致性** | `count/gender` 标签数量与实际角色数一致，无 `1boy,2boys` 等矛盾 |
| 2 | **互斥冲突** | 对照 §3.1 互斥表，无视角/身份/服装/动作/细节标签矛盾 |
| 3 | **重复标签** | 同一标签不出现两次（强调应靠位置权重，不靠重复） |
| 4 | **场景合理性** | 场景标签与动作标签物理兼容（如 `underwater` 不能配 `cigarette`） |
| 5 | **光影基调** | 恰含 1 个光影基调词（见 `tags/13` §13.5），且与场景时辰/情绪一致 |
| 6 | **标签总数** | 在 §4.2 规定的复杂度范围内（单人 16-30 / 双人 22-38 / 复杂 30-48） |
| 7 | **遮挡一致性** | 视角/姿势导致某部位不可见时（如土下座俯视只见背面、低头掩面、背身），不得出现对该部位的描述词（脸→不得写 eyes/表情/笑容；胸→不得写 breasts 等）；按需用 `face_hidden`、`hiding face` 等遮挡 tag 或自然语言补充遮挡事实 |

**自检流程**：组装完 → 逐项打勾 → 有冲突回退修改 → 全部通过才提交。

---

## 3.1 CONFLICT TABLE

以下标签对**不可同时出现**，AI 必须在组装时检查冲突：

### 视角互斥

| 标签A | 标签B | 原因 |
|---|---|---|
| `from front` | `from behind` | 物理矛盾 |
| `from above` | `from below` | 物理矛盾 |
| `looking at viewer` | `facing away` | 视线矛盾 |
| `pov` | `full body` | POV 不可能看到自己全身 |
| `close-up` | `full body` | 景别矛盾 |

### 身份互斥

| 标签A | 标签B | 原因 |
|---|---|---|
| `solo` | `hetero` / `1boy` / `yuri` | 单人不存在互动 |
| `femdom` | `male-on-female rape` | 逻辑矛盾（主导方冲突） |
| `sleeping` / `unconscious` | `looking at viewer` | 无意识不可能直视 |
| `blindfold` | `heart-shaped pupils` / `rolling eyes` | 看不到眼睛 |

### 服装互斥

| 标签A | 标签B | 原因 |
|---|---|---|
| `completely nude` | 任何具体服装标签 | 全裸不穿衣 |
| `pantyhose` | `barefoot` | 穿了丝袜不可能光脚（除非 `torn pantyhose`） |
| `blindfold` | `glasses` | 物理冲突 |
| 内衣套装 (`cat lingerie`, `lace lingerie`, `babydoll`, `negligee`, `chemise` 等) | `no panties` / `bottomless` | 内衣套装隐含包含内裤，模型优先解析套装忽略暴露标签；需暴露时拆为单件（`cat bra` + `no panties`） |

> **不互斥**：外衣/制服（`maid outfit`、`school uniform`、`bunny suit`、`sailor uniform` 等）与 `no panties` / `bottomless` 完全兼容——穿制服不穿内裤 = 合理场景。

### 动作互斥

| 标签A | 标签B | 原因 |
|---|---|---|
| `standing sex` | `lying` / `on back` | 体位矛盾 |
| `missionary` | `doggystyle` | 不可能同时两个体位 |
| `cowgirl position` | `prone bone` | 体位矛盾 |
| `fellatio` | `cunnilingus`（同一人执行） | 嘴只有一张 |

### 细节标签过度

同一身体部位同时堆叠多个细节标签会导致模型过度渲染，产生畸形。**每部位细节标签 ≤2 个，且不能互斥。**

| 部位 | 矛盾组合 | 原因 |
|---|---|---|
| 脚趾 | `spread toes` + `toe scrunch` / `toes curling` | 舒展 vs 蜷缩，物理矛盾 |
| 脚趾 | `spread toes` + `feet together` | 分趾需要空间，合拢则压缩 |
| 手指 | `spread fingers` + `clenched fist` / `gripping` | 张开 vs 握拳 |
| 胸部 | `bouncing breasts` + `breasts squeeze together` | 弹跳 vs 挤压，动态矛盾 |
| 嘴巴 | `open mouth` + `clenched teeth` / `closed mouth` | 张嘴 vs 闭嘴 |
| 眼睛 | `rolling eyes` + `looking at viewer` | 翻白眼 vs 直视 |
| 腿部 | `spread legs` + `legs together` | 分开 vs 并拢 |
| 足部整体 | 3 个以上足部标签（如 `foot focus` + `footjob` + `toe scrunch` + `spread toes`） | 过度细化导致脚趾/脚掌畸形 |

**原则**：同一部位的状态标签可以多个，但不能互斥。`barefoot` + `feet focus` + `soles` + `toe scrunch` 四个兼容标签没问题；`spread toes` + `toe scrunch` 两个就矛盾。关键在于**状态一致性**而非数量。

**例外**：`torn pantyhose` + `barefoot`（脚部撕开）、`partially undressed` + 具体服装（半脱状态）属于合理组合。

---

