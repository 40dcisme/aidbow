# -*- coding: utf-8 -*-
"""Overview 自动化双路径测试：LLM / Agent（同一 OverviewResult 契约）。"""
import sys, os, json
_P = os.path.join(os.path.dirname(__file__), "..", "..")
for sub in ["core", "p-system", "prompts", "harness"]:
    sys.path.insert(0, os.path.join(_P, sub))
from aidbow_core import Idea, Demand, LLMAdapter, AgentAdapter, OverviewResult
from aidbow_p_system import BasePEvaluator
from aidbow_prompts import BasePromptPack
from aidbow_harness import BaseHarness, BaseOverviewLLM, AgentOverview


def _ideas():
    return [
        Idea(id="a:1", author="a", round="R1", title="辩题保险库", oneLiner="把备题资产化",
             body="**正文**：" + "字"*450, P={"P4": 4}),
        Idea(id="a:2", author="b", round="R1", title="立场状态机", oneLiner="带阻尼的倒戈",
             body="**正文**：" + "字"*500, P={"P4": 3}),
    ]


class MockLLM(object):
    id = "mock-llm"
    def generate(self, prompt, model=None):
        # 模拟 LLM 返回合规 JSON（带 idea_id 溯源 + 一处跨域冲突）
        return json.dumps({
            "clusters": [{"label": "内核", "note": "把内容资产化", "idea_ids": ["a:1", "a:2"]}],
            "conflicts": [{"term": "阻尼", "statements": [
                {"idea_id": "a:2", "claim": "阻尼指回弹力"}, {"idea_id": "a:1", "claim": "阻尼指热度衰减"}]}],
            "shortlist": [{"idea_id": "a:2", "why": "可直接文字流验证"}],
            "open_questions": ["阻尼的量化口径？"], "warnings": ["a:1 正文含代码块已剔除"],
        })


class MockAgent(object):
    id = "mock-agent"
    def review(self, ideas, demand, **kw):
        return {"clusters": [{"label": "内核", "idea_ids": [i.id for i in ideas]}],
                "shortlist": [{"idea_id": ideas[0].id, "why": "agent 读整包后推荐"}],
                "conflicts": [], "open_questions": [], "warnings": ["由 agent 直读上下文"]}


def test_llm_path_returns_overviewresult():
    s = BaseOverviewLLM(MockLLM(), prompts=BasePromptPack())
    r = s.summarize(_ideas(), Demand(id="d1", prompt="p"))
    assert isinstance(r, OverviewResult) and r.method == "llm"
    assert r.clusters and r.clusters[0].idea_ids == ["a:1", "a:2"]
    assert r.conflicts and r.conflicts[0].term == "阻尼"       # 跨专业冲突显式标记
    assert r.provenance.get("model") == "mock-llm"


def test_llm_adapter_protocol():
    assert isinstance(MockLLM(), LLMAdapter)


def test_agent_path_returns_overviewresult():
    s = AgentOverview(MockAgent())
    r = s.summarize(_ideas(), Demand(id="d1", prompt="p"))
    assert isinstance(r, OverviewResult) and r.method == "agent"
    assert r.shortlist and r.shortlist[0]["idea_id"] == "a:1"
    assert r.provenance.get("agent") == "mock-agent"


def test_agent_adapter_protocol():
    assert isinstance(MockAgent(), AgentAdapter)


def test_harness_wires_summarizer_into_overview():
    # 注入 LLM summarizer → 编排的 overview 步骤自动产出 OverviewResult
    s = BaseOverviewLLM(MockLLM(), prompts=BasePromptPack())
    class BrainstormWithIdeas(object):
        name = "brainstorm"
        def run(self, input, ctx):
            dem = input if not isinstance(input, dict) else input.get("demand")   # 首阶段收 Demand，后续收 dict
            return {"demand": dem, "ideas": _ideas()}
    hh = BaseHarness(evaluator=BasePEvaluator(), summarizer=s,
                     overrides={"brainstorm": BrainstormWithIdeas()},
                     stages=[("brainstorm", BrainstormWithIdeas()), ("overview",
                             __import__("aidbow_harness").OverviewStep())])
    out = hh.run(Demand(id="d1", prompt="p"))
    assert out["result"]["overview"].method == "llm"
    assert out["result"]["overview"].clusters
