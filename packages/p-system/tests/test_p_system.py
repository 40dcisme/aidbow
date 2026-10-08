import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "core"))
from aidbow_core import Idea, PEvaluator
from aidbow_p_system import BasePEvaluator, RUBRIC, P_KEYS
from aidbow_p_system.evaluator import count_body_chars, p3_score

def _idea(body, rnd="R1", P=None):
    return Idea(id="t:1", author="a", round=rnd, title="t", oneLiner="o", body=body, P=P or {})

def test_implements_pevaluator():
    assert isinstance(BasePEvaluator(), PEvaluator)

def test_p3_computed_and_codeblock_excluded():
    body = "**正文**：" + "甲"*500 + "\n```代码不算字数```"
    n = count_body_chars(body)
    assert 495 <= n <= 505, n
    assert p3_score(n) == 3

def test_p6_split_by_round():
    e = BasePEvaluator()
    r1 = e.evaluate(_idea("**正文**："+"x"*500, rnd="R1", P={"P6-R1": 5}))
    r2 = e.evaluate(_idea("**正文**："+"x"*500, rnd="R2", P={"P6-R2": 4}))
    assert r1.P.get("P6-R1") == 5 and "P6-R2" not in r1.P
    assert r2.P.get("P6-R2") == 4 and "P6-R1" not in r2.P

def test_aggregate():
    e = BasePEvaluator()
    agg = e.aggregate([_idea("**正文**："+"x"*500, P={"P4":3}), _idea("**正文**："+"x"*900, P={"P4":5})])
    assert agg.n == 2 and "P3" in agg.mean and "P4" in agg.mean

def test_rubric_has_split_p6():
    assert "P6-R1" in RUBRIC and "P6-R2" in RUBRIC and "P6" not in RUBRIC
