"""Adapter 扩展点协议 —— 对齐 SPEC.md §2.2（HarnessContext 注入点）与 §3（覆盖机制）。

SPEC 只在 `HarnessContext.llm?: LLMAdapter` 处引用了 LLMAdapter，
本包补全其 Python 契约（零依赖，仅依赖 aidbow_core 的数据模型概念）。
"""
from __future__ import annotations
from typing import Any, Protocol, runtime_checkable


# ⚠️ LLMAdapter 契约以 @aidbow/core 为唯一真源（SSOT）。
# 本包此前另立 `complete()` 契约，与 core 的 `generate()` 方法名不一致，
# 导致实现**无法注入** harness（BaseOverviewLLM 调 llm.generate → AttributeError）。
# 现直接复用 core 的协议，实现须提供 `generate(prompt, **kwargs)`。
try:
    from aidbow_core import LLMAdapter  # noqa: F401  (SSOT)
except Exception:  # 无 core 时的等价兜底（保持方法名一致）
    @runtime_checkable
    class LLMAdapter(Protocol):
        id: str
        def generate(self, prompt: str, **kwargs: Any) -> str: ...


@runtime_checkable
class RetrievalAdapter(Protocol):
    """检索适配器：把查询解析为可注入提示的参考文本片段。

    与 `ContextProvider`（SPEC §2.3，@aidbow/context）互补：
    ContextProvider 面向「结构化来源条目」，RetrievalAdapter 面向「自由查询 → 片段」。
    """
    id: str
    def search(self, query: str, *, top_k: int = 5, **opts: Any) -> list[dict[str, Any]]:
        """返回 [{text, score, source}] 列表；无结果返回空列表（不编造）。"""
        ...


__all__ = ["LLMAdapter", "RetrievalAdapter"]
