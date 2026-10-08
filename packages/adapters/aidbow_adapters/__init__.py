"""aidbow_adapters — 可插拔适配器（LLM provider / 检索 / 上下文源）。

契约：SPEC.md §2.2 `HarnessContext.llm`（LLMAdapter）+ §3 覆盖机制。
零第三方运行时依赖；密钥一律走环境变量。
"""
from .interfaces import LLMAdapter, RetrievalAdapter
from .mock import MockLLMAdapter, MockRetrievalAdapter
from .openai_compat import OpenAICompatAdapter, AdapterNotConfigured, AdapterRequestError

__all__ = [
    "LLMAdapter", "RetrievalAdapter",
    "MockLLMAdapter", "MockRetrievalAdapter",
    "OpenAICompatAdapter", "AdapterNotConfigured", "AdapterRequestError",
]
__version__ = "0.1.0"
