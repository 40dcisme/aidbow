#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P 值体系演示（重点：P6 拆分为 P6-R1 / P6-R2）。

    python3 examples/run_pdemo.py

预期最后一行：✅ P-DEMO OK
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PKG = os.path.join(os.path.dirname(_HERE), "packages")
for _p in ["core", "p-system"]:
    sys.path.insert(0, os.path.join(_PKG, _p))

from aidbow_core import Idea, Demand          # noqa: E402
from aidbow_p_system import BasePEvaluator    # noqa: E402


def main():
    print("=" * 58)
    print("P 值体系演示 —— 重点看 P6 的双轮拆分")
    print("=" * 58)
    ev = BasePEvaluator()
    demand = Demand(id="d1", prompt="演示")

    print("\n[评委视角] BasePEvaluator().dimensions =", ev.dimensions)

    # R1：盲作轮 → 用 P6-R1（盲作独立度）
    r1 = Idea(id="A:01", author="a", round="R1", title="盲作创意", oneLiner="o",
              body="**正文**：" + "字" * 500, P={"P6-R1": 5, "P2": 4})
    # R2：递进轮 → 用 P6-R2（互文增量度）
    r2 = Idea(id="A-r2:01", author="a", round="R2", title="递进创意", oneLiner="o",
              body="**正文**：" + "字" * 900, P={"P6-R2": 4, "P2": 4})

    p1 = ev.evaluate(r1, demand); p2 = ev.evaluate(r2, demand)
    print("\nR1 创意 P 值：", p1.P)
    print("   → 含 P6-R1 =", p1.P.get("P6-R1"), "；不含 P6-R2 =", "P6-R2" not in p1.P)
    print("R2 创意 P 值：", p2.P)
    print("   → 含 P6-R2 =", p2.P.get("P6-R2"), "；不含 P6-R1 =", "P6-R1" not in p2.P)

    agg = ev.aggregate([r1, r2], demand)
    print("\n话题级聚合(n=%d) mean：%s" % (agg.n, agg.mean))

    assert p1.P.get("P6-R1") == 5 and p2.P.get("P6-R2") == 4
    assert p1.P.get("P3") == 3 or p1.P.get("P3") == 4     # 500 字 → P3
    print("\n" + "-" * 58)
    print("要点：R1 判「与同轮他人重合度」；R2 判「在 R1 之上新增机制占比」——")
    print("      旧 rubric 用同一个 P6 且要求『R2 盲作』，R2 实际不可达，故拆分修复。")
    print("✅ P-DEMO OK")


if __name__ == "__main__":
    main()
