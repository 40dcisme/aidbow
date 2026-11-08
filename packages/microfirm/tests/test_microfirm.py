"""Microfirm OS 包测试：值班编排 / 任务队列 / 日报（纯 stdlib）。"""

import datetime
import sys
import unittest

sys.path.insert(0, ".")

from aidbow_microfirm import Agent, Roster, Task, Kanban, DailyReport  # noqa: E402


class TestRoster(unittest.TestCase):
    """机制 1：值班编排"""

    def test_oncall_rotation(self):
        roster = Roster(
            agents=[
                Agent("a1", "content", sync_hours=6),
                Agent("a2", "support", sync_hours=6),
                Agent("a3", "ops", sync_hours=6),
            ],
            escalation_chain=["a3", "a2", "human"],
        )
        # 确定性：同一时刻同一值班者
        at = datetime.datetime(2026, 11, 8, 12, 0, tzinfo=datetime.timezone.utc)
        a = roster.oncall_now(at)
        b = roster.oncall_now(at)
        self.assertIsNotNone(a)
        self.assertIsNotNone(b)
        self.assertEqual(a.id, b.id)
        self.assertIn(a.id, {"a1", "a2", "a3"})

    def test_escalation(self):
        roster = Roster([Agent("a1", "content")], ["a1", "human"])
        e = roster.escalate("t-1", "agent stuck")
        self.assertEqual(e["final_owner"], "human")
        self.assertEqual(len(e["chain"]), 2)

    def test_yaml_load(self):
        yaml_text = """
agents:
  - id: "writer"
    role: "content"
    sync_hours: 6
  - id: "support"
    role: "customer"
    sync_hours: 12
escalation_chain:
  - support
  - human
"""
        roster = Roster.from_yaml(yaml_text)
        self.assertEqual(len(roster.agents), 2)
        self.assertEqual(roster.escalation_chain, ["support", "human"])


class TestKanban(unittest.TestCase):
    """机制 2：任务队列即看板"""

    def test_lifecycle(self):
        kb = Kanban()
        t = kb.assign("写一篇 blog", "writer", "≥800 词且 0 AI 痕迹词")
        self.assertEqual(t.status, "open")
        t.start()
        self.assertEqual(t.status, "doing")
        t.complete("完成，1080 词", {"words": 1080})
        self.assertEqual(t.status, "done")
        # 工作证明生成
        self.assertTrue(t.proof)
        self.assertIn("result_hash", t.proof)

    def test_acceptance_required(self):
        kb = Kanban()
        with self.assertRaises(ValueError):
            kb.assign("无验收标准的任务", "writer", "")

    def test_board_columns(self):
        kb = Kanban()
        t1 = kb.assign("A", "a1", "c1").start().complete("ok")
        t2 = kb.assign("B", "a2", "c2").start()
        t3 = kb.assign("C", "a3", "c3")
        board = kb.board()
        self.assertEqual(len(board["done"]), 1)
        self.assertEqual(len(board["doing"]), 1)
        self.assertEqual(len(board["open"]), 1)

    def test_pending_proofs(self):
        kb = Kanban()
        kb.assign("A", "a1", "c1").start().complete("ok")
        proofs = kb.pending_proofs()
        self.assertEqual(len(proofs), 1)
        self.assertTrue(proofs[0])
        self.assertIn("task_id", proofs[0])


class TestDailyReport(unittest.TestCase):
    """机制 3：日报即数据"""

    def test_generate(self):
        roster = Roster([Agent("writer", "content")], ["human"])
        kb = Kanban()
        kb.assign("写一篇 blog", "writer", "≥800 词").start().complete("ok")
        report = DailyReport(roster, kb, date="2026-11-08").generate()
        self.assertEqual(report["date"], "2026-11-08")
        self.assertIn("settlement", report)
        self.assertIn("content_asset", report)
        # 获客素材可发布
        self.assertIn("hook", report["content_asset"])
        self.assertIn("cta", report["content_asset"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
