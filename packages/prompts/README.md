# @aidbow/prompts

> 基础提示词包（实现 `aidbow_core.PromptPack`）。**抗幻觉 + 跨专业一致性**基线。

**状态**：✅ v0.1.0

## 模板
| 名称 | 用途 |
|---|---|
| `decompose` | D 需求拆解 |
| `brainstorm` | B 头脑风暴（含跨域待核） |
| `synthesize` | O 汇总收敛（**抗幻觉 + 跨专业冲突显式标记**） |
| `workflow` | W 工作流指令生成 |

## 覆盖（SPEC §3）
`BasePromptPack(overlay_dir=...)`：项目覆盖目录 → base（同名覆盖）。闭源精炼提示词放覆盖目录，**不改 base**。
