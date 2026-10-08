"""aidbow_core — DBOW 数据模型与扩展点协议（零依赖）。"""
from .models import (
    PKey, Demand, ContextBundle, ContextItem, Idea, Decision, WorkflowSpec,
    PResult, PAggregate, ResolvedContext, EvalContext, HarnessContext,
)
from .interfaces import PEvaluator, ContextProvider, PromptPack, StepContract, Harness

__all__ = [
    "PKey","Demand","ContextBundle","ContextItem","Idea","Decision","WorkflowSpec",
    "PResult","PAggregate","ResolvedContext","EvalContext","HarnessContext",
    "PEvaluator","ContextProvider","PromptPack","StepContract","Harness",
]
__version__ = "0.1.0"
