"""跨包集成冒烟：core + p-system + prompts + harness 串起来。"""
import sys, os
_here = os.path.dirname(__file__)
_P = os.path.join(_here, "..", "packages")
for sub in ["core", "p-system", "prompts", "harness"]:
    sys.path.insert(0, os.path.join(_P, sub))
from aidbow_core import Demand, Idea, Decision, PEvaluator, PromptPack, Harness
from aidbow_p_system import BasePEvaluator
from aidbow_prompts import BasePromptPack
from aidbow_harness import BaseHarness

def test_full_stack_wiring():
    ev = BasePEvaluator()
    pk = BasePromptPack()
    h = BaseHarness(evaluator=ev)
    # 契约一致
    assert isinstance(ev, PEvaluator) and isinstance(pk, PromptPack) and isinstance(h, Harness)
    # 一条创意的端到端 P 判定
    idea = Idea(id="a:1", author="anon", round="R1", title="t", oneLiner="o",
                body="**正文**：" + "字"*500, P={"P4": 3, "P6-R1": 4})
    res = ev.evaluate(idea, Demand(id="d1", prompt="p"))
    assert res.P["P3"] == 3 and res.P["P6-R1"] == 4
    # 编排跑通
    out = h.run(Demand(id="d1", prompt="p"))
    assert out["trace"] == ["demand","brainstorm","overview","workflow"]
    # 提示词可用
    assert "编造" in pk.get("synthesize")
