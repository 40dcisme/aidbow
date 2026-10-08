"""Adapter 扩展点协议 —— 对齐 SPEC.md §2.2（HarnessContext 注入点）与 §3（覆盖机制）。

SPEC 只在 `HarnessContext.llm?: LLMAdapter` 处引用了 LLMAdapter，
本包补全其 Python 契约（零依赖，仅依赖 aidbow_core 的数据模型概念）。
"""
from __future__ import annotations
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class LLMAdapter(Protocol):
    """SPEC §2.2 `HarnessContext.llm` 注入点。

    约定：
    - `complete()` 是唯一必需方法：输入提示词，输出纯文本补全。
    - 实现必须可通过 `HarnessContext(llm=...)` 注入给 harness 使用；
      harness 步骤（如 brainstorm）在 `ctx.llm` 存在时调用它生成真实产出。
    - 密钥等凭据一律从环境变量读取，**禁止硬编码**（AGENTS.md §5 红线）。
    - 网络失败/未配置时抛出明确异常或返回显式错误标记，**不得编造内容**。
    """
    id: str
    def complete(self, prompt: str, *, system: str | None = None,
                 temperature: float = 0.7, max_tokens: int = 1024,
                 **opts: Any) -> str: ...


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
