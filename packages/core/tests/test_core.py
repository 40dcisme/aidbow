"""core 单测（零依赖，无 pytest 也可跑）。"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from aidbow_core import (Demand, Idea, Decision, WorkflowSpec, ContextBundle, ContextItem,
                         PEvaluator, ContextProvider, PromptPack, StepContract, Harness)

def test_models_serialize():
    d = Demand(id="d1", prompt="p",
               context=ContextBundle(items=[ContextItem(kind="link", ref="http://x")]),
               constraints=["no-ads"], targets={"P2": 4})
    dd = d.to_dict()
    assert dd["id"] == "d1" and dd["context"]["items"][0]["kind"] == "link"

def test_idea_p_and_basis():
    i = Idea(id="a:1", author="anon", round="R1", title="t", oneLiner="o", body="b",
             P={"P3": 3}, basis={"P3": "字数=500"})
    assert i.to_dict()["P"]["P3"] == 3

def test_decision_workflowspec():
    dec = Decision(demandId="d1", selected=["a:1"], priorities={"a:1": "P0"}, notes={"a:1": "好"})
    wf = WorkflowSpec(demandId="d1", steps=[{"title": "s", "instruction": "do"}], sourceIdeas=["a:1"])
    assert dec.to_dict()["priorities"]["a:1"] == "P0" and wf.to_dict()["sourceIdeas"] == ["a:1"]

def test_protocols_runtime_checkable():
    class PE:
        dimensions = ["P3"]
        def evaluate(self, idea, demand, ctx=None): ...
        def aggregate(self, ideas, ctx=None): ...
    assert isinstance(PE(), PEvaluator)
