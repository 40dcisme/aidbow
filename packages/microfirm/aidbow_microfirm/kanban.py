"""Microfirm OS · 任务队列即看板（Task Kanban）—— 机制 2。

把 999 inbox/TODO/PROGRESS 产品化为单人创业者的运营台：
- 派活（给哪个 Agent）→ 验收（标准先行）→ 留痕（状态机 open/doing/done）
- 每张任务卡 = 一条可结算工作证明（接 A-001#03 结算协议）
"""

from __future__ import annotations

import datetime
import json
import uuid
from typing import Any, Optional


class Task:
    """一张任务卡（对齐 999 inbox 任务卡的最小字段 + 状态机）。"""
    __slots__ = ("id", "title", "assignee", "status", "acceptance",
                 "created_at", "done_at", "result", "proof")

    def __init__(self, title: str, assignee: str, acceptance: str,
                 task_id: Optional[str] = None):
        self.id = task_id or f"t-{uuid.uuid4().hex[:10]}"
        self.title = title
        self.assignee = assignee
        self.acceptance = acceptance      # 验收标准（标准先行）
        self.status = "open"              # open → doing → done
        self.created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.done_at: Optional[str] = None
        self.result: Optional[str] = None
        self.proof: Optional[dict] = None # 工作证明（接结算层）

    # -- 状态机 ----------------------------------------------------------
    def start(self) -> "Task":
        if self.status != "open":
            raise ValueError(f"只能从 open 开始，当前 {self.status}")
        self.status = "doing"
        return self

    def complete(self, result: str, proof: Optional[dict] = None) -> "Task":
        if self.status != "doing":
            raise ValueError(f"只能从 doing 完成，当前 {self.status}")
        self.status = "done"
        self.done_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.result = result
        # 工作证明：任务卡 = 可结算证据（对齐 Agent 任务工作证明结算层）
        self.proof = {
            "task_id": self.id,
            "assignee": self.assignee,
            "accepted_at": self.done_at,
            "acceptance_criteria": self.acceptance,
            "result_hash": _hash(result),
            ** (proof or {}),
        }
        return self

    def to_dict(self) -> dict:
        return {"id": self.id, "title": self.title, "assignee": self.assignee,
                "status": self.status, "acceptance": self.acceptance,
                "created_at": self.created_at, "done_at": self.done_at,
                "result": self.result, "proof": self.proof}


class Kanban:
    """任务队列（单人创业者的运营台）。"""

    def __init__(self):
        self.tasks: list[Task] = []

    def assign(self, title: str, assignee: str, acceptance: str) -> Task:
        """派活：验收标准先行（标准不明不派活）。"""
        if not acceptance.strip():
            raise ValueError("验收标准必填（标准先行）")
        task = Task(title=title, assignee=assignee, acceptance=acceptance)
        self.tasks.append(task)
        return task

    def board(self) -> dict[str, list[Task]]:
        """看板视图：open / doing / done 三列。"""
        return {
            "open": [t for t in self.tasks if t.status == "open"],
            "doing": [t for t in self.tasks if t.status == "doing"],
            "done": [t for t in self.tasks if t.status == "done"],
        }

    def pending_proofs(self) -> list[dict]:
        """未结算的工作证明（接结算层：A-001#03 按证明入账）。"""
        return [t.proof for t in self.tasks if t.status == "done" and t.proof]

    def dump_json(self) -> str:
        return json.dumps(
            {k: [t.to_dict() for t in v] for k, v in self.board().items()},
            ensure_ascii=False, indent=2)


def _hash(s: str) -> str:
    import hashlib
    return hashlib.sha256(s.encode()).hexdigest()[:16]
