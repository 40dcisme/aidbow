# @aidbow/harness

> DBOW 编排：`demand → brainstorm → overview → workflow`，**步骤可替换**（实现 `aidbow_core.Harness`）。

**状态**：✅ v0.1.0

## 可替换步骤（SPEC §2.2）
```python
from aidbow_harness import BaseHarness
h = BaseHarness(evaluator=my_evaluator, overrides={"brainstorm": MyRefinedStep()})
h.run(demand)
```
闭源精炼层注入 `overrides` 或整套 `stages`，**不 fork**。

## 阶段入参约定（重要）
- **首个阶段**收到原始 `Demand` 对象；**后续阶段**收到上一阶段返回的 `dict`。
- 因此自定义步骤应写成：`dem = input if not isinstance(input, dict) else input.get("demand")`。

## Overview 自动化（人审之外的两条路径）
`BaseHarness(summarizer=...)` 注入后，`overview` 步骤自动产出 `OverviewResult`（同一契约）：
```python
from aidbow_harness import BaseHarness, BaseOverviewLLM, AgentOverview
h1 = BaseHarness(evaluator=ev, summarizer=BaseOverviewLLM(llm, prompts=pack))   # LLM 路径
h2 = BaseHarness(evaluator=ev, summarizer=AgentOverview(another_agent))        # Agent 路径
```
两条路径都**只归纳实际出现内容、必须带 idea_id 溯源、跨专业冲突显式标记**（conflicts），不编造。
