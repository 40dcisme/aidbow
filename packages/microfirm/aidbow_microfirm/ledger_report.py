"""Microfirm OS · 日报即数据（Daily Report as Data）—— 机制 3。

996 式日报 + iPlan 快照自动生成：
- 既是审计证据、也是结算依据、还是获客素材（真实单人公司的运营留痕）
"""

from __future__ import annotations

import datetime
from typing import Any

from .kanban import Kanban
from .roster import Roster


class DailyReport:
    """一天的公司运营留痕（对齐 996 日报 + iPlan 快照）。"""

    def __init__(self, roster: Roster, kanban: Kanban, date: str | None = None):
        self.roster = roster
        self.kanban = kanban
        self.date = date or datetime.date.today().isoformat()

    def generate(self) -> dict[str, Any]:
        """生成日报：值班摘要 + 任务流水 + 结算依据。"""
        board = self.kanban.board()
        done_today = [
            t for t in board["done"]
            if t.done_at and t.done_at.startswith(self.date)
        ]
        oncall = self.roster.oncall_now()
        return {
            "date": self.date,
            "oncall": oncall.to_dict() if oncall else None,
            "company": {
                "agents": [a.to_dict() for a in self.roster.agents],
                "escalation_chain": self.roster.escalation_chain,
            },
            "today": {
                "opened": len(board["open"]),
                "in_progress": len(board["doing"]),
                "completed": len(done_today),
                "tasks": [t.to_dict() for t in done_today],
            },
            "settlement": {
                "proofs": self.kanban.pending_proofs(),
                "total_pending": len(self.kanban.pending_proofs()),
            },
            # 获客素材：真实运营留痕 = 稀缺内容资产
            "content_asset": _build_content_asset(self),
        }


def _build_content_asset(report: DailyReport) -> dict[str, str]:
    """把日报转成可发布的内容素材（喂 ascii.im Blog SEO / Ximo 地推池）。"""
    board = report.kanban.board()
    oncall = report.roster.oncall_now()
    oncall_id = oncall.id if oncall else "none"
    done_today = len([t for t in board["done"] if t.done_at and t.done_at.startswith(report.date)])
    return {
        "hook": f"A one-person company run by {len(report.roster.agents)} agents — day {report.date}",
        "body": f"On call: {oncall_id} · opened {len(board['open'])} · done {done_today}",
        "cta": "Built with Microfirm OS — the company shell for 1 human + N agents.",
    }
