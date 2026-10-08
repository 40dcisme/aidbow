"""DBOW 数据模型 —— 严格对齐 opensource/SPEC.md §1 / §2。"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Literal, Optional

PKey = str  # "P1".."P7"（或扩展维度如 "P6-R1"）
ROUND = Literal["R1", "R2"]
LINEAGE_MODE = Literal["graft", "rebut", "combine", "deepen"]
PRIORITY = Literal["P0", "P1", "P2", "shelved"]


# ---------------- 序列化工具 ----------------
class _Ser:
    def to_dict(self) -> dict:
        return asdict(self)                      # type: ignore[arg-type]


# ---------------- §1 数据模型 ----------------
@dataclass
class ContextItem(_Ser):
    kind: Literal["text", "link", "file", "dataset"]
    ref: str
    meta: dict[str, str] = field(default_factory=dict)


@dataclass
class ContextBundle(_Ser):
    items: list[ContextItem] = field(default_factory=list)


@dataclass
class Demand(_Ser):
    id: str
    prompt: str
    context: Optional[ContextBundle] = None
    constraints: list[str] = field(default_factory=list)
    targets: dict[PKey, float] = field(default_factory=dict)


@dataclass
class Idea(_Ser):
    id: str
    author: str
    round: ROUND
    title: str
    oneLiner: str
    body: str
    P: dict[PKey, float] = field(default_factory=dict)
    basis: dict[PKey, str] = field(default_factory=dict)
    lineage: Optional[dict[str, str]] = None      # {"from": id, "mode": graft|rebut|combine|deepen}


@dataclass
class Decision(_Ser):
    demandId: str
    selected: list[str] = field(default_factory=list)
    priorities: dict[str, PRIORITY] = field(default_factory=dict)
    notes: dict[str, str] = field(default_factory=dict)


@dataclass
class WorkflowSpec(_Ser):
    demandId: str
    steps: list[dict[str, Any]] = field(default_factory=list)   # [{title,instruction,inputs?,outputs?}]
    sourceIdeas: list[str] = field(default_factory=list)


# ---------------- §2 结果类型 ----------------
@dataclass
class PResult(_Ser):
    P: dict[PKey, float] = field(default_factory=dict)
    basis: dict[PKey, str] = field(default_factory=dict)


@dataclass
class PAggregate(_Ser):
    mean: dict[PKey, float] = field(default_factory=dict)
    n: int = 0


@dataclass
class ResolvedContext(_Ser):
    text: str
    citations: list[str] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvalContext:
    """P 判定上下文（可选）。"""
    reference_ideas: list[Idea] = field(default_factory=list)   # 用于 P6-R2 同轮重合度
    rubric: dict[str, Any] = field(default_factory=dict)        # 项目级 rubric 覆盖


@dataclass
class HarnessContext:
    """注入点：evaluator / context / llm / logger（SPEC §2.2）。"""
    evaluator: Any = None
    context: Any = None
    llm: Any = None
    logger: Any = None
