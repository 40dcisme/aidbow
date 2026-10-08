"""Decision 导出 —— 状态字典 → SPEC §1 Decision JSON / 人类可读 Markdown。

状态口径与页面 JS 完全一致：
    state[idea_id] = {"picked": bool, "priority": "P0|P1|P2|shelved|''", "note": str}

浏览器端由内联 JS 复刻本文件的 Markdown 排版；本 Python 实现供 CLI、
测试和服务端集成使用（例如离线批量评审、CI 中校验决策单）。
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .models import validate_decision

# 与前端 JS 的 localStorage 结构一一对应（见 static/app.js）。
EMPTY_STATE = {"picked": False, "priority": "", "note": ""}

_PRIORITY_LABEL = {
    "P0": "P0 · 立即做",
    "P1": "P1 · 本轮做",
    "P2": "P2 · 排期做",
    "shelved": "搁置",
}


def get_state(store: Dict[str, Dict[str, Any]], idea_id: str) -> Dict[str, Any]:
    st = store.get(idea_id)
    if not st:
        return dict(EMPTY_STATE)
    # 容忍缺字段的旧状态。
    return {
        "picked": bool(st.get("picked", False)),
        "priority": st.get("priority", "") or "",
        "note": st.get("note", "") or "",
    }


def build_decision(
    ideas: List[Dict[str, Any]],
    store: Dict[str, Dict[str, Any]],
    demand_id: str,
) -> Dict[str, Any]:
    """按当前勾选状态构造 SPEC §1 Decision 对象。"""
    selected, priorities, notes = [], {}, {}
    for it in ideas:
        st = get_state(store, it["id"])
        if st["picked"]:
            selected.append(it["id"])
        if st["priority"]:
            priorities[it["id"]] = st["priority"]
        if st["note"].strip():
            notes[it["id"]] = st["note"].strip()
    decision: Dict[str, Any] = {"demandId": demand_id, "selected": selected}
    if priorities:
        decision["priorities"] = priorities
    if notes:
        decision["notes"] = notes
    return validate_decision(decision, [it["id"] for it in ideas])


def decision_to_json(decision: Dict[str, Any], *, indent: int = 2) -> str:
    return json.dumps(decision, ensure_ascii=False, indent=indent)


def _p_string(idea: Dict[str, Any]) -> str:
    parts = [f"{k}={idea['P'][k]:g}" for k in sorted(idea["P"])]
    return " ".join(parts) if parts else "（未评分）"


def _section(lines: List[str], tag: str, items: List[Dict[str, Any]],
             store: Dict[str, Dict[str, Any]], title_key: str) -> None:
    if not items:
        return
    lines.append(f"## {tag}（{len(items)}）")
    for it in items:
        st = get_state(store, it["id"])
        head = f"[{_PRIORITY_LABEL.get(st['priority'], st['priority'])}] " if st["priority"] else ""
        lines.append(f"### {head}{it[title_key]}")
        lines.append(
            f"- **编号**：{it['id']} ｜ **作者**：{it['author']} ｜ **轮次**：{it['round']}"
        )
        lines.append(f"- **P 值**：{_p_string(it)}")
        lines.append(f"- **一句话核心**：{it['oneLiner']}")
        if it.get("lineage"):
            lg = it["lineage"]
            lines.append(f"- **递进来源**：{lg['mode']} ← {lg['from']}")
        if st["note"].strip():
            lines.append(f"- **决策备注**：{st['note'].strip()}")
        lines.append("")
    lines.append("---")


def decision_to_markdown(
    ideas: List[Dict[str, Any]],
    store: Dict[str, Dict[str, Any]],
    demand_id: str,
    *,
    decision_time: Optional[str] = None,
) -> str:
    """生成与页面 JS 相同口径的评审决策单 Markdown。"""
    decision = build_decision(ideas, store, demand_id)
    when = decision_time or datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")

    picked = [it for it in ideas if get_state(store, it["id"])["picked"]]
    drafted = [
        it for it in ideas
        if not get_state(store, it["id"])["picked"]
        and get_state(store, it["id"])["priority"]
        and get_state(store, it["id"])["priority"] != "shelved"
    ]
    shelved = [it for it in ideas if get_state(store, it["id"])["priority"] == "shelved"]

    lines = [
        f"# 评审决策单 · {demand_id}",
        f"> Demand `{demand_id}` ｜ 决策时间 {when} ｜ 共 {len(ideas)} 条 · 选中 {len(picked)} 条",
        "> 口径：✅ 选中 = 纳入执行候选；🕓 备选 = 已定优先级未勾选；⏸ 搁置 = 暂缓。",
        "---",
    ]
    _section(lines, "✅ 选中（纳入执行候选）", picked, store, "title")
    _section(lines, "🕓 备选（已定优先级未勾选）", drafted, store, "title")
    _section(lines, "⏸ 搁置", shelved, store, "title")
    if not picked and not drafted and not shelved:
        lines.append("> ⚠️ 尚未做出任何决策（未勾选 / 未标优先级）。")
    lines.append(f"_由 aidbow review-ui 决策台生成 · {when}_")

    # 与 Decision JSON 交叉自检：导出内容不得与结构化决策矛盾。
    assert set(decision["selected"]) == {it["id"] for it in picked}
    return "\n".join(lines)
