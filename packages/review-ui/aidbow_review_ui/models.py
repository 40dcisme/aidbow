"""review-ui 数据加载与校验 —— 严格对齐 SPEC.md §1。

零三方依赖。只做两件事：
  1. 从 JSON 文件 / 字典列表加载 Idea[]，校验必填字段并给出可读错误；
  2. 在浏览器数据之外提供 Decision 的构造与校验（CLI / 测试 / 二次集成用）。

SPEC 未定义的字段一律保留但不校验（前向兼容）；必填字段缺失或类型错误
时抛 ReviewUIError，不静默丢数据（AGENTS.md §3 禁止编造）。
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Union

P_KEYS = ("P1", "P2", "P3", "P4", "P5", "P6", "P7")
ROUNDS = ("R1", "R2")
PRIORITIES = ("P0", "P1", "P2", "shelved")

_IDEA_REQUIRED = ("id", "author", "round", "title", "oneLiner", "body")
_DECISION_REQUIRED = ("demandId", "selected")


class ReviewUIError(ValueError):
    """输入数据不满足 SPEC §1 契约。"""


def _require(obj: Dict[str, Any], keys, where: str) -> None:
    missing = [k for k in keys if k not in obj]
    if missing:
        raise ReviewUIError(f"{where} 缺少必填字段: {', '.join(missing)}")


def _check_type(obj: Dict[str, Any], key: str, types: tuple, where: str) -> None:
    if not isinstance(obj[key], types):
        raise ReviewUIError(
            f"{where} 字段 {key} 类型错误: 应为 {types}, 实际 {type(obj[key]).__name__}"
        )


def normalize_idea(raw: Dict[str, Any], *, index: int = -1) -> Dict[str, Any]:
    """校验并规范化单条 Idea；返回可直接序列化进 HTML 的新字典。"""
    where = f"Idea[{index}]" if index >= 0 else "Idea"
    if not isinstance(raw, dict):
        raise ReviewUIError(f"{where} 必须是对象 (dict), 实际 {type(raw).__name__}")
    _require(raw, _IDEA_REQUIRED, where)

    for key in ("id", "author", "round", "title", "oneLiner", "body"):
        _check_type(raw, key, (str,), where)
    if raw["round"] not in ROUNDS:
        raise ReviewUIError(f"{where} round 必须是 {ROUNDS}, 实际 {raw['round']!r}")
    if not raw["id"].strip():
        raise ReviewUIError(f"{where} id 不能为空字符串")

    out: Dict[str, Any] = {k: raw[k] for k in _IDEA_REQUIRED}

    # P 值卡：SPEC 允许缺维度；分值必须是 0–5 的数（int 或 float）。
    p_in = raw.get("P", {})
    if not isinstance(p_in, dict):
        raise ReviewUIError(f"{where} P 必须是对象 (dict)")
    p_out: Dict[str, float] = {}
    for k, v in p_in.items():
        if k not in P_KEYS:
            raise ReviewUIError(f"{where} P 含未知维度 {k!r}（合法: {P_KEYS}）")
        if not isinstance(v, (int, float)) or isinstance(v, bool) or not 0 <= v <= 5:
            raise ReviewUIError(f"{where} P.{k} 必须是 0–5 的数字, 实际 {v!r}")
        p_out[k] = v
    out["P"] = p_out

    basis_in = raw.get("basis", {})
    if not isinstance(basis_in, dict):
        raise ReviewUIError(f"{where} basis 必须是对象 (dict)")
    basis_out: Dict[str, str] = {}
    for k, v in basis_in.items():
        if k not in P_KEYS:
            raise ReviewUIError(f"{where} basis 含未知维度 {k!r}")
        if not isinstance(v, str):
            raise ReviewUIError(f"{where} basis.{k} 必须是字符串")
        basis_out[k] = v
    out["basis"] = basis_out

    lineage = raw.get("lineage")
    if lineage is not None:
        if not isinstance(lineage, dict) or "from" not in lineage or "mode" not in lineage:
            raise ReviewUIError(
                f"{where} lineage 必须是 {{'from': id, 'mode': graft|rebut|combine|deepen}}"
            )
        if lineage["mode"] not in ("graft", "rebut", "combine", "deepen"):
            raise ReviewUIError(f"{where} lineage.mode 非法: {lineage['mode']!r}")
        out["lineage"] = {"from": str(lineage["from"]), "mode": lineage["mode"]}

    return out


def load_ideas(source: Union[str, Path, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """从 JSON 文件或字典列表加载 Idea[]。

    JSON 支持两种顶层形态：
      - 直接是 Idea 数组 ``[{...}, ...]``；
      - 对象 ``{"demandId": ..., "ideas": [...]}``（便于连同 demand 一起归档）。
    """
    if isinstance(source, list):
        data: Any = source
    else:
        path = Path(source)
        if not path.exists():
            raise ReviewUIError(f"输入文件不存在: {path}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ReviewUIError(f"JSON 解析失败 {path}: {exc}") from exc

    if isinstance(data, dict) and isinstance(data.get("ideas"), list):
        data = data["ideas"]
    if not isinstance(data, list):
        raise ReviewUIError("输入 JSON 顶层必须是 Idea[] 或 {'ideas': Idea[]}")

    ideas = [normalize_idea(raw, index=i) for i, raw in enumerate(data)]
    ids = [it["id"] for it in ideas]
    dup = {x for x in ids if ids.count(x) > 1}
    if dup:
        raise ReviewUIError(f"Idea id 必须唯一, 重复: {sorted(dup)}")
    return ideas


def validate_decision(
    decision: Dict[str, Any], known_ids: List[str]
) -> Dict[str, Any]:
    """校验浏览器/调用方给出的 Decision（SPEC §1）。"""
    if not isinstance(decision, dict):
        raise ReviewUIError("Decision 必须是对象 (dict)")
    _require(decision, _DECISION_REQUIRED, "Decision")
    if not isinstance(decision["demandId"], str):
        raise ReviewUIError("Decision.demandId 必须是字符串")

    selected = decision["selected"]
    if not isinstance(selected, list) or not all(isinstance(x, str) for x in selected):
        raise ReviewUIError("Decision.selected 必须是 string[]")

    known = set(known_ids)
    unknown = [x for x in selected if x not in known]
    if unknown:
        raise ReviewUIError(f"Decision.selected 引用了不存在的 Idea id: {unknown}")

    priorities = decision.get("priorities", {})
    if not isinstance(priorities, dict):
        raise ReviewUIError("Decision.priorities 必须是对象")
    for k, v in priorities.items():
        if k not in known:
            raise ReviewUIError(f"priorities 的 key {k!r} 不是已知 Idea id")
        if v not in PRIORITIES:
            raise ReviewUIError(f"priorities[{k!r}] 必须是 {PRIORITIES}, 实际 {v!r}")

    notes = decision.get("notes", {})
    if not isinstance(notes, dict) or not all(
        isinstance(k, str) and isinstance(v, str) for k, v in notes.items()
    ):
        raise ReviewUIError("Decision.notes 必须是 string→string 对象")
    for k in notes:
        if k not in known:
            raise ReviewUIError(f"notes 的 key {k!r} 不是已知 Idea id")

    return decision
