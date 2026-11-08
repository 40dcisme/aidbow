"""Microfirm OS · 值班编排（On-call Roster）—— 机制 1。

把「1 个自然人 + N 个 Agent」的 24×7 轮值与升级链跑起来：
- roster.yaml 定义成员、轮值周期、升级链（低优先级 Agent 自治，异常升级到自然人）
- 对齐 AgentSync 798 registry 的 sync_hours 节拍思想（心跳自我运转）
"""

from __future__ import annotations

import datetime
import json
from typing import Any, Optional

# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------

class Agent:
    """一名 Agent 成员（对齐 798 registry 的最小字段）。"""
    __slots__ = ("id", "role", "level", "sync_hours", "oncall")

    def __init__(self, id: str, role: str, level: str = "L1",
                 sync_hours: int = 6, oncall: bool = True):
        self.id = id
        self.role = role
        self.level = level
        self.sync_hours = sync_hours
        self.oncall = oncall

    def to_dict(self) -> dict:
        return {"id": self.id, "role": self.role, "level": self.level,
                "sync_hours": self.sync_hours, "oncall": self.oncall}

    @classmethod
    def from_dict(cls, d: dict) -> "Agent":
        return cls(d["id"], d.get("role", ""), d.get("level", "L1"),
                   d.get("sync_hours", 6), d.get("oncall", True))


class Roster:
    """值班表：按 sync_hours 节拍轮值，含升级链。"""

    def __init__(self, agents: list[Agent], escalation_chain: list[str]):
        """
        agents:            全部 Agent（oncall=True 的参与轮值）
        escalation_chain:  升级链（升到谁：["agent_c", "agent_b", "human"] 从低到高）
        """
        self.agents = agents
        self.escalation_chain = escalation_chain

    # -- 构造 ------------------------------------------------------------
    @classmethod
    def from_yaml(cls, yaml_text: str) -> "Roster":
        """极简 YAML 解析（无外部依赖）：roster.yaml → Roster。"""
        import re
        agents: list[Agent] = []
        chain: list[str] = []
        current: dict[str, Any] = {}
        section = ""
        for line in yaml_text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line == "agents:":
                section = "agents"
                continue
            if line == "escalation_chain:":
                section = "chain"
                continue
            if section == "agents":
                if line.startswith("- id:"):
                    if current:
                        agents.append(Agent.from_dict(current))
                    current = {"id": line.split(":", 1)[1].strip().strip('"\'')}
                elif ":" in line:
                    k, v = line.split(":", 1)
                    current[k.strip()] = v.strip().strip('"\'').lower() == "true" \
                        if v.strip() in ("true", "false") else v.strip().strip('"\'')
            elif section == "chain":
                m = re.match(r"- ([\w]+)", line)
                if m:
                    chain.append(m.group(1))
        if current:
            agents.append(Agent.from_dict(current))
        return cls(agents, chain)

    # -- 值班逻辑 --------------------------------------------------------
    def oncall_now(self, at: Optional[datetime.datetime] = None) -> Optional[Agent]:
        """当前值班者：按 sync_hours 节拍轮值（确定性：epoch // 节拍 % 人数）。"""
        at = at or datetime.datetime.now(datetime.timezone.utc)
        eligible = [a for a in self.agents if a.oncall]
        if not eligible:
            return None
        tick = int(at.timestamp()) // 3600  # 小时级节拍
        total_hours = sum(max(1, a.sync_hours) for a in eligible)
        acc = 0
        for a in eligible:
            acc += max(1, a.sync_hours)
            if tick % total_hours < acc:
                return a
        return eligible[0]

    def escalate(self, task_id: str, reason: str,
                 at: Optional[datetime.datetime] = None) -> dict:
        """升级：低优先级 Agent 自治失败 → 沿升级链上升，直到自然人。
        返回升级留痕（对齐 999 inbox 的留痕语义）。"""
        at = at or datetime.datetime.now(datetime.timezone.utc)
        return {
            "task_id": task_id,
            "reason": reason,
            "escalated_at": at.isoformat(),
            "chain": self.escalation_chain,
            "final_owner": self.escalation_chain[-1] if self.escalation_chain else "human",
            "log": [{"to": h, "at": at.isoformat()} for h in self.escalation_chain],
        }

    def to_dict(self) -> dict:
        return {"agents": [a.to_dict() for a in self.agents],
                "escalation_chain": self.escalation_chain}

    def dump_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
