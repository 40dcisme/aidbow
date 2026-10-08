import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "core"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "p-system"))
from aidbow_core import Demand, Idea, Harness, HarnessContext
from aidbow_p_system import BasePEvaluator
from aidbow_harness import BaseHarness

def test_implements_harness():
    assert isinstance(BaseHarness(), Harness)

def test_end_to_end_with_mock_steps():
    logged = []
    h = BaseHarness(evaluator=BasePEvaluator(), logger=lambda e,d=None: logged.append(e))
    out = h.run(Demand(id="d1", prompt="零预算宣发"))
    assert out["trace"] == ["demand","brainstorm","overview","workflow"]
    assert "demand.start" in logged and "brainstorm.start" in logged

def test_step_override_contract():
    from aidbow_core import StepContract
    class MyDemand:
        name = "demand"
        def run(self, input, ctx): return {"demand": input, "brief": "OVERRIDDEN"}
    assert isinstance(MyDemand(), StepContract)
    # 单阶段运行，验证替换步骤确实被调用（全流水线时 result 是最后一步输出）
    h = BaseHarness(stages=[("demand", MyDemand())])
    out = h.run(Demand(id="d1", prompt="x"))
    assert out["result"]["brief"] == "OVERRIDDEN" and out["trace"] == ["demand"]

def test_overview_aggregates_with_injected_evaluator():
    h = BaseHarness(evaluator=BasePEvaluator())
    out = h.run(Demand(id="d1", prompt="x"))
    assert out["trace"][2] == "overview"
