"""BaseHarness — 按阶段推进，步骤可替换（SPEC §2.2）。"""
from __future__ import annotations
try:
    from aidbow_core import HarnessStage  # 若 core 提供
except Exception:
    HarnessStage = None


class _Stage:
    def __init__(self, key, step):
        self.key = key; self.step = step


class BaseHarness:
    """默认阶段：demand→brainstorm→overview→workflow。
    传入 `stages=[(key, step), ...]` 或 `overrides={key: step}` 可替换任意步骤（闭源精炼层用）。
    """
    def __init__(self, evaluator=None, context=None, llm=None, logger=None,
                 summarizer=None, overrides: dict | None = None, stages: list | None = None):
        from .steps import DemandStep, BrainstormStep, OverviewStep, WorkflowStep
        defaults = {"demand": DemandStep(), "brainstorm": BrainstormStep(),
                    "overview": OverviewStep(), "workflow": WorkflowStep()}
        defaults.update(overrides or {})
        self.stages = [(_k, _v) for _k, _v in (stages or defaults.items())]
        self.ctx_kwargs = dict(evaluator=evaluator, context=context, llm=llm, logger=logger,
                               summarizer=summarizer)

    def run(self, demand, ctx=None):
        from aidbow_core import HarnessContext
        hctx = ctx or HarnessContext(**self.ctx_kwargs)
        cur = demand
        trace = []
        for key, step in self.stages:
            out = step.run(cur, hctx)
            trace.append(key)
            cur = out if isinstance(out, dict) else {"_": out}
        return {"demand": demand, "result": cur, "trace": trace}
