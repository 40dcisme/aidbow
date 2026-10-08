"""aidbow_core — DBOW 数据模型与扩展点协议（零依赖）。"""
from .models import (
    PKey, Demand, ContextBundle, ContextItem, Idea, Decision, WorkflowSpec,
    PResult, PAggregate, ResolvedContext, EvalContext, HarnessContext,
    OverviewResult, OverviewCluster, OverviewConflict,
)
from .interfaces import (PEvaluator, ContextProvider, PromptPack, StepContract, Harness,
                         LLMAdapter, AgentAdapter)

__all__ = [
    "PKey","Demand","ContextBundle","ContextItem","Idea","Decision","WorkflowSpec",
    "PResult","PAggregate","ResolvedContext","EvalContext","HarnessContext",
    "PEvaluator","ContextProvider","PromptPack","StepContract","Harness",
    "LLMAdapter","AgentAdapter",
    "OverviewResult","OverviewCluster","OverviewConflict",
]
__version__ = "0.1.0"
