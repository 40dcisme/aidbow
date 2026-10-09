# -*- coding: utf-8 -*-
"""跨包集成测试：adapters 必须能被 harness 的 LLM 路径实际注入。

这正是此前缺失的验收——单包测试全绿，但 adapters 的 `complete()` 与 core 的
`generate()` 不一致，导致注入 harness 时 AttributeError（合并时未发现）。
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_P = os.path.dirname(_HERE)
for sub in ["core", "p-system", "prompts", "harness", "adapters", "context"]:
    sys.path.insert(0, os.path.join(_P, "packages", sub))

from aidbow_core import LLMAdapter, Idea, Demand, PromptPack, ContextProvider, ContextItem  # noqa: E402
import aidbow_adapters as AD                                                    # noqa: E402
import aidbow_context as CT                                                     # noqa: E402
from aidbow_harness import BaseOverviewLLM                                      # noqa: E402
from aidbow_prompts import BasePromptPack                                       # noqa: E402


def test_adapter_satisfies_core_llm_protocol():
    assert isinstance(AD.MockLLMAdapter(), LLMAdapter)


def test_adapter_injects_into_harness_llm_path():
    """关键回归：MockLLMAdapter 必须能被 BaseOverviewLLM 实际调用（不 AttributeError）。"""
    class JSONLLM(AD.MockLLMAdapter):
        def complete(self, prompt, **kw):
            return '{"clusters":[],"conflicts":[],"shortlist":[],"open_questions":[],"warnings":[]}'
    s = BaseOverviewLLM(JSONLLM(), prompts=BasePromptPack())
    r = s.summarize([Idea(id="x:1", author="a", round="R1", title="t",
                          oneLiner="o", body="b", P={})], Demand(id="d", prompt="p"))
    assert r.method == "llm"


def test_context_provider_satisfies_core_protocol():
    assert isinstance(CT.TextProvider(), ContextProvider)


def test_end_to_end_adapters_plus_context():
    reg = CT.ContextRegistry()
    rc = reg.resolve(ContextItem(kind="text", ref="上下文"))
    assert rc.text == "上下文"
