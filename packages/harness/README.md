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
