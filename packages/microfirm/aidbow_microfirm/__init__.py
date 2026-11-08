"""aidbow_microfirm — Microfirm OS：1 个自然人 + N 个 Agent 的最小公司壳。

机制：
- roster.py        值班编排（轮值 + 升级链）
- kanban.py        任务队列即看板（派活/验收/留痕/工作证明）
- ledger_report.py 日报即数据（审计/结算/获客素材）

来源：777-014 A-001-r2 R2-03「一人公司 OS」（P6=4 · S=0.83）
依赖：仅 stdlib（零外部依赖，可独立使用）
"""

from .roster import Agent, Roster
from .kanban import Task, Kanban
from .ledger_report import DailyReport

__all__ = ["Agent", "Roster", "Task", "Kanban", "DailyReport"]
__version__ = "0.1.0"
