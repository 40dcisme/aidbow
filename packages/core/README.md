# @aidbow/core

> DBOW 编排层地基：数据模型 + 扩展点协议（**零依赖**）。

**状态**：✅ v0.1.0

## 内容
- `aidbow_core/models.py` — Demand / Idea / Decision / WorkflowSpec / ContextBundle（对齐 SPEC §1）
- `aidbow_core/interfaces.py` — `PEvaluator` / `ContextProvider` / `PromptPack` / `StepContract` / `Harness`（对齐 SPEC §2）

## 快速开始
```python
from aidbow_core import Demand, Idea, PEvaluator
d = Demand(id="d1", prompt="给独立游戏做零预算宣发")
idea = Idea(id="a:1", author="anon", round="R1", title="t", oneLiner="o", body="...")
```

## 归属
开源基础能力。**零依赖**（SPEC §4：core 不依赖任何包）。
