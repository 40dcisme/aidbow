#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aidbow DBOW 端到端最小示例 —— 零配置、零第三方依赖、无需联网。

运行：
    python3 examples/run_demo.py

它会走完整条 DBOW 链路：
    Demand(需求) → Brainstorm(创意) → Overview(汇总) → Decision(决策) → Workflow(工作流指令)
并打印结果。最后一行应为：

    ✅ DEMO OK
"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PKG = os.path.join(os.path.dirname(_HERE), "packages")
for _p in ["core", "p-system", "prompts", "harness", "adapters"]:
    sys.path.insert(0, os.path.join(_PKG, _p))

from aidbow_core import (Demand, Idea, Decision, ContextBundle, ContextItem,
                         OverviewResult)          # noqa: E402
from aidbow_p_system import BasePEvaluator         # noqa: E402
from aidbow_prompts import BasePromptPack          # noqa: E402
from aidbow_harness import BaseHarness, BaseOverviewLLM, OverviewStep  # noqa: E402


# ---------- 一个确定性的离线 LLM（无需 API Key，便于小白复现） ----------
class DemoLLM(object):
    id = "demo-llm"
    def generate(self, prompt, **kw):
        # 仅用于演示：返回符合 OverviewResult 结构的 JSON（真实用法接你自选的 LLM）
        return json.dumps({
            "clusters": [
                {"label": "内容资产化", "note": "把备题/素材沉淀为可复用资产",
                 "idea_ids": ["A:01", "A:02"]},
            ],
            "conflicts": [],
            "shortlist": [{"idea_id": "A:02", "why": "改动小、当月可上线"}],
            "open_questions": ["首批辩题从哪个平台采集？"],
            "warnings": [],
        }, ensure_ascii=False)


def main():
    print("=" * 60)
    print("Aidbow DBOW 端到端示例（零配置）")
    print("=" * 60)

    # 1) D · 需求（可挂上下文）
    demand = Demand(
        id="demo-001",
        prompt="给一款独立游戏做“零预算”宣发，要求可执行、可衡量。",
        context=ContextBundle(items=[
            ContextItem(kind="text", ref="产品：像素风 Roguelike，Steam 首发"),
        ]),
        constraints=["无投放预算", "2 周内启动"],
        targets={"P2": 4, "P7": 4},
    )
    print("\n[1/5] Demand 需求：", demand.prompt)

    # 2) B · 头脑风暴（这里用 2 条示例创意代表 LLM 产出）
    ideas = [
        Idea(id="A:01", author="anon", round="R1", title="辨题素材库 / 内容资产化",
             oneLiner="把可复用的宣发素材沉淀为资产",
             body="**正文**：" + "把每次宣发用到的图/文案/短视频都入库，形成可复用资产。" * 12,
             P={"P2": 4, "P4": 3}),
        Idea(id="A:02", author="anon", round="R1", title="零预算冷启动：社群先发",
             oneLiner="先用 Discord/贴吧社群做种子用户",
             body="**正文**：" + "在玩家社群先发 Demo 收集反馈，再反向做内容。" * 12,
             P={"P2": 5, "P4": 4}),
    ]
    print("[2/5] Brainstorm 创意数：", len(ideas))

    # 3) P 值自动评估（P3 篇幅可计算）
    evaluator = BasePEvaluator()
    for it in ideas:
        res = evaluator.evaluate(it, demand)
        it.P.update(res.P)
        it.basis.update(res.basis)
    print("[3/5] P 值评估完成（含可计算的 P3）：",
          {it.id: it.P.get("P3") for it in ideas})

    # 4) O · 汇总收敛（用离线 LLM 走 BaseOverviewLLM；也可换 AgentOverview）
    pack = BasePromptPack()
    summarizer = BaseOverviewLLM(DemoLLM(), prompts=pack)

    class _Brainstorm(object):
        name = "brainstorm"
        def run(self, inp, ctx):
            dem = inp if not isinstance(inp, dict) else inp.get("demand")
            return {"demand": dem, "ideas": ideas}

    harness = BaseHarness(
        evaluator=evaluator, summarizer=summarizer,
        stages=[("demand", __import__("aidbow_harness").DemandStep()),
                ("brainstorm", _Brainstorm()),
                ("overview", OverviewStep())],
    )
    out = harness.run(demand)
    overview = out["result"]["overview"]
    assert isinstance(overview, OverviewResult)
    print("[4/5] Overview 汇总：", overview.method,
          "| 簇:", [c.label for c in overview.clusters],
          "| 短名单:", [s["idea_id"] for s in overview.shortlist])

    # 5) W · 决策 → 工作流指令
    decision = Decision(demandId=demand.id, selected=["A:02"], priorities={"A:02": "P0"},
                        notes={"A:02": "先做社群冷启动"})
    wf_step = __import__("aidbow_harness").WorkflowStep()
    wf_out = wf_step.run({"demand": demand, "decision": decision}, None)
    spec = wf_out["workflow"]
    print("[5/5] Workflow 指令：", len(spec.steps), "步 · 源自", spec.sourceIdeas)

    print("\n" + "-" * 60)
    print("预期成果 (OverviewResult):")
    print(json.dumps(overview.to_dict(), ensure_ascii=False, indent=2))
    print("-" * 60)
    print("✅ DEMO OK")


if __name__ == "__main__":
    main()
