"""扩展点协议 —— 严格对齐 opensource/SPEC.md §2（四接口 + Harness）。"""
from __future__ import annotations
from typing import Protocol, runtime_checkable, Any
from .models import (
    Demand, Idea, PResult, PAggregate, EvalContext, ContextItem,
    ResolvedContext, HarnessContext,
)


@runtime_checkable
class PEvaluator(Protocol):
    """§2.1 P 值引擎。"""
    dimensions: list[str]
    def evaluate(self, idea: Idea, demand: Demand, ctx: EvalContext | None = None) -> PResult: ...
    def aggregate(self, ideas: list[Idea], ctx: EvalContext | None = None) -> PAggregate: ...


@runtime_checkable
class ContextProvider(Protocol):
    """§2.3 上下文解析。"""
    id: str
    def canHandle(self, item: ContextItem) -> bool: ...
    def resolve(self, item: ContextItem, ctx: Any = None) -> ResolvedContext: ...


@runtime_checkable
class PromptPack(Protocol):
    """§2.4 提示词包。"""
    id: str
    templates: dict[str, str]
    def get(self, name: str, vars: dict[str, str] | None = None) -> str: ...


@runtime_checkable
class StepContract(Protocol):
    """§2.2 可替换步骤。"""
    name: str
    def run(self, input: Any, ctx: HarnessContext) -> Any: ...


@runtime_checkable
class Harness(Protocol):
    """§2.2 编排。"""
    stages: list[Any]
    def run(self, demand: Demand, ctx: HarnessContext) -> Any: ...
