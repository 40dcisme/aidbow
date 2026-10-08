# SPEC · aidbow Creative OS · 扩展点契约

> **本文件是开源框架与闭源精炼层之间的唯一接口契约。** 任何包、任何实现（开源基础版 / 闭源精炼版）都必须与本文对齐。
> 变更本文 = 破坏性变更，需走 semver major，并在 CHANGELOG 记录。
> **红线**：本仓（开源）不得出现精炼 P 体系 / 核心 Harness / 精炼提示词 / 客户资产 / 内部事件号。

## 0. 术语

| 术语 | 含义 |
|---|---|
| **Demand** | 用户的原始创意需求 + 上下文（DBOW 的 D） |
| **Idea** | 一次产出的一条创意（含正文 + P 值卡），DBOW 的 B/O 单位 |
| **Decision** | 人对一组 Idea 的取舍（选中/优先级/备注），驱动 W |
| **Workflow Spec** | 由 Decision 生成、可交给执行器的工作流关键指令（DBOW 的 W） |
| **Package** | 一个可独立版本化的能力单元（`@aidbow/<name>`） |

## 1. 数据模型（语言无关，实现可用 JSON 序列化）

```ts
type Demand = {
  id: string;                 // 调用方生成，全局唯一
  prompt: string;             // 创意需求原文
  context?: ContextBundle;    // 可选：上下文材料
  constraints?: string[];     // 约束（品牌调性/禁项/预算…）
  targets?: Partial<Record<"P1"|"P2"|"P3"|"P4"|"P5"|"P6"|"P7", number>>; // 目标 P 值
};

type ContextBundle = {
  items: ContextItem[];
};
type ContextItem = {
  kind: "text" | "link" | "file" | "dataset";
  ref: string;                // 内容或来源引用（本地路径 / URL / 内联）
  meta?: Record<string, string>;
};

type Idea = {
  id: string;                 // `<agent>:<n>` 或调用方自定义
  author: string;             // 生成者标识（开源匿名化；闭源可填真名）
  round: "R1" | "R2";         // 盲作轮 / 递进轮
  title: string;
  oneLiner: string;           // 一句话核心
  body: string;               // 正文
  P: Partial<Record<"P1"|...|"P7", number>>;
  basis?: Partial<Record<"P1"|...|"P7", string>>;  // 各 P 值的判定依据
  lineage?: { from: string; mode: "graft"|"rebut"|"combine"|"deepen" }; // R2 递进来源
};

type Decision = {
  demandId: string;
  selected: string[];                                   // 选中的 Idea.id
  priorities?: Record<string, "P0"|"P1"|"P2"|"shelved">;
  notes?: Record<string, string>;
};

type WorkflowSpec = {
  demandId: string;
  steps: { title: string; instruction: string; inputs?: string[]; outputs?: string[] }[];
  sourceIdeas: string[];
};
```

## 2. 扩展点接口（**四接口，必须逐字对齐**）

### 2.1 `PEvaluator` — P 值引擎（`@aidbow/p-system`）

```ts
interface PEvaluator {
  /** 该实现覆盖的 P 维度（开源基础版：P1–P7 全量基础定义） */
  readonly dimensions: PKey[];
  /** 对单条创意打分；返回 score(0–5) 与 basis（判定依据，禁止编造） */
  evaluate(idea: Idea, demand: Demand, ctx?: EvalContext): PResult;
  /** 组合多条创意的 P 值（话题级/组级统计） */
  aggregate(ideas: Idea[], ctx?: EvalContext): PAggregate;
}
type PKey = "P1"|"P2"|"P3"|"P4"|"P5"|"P6"|"P7";
type PResult = { P: Partial<Record<PKey, number>>; basis: Partial<Record<PKey, string>> };
type PAggregate = { mean: Partial<Record<PKey, number>>; n: number };
```

> **闭源覆盖**：实现同一 `PEvaluator`，`dimensions` 可增维（如 `P6-R1`/`P6-R2`）。允许在构造时注入**项目级 rubric 覆盖**（目录级 or 配置级）。

### 2.2 `Harness` — 流程编排（`@aidbow/harness`）

```ts
interface Harness {
  readonly stages: HarnessStage[];        // 默认：demand→brainstorm→overview→workflow
  /** 执行整条流水线；每步可被替换/包裹（见 StepContract） */
  run(demand: Demand, ctx: HarnessContext): Promise<HarnessResult>;
}
interface HarnessStage {
  key: "demand"|"brainstorm"|"overview"|"workflow"|string;
  /** 可替换步骤：闭源提供精炼实现，签名一致即可换入 */
  step: StepContract;
}
interface StepContract {
  name: string;
  run(input: unknown, ctx: HarnessContext): Promise<unknown>;
}
interface HarnessContext {
  evaluator?: PEvaluator;
  context?: ContextProvider;
  llm?: LLMAdapter;
  logger?: (evt: string, data?: unknown) => void;
}
```

> **闭源覆盖**：提供精炼 `StepContract` 实现或整套 `Harness`，通过 `HarnessContext` 注入；**不 fork 开源代码**。

### 2.3 `ContextProvider` — 上下文解析（`@aidbow/context`）

```ts
interface ContextProvider {
  readonly id: string;
  /** 判定能否处理某来源（URL/文件/数据集…） */
  canHandle(item: ContextItem): boolean;
  /** 解析为可注入提示的结构化上下文 */
  resolve(item: ContextItem, ctx?: unknown): Promise<ResolvedContext>;
}
type ResolvedContext = { text: string; citations?: string[]; meta?: Record<string, unknown> };
```

> 基础版工具集：文本内联、URL 抓取、本地文件。闭源可注册垂类 provider（如 api.aidbow.com 深度调研）。

### 2.4 Prompt 覆盖（`@aidbow/prompts`）

```ts
interface PromptPack {
  id: string;                                  // 基础包: "base"
  templates: Record<string, string>;           // 名称→模板文本
  get(name: string, vars?: Record<string,string>): string;
}
```
> **覆盖机制**：解析顺序 `项目覆盖目录 → 基础包`（同名覆盖）。闭源把精炼提示词放覆盖目录，不改开源默认包。

## 3. 覆盖 / 扩展机制（**不 fork**）

| 扩展点 | 开源提供 | 闭源覆盖方式 |
|---|---|---|
| P 引擎 | `PEvaluator` 基础实现 | 实现接口 + 增维 + 项目 rubric 注入 |
| Harness | 基础 `Harness`/步骤 | 注入精炼 `StepContract` 或整套 |
| 提示词 | `base` PromptPack | 目录覆盖（同名优先） |
| 上下文源 | 基础 Provider 集 | 注册垂类 Provider（`canHandle`） |
| 适配器 | 通用 LLM/检索适配器 | 项目专属适配器（同一接口） |

**兼容性保证（契约测试）**：CI 对每个公开发布物跑「接口签名 + 冒烟」一致性测试；任何接口变更即 major。

## 4. 包清单与依赖方向

```
adapters ──▶ (被 context/harness 使用)
context  ──▶ core(数据模型)
p-system ──▶ core(数据模型)
prompts  ──▶ (无依赖，纯文本)
harness  ──▶ core + p-system + context + adapters (可选注入)
core     ──▶ (无依赖，仅数据模型 + 编排接口)
review-ui──▶ core(数据模型)
```
> 依赖只能**向下**；`core` 不依赖任何包（保证可独立使用）。

## 5. 版本与兼容

- 语义化版本；`packages/*` 各自版本，仓级用 workspace。
- 扩展点接口的**任何破坏性改动** = major，且须同步更新本文件与 CHANGELOG。

---
*Aidbow · 本文件为开源框架的接口契约（G1）。*
