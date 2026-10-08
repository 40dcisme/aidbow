"""四个默认步骤（StepContract 实现）。闭源可注入精炼实现替换同名步骤。

步骤是「壳」：真调用由注入的 llm / evaluator / context 完成；无注入时用安全缺省（不编造）。
"""
from __future__ import annotations

try:
    from aidbow_core import Demand, Idea, Decision, WorkflowSpec, HarnessContext
except Exception:
    pass


class DemandStep:
    """D：需求拆解。"""
    name = "demand"
    def run(self, input, ctx):
        demand = input                                  # 入参=Demand
        ctx.logger and ctx.logger("demand.start", {"id": getattr(demand, "id", "?")})
        # 有 llm+prompts 时调用 decompose；缺省直接透传（不臆造）
        return {"demand": demand, "brief": getattr(demand, "prompt", "")}


class BrainstormStep:
    """B：头脑风暴（发散）。"""
    name = "brainstorm"
    def run(self, input, ctx):
        ideas = []                                      # 真实产出应由 llm 生成；缺省空集
        ctx.logger and ctx.logger("brainstorm.start", {})
        return {"demand": input.get("demand"), "ideas": ideas}


class OverviewStep:
    """O：汇总收敛（此处只做结构化的 P 汇总，不编造结论）。"""
    name = "overview"
    def run(self, input, ctx):
        ideas = input.get("ideas", [])
        agg = None
        if ctx.evaluator and ideas:
            agg = ctx.evaluator.aggregate(ideas)
        # 注入 summarizer → 自动产出 OverviewResult（LLM 或 Agent 路径）
        overview = None
        sm = getattr(ctx, "summarizer", None)
        if sm is not None and ideas:
            try:
                overview = sm.summarize(ideas, input.get("demand"))
            except Exception as e:            # 不编造：失败则显式记录
                overview = {"error": str(e), "method": getattr(sm, "id", "summarizer")}
        return {"demand": input.get("demand"), "ideas": ideas, "aggregate": agg,
                "overview": overview}


class WorkflowStep:
    """W：由 Decision 生成 WorkflowSpec。"""
    name = "workflow"
    def run(self, input, ctx):
        demand = input.get("demand")
        decision = input.get("decision")
        steps = []
        if decision:
            for sid in getattr(decision, "selected", []):
                steps.append({"title": f"Idea {sid} 落地", "instruction": "由使用者填充关键指令",
                              "inputs": [], "outputs": []})
        wf = WorkflowSpec(demandId=getattr(demand, "id", ""), steps=steps,
                          sourceIdeas=list(getattr(decision, "selected", []) if decision else []))
        return {"demand": demand, "workflow": wf}
