# @aidbow/p-system

> P 值引擎（基础版）：实现 `aidbow_core.PEvaluator`。**P6 已拆为 P6-R1 / P6-R2**。

**状态**：✅ v0.1.0

## 关键设计
- **P3 篇幅**：可计算，口径 `**正文**:` 锚 + 剔除代码块（与既有计数口径一致）。
- **P6 拆分**（修正已实证的 rubric 缺陷）：R1 判「盲作独立度」，R2 判「互文增量度」，不再要求 R2 盲作。
- **闭源覆盖**：构造时传 `rubric=` 注入项目级精炼 rubric，**不 fork**。

## 快速开始
```python
from aidbow_p_system import BasePEvaluator
e = BasePEvaluator()            # 或 BasePEvaluator(rubric=custom)
print(e.evaluate(idea).P)
```
