"""BasePEvaluator — 开源基础版 P 引擎。"""
from __future__ import annotations
import re
from typing import Optional

try:
    from aidbow_core import Idea, Demand, PResult, PAggregate, EvalContext
except Exception:  # 允许在未安装 core 时本地运行
    from dataclasses import dataclass, field
    @dataclass
    class PResult:  # type: ignore
        P: dict = field(default_factory=dict); basis: dict = field(default_factory=dict)
    @dataclass
    class PAggregate:  # type: ignore
        mean: dict = field(default_factory=dict); n: int = 0
    EvalContext = object  # type: ignore

from .rubric import RUBRIC, P_KEYS


def count_body_chars(body: str) -> int:
    """P3 篇幅口径：`**正文**:` 锚之后、剔除 ``` 代码块``` 的正文字符数（与既有计数口径一致）。"""
    if not body:
        return 0
    seg = body
    m = re.search(r"\*\*正文\*\*[：:]\s*(.*)", body, re.S)
    seg = m.group(1) if m else body
    seg = re.sub(r"```.*?```", "", seg, flags=re.S)      # 剔除代码块
    seg = re.sub(r"`[^`]*`", "", seg)                     # 剔除行内代码
    return len(re.sub(r"\s+", "", seg))


def p3_score(nchars: int) -> int:
    if nchars < 400: return 1
    if nchars < 800: return 3
    if nchars < 1200: return 4
    return 5


class BasePEvaluator:
    """基础实现。`rubric` 参数=项目级覆盖（闭源精炼层注入用，开源不 fork）。"""
    dimensions = list(P_KEYS)

    def __init__(self, rubric: Optional[dict] = None):
        self.rubric = {**RUBRIC, **(rubric or {})}

    def evaluate(self, idea, demand=None, ctx=None) -> PResult:
        P, basis = {}, {}
        # 可计算维度
        n = count_body_chars(getattr(idea, "body", "") or "")
        P["P3"] = p3_score(n); basis["P3"] = f"正文={n}字（口径：**正文**锚+剔代码块）"
        # 自评维度：优先取 idea 自带（参与者填），缺省不臆造
        for k in ["P1", "P2", "P4", "P5", "P7"]:
            if getattr(idea, "P", {}).get(k) is not None:
                P[k] = idea.P[k]; basis[k] = getattr(idea, "basis", {}).get(k, "参与者自评")
        # P6 拆分：按轮次择一
        rnd = getattr(idea, "round", "R1")
        key = "P6-R1" if rnd == "R1" else "P6-R2"
        if getattr(idea, "P", {}).get(key) is not None:
            P[key] = idea.P[key]; basis[key] = getattr(idea, "basis", {}).get(key, "主持判定/参与者自评")
        elif getattr(idea, "P", {}).get("P6") is not None:      # 兼容旧卡 P6
            P[key] = idea.P["P6"]
            basis[key] = getattr(idea, "basis", {}).get("P6", "经旧 P6 归并")
        return PResult(P=P, basis=basis)

    def aggregate(self, ideas, ctx=None) -> PAggregate:
        acc: dict[str, list[float]] = {}
        for it in ideas:
            res = self.evaluate(it)
            for k, v in res.P.items():
                acc.setdefault(k, []).append(v)
        return PAggregate(mean={k: round(sum(v)/len(v), 3) for k, v in acc.items() if v},
                          n=len(ideas))
