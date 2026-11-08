#!/usr/bin/env python3
"""Microfirm OS 演示：1 个自然人 + 3 个 Agent 跑一周的「一人公司」。

演示三件机制：值班编排 → 任务队列（派活/验收/留痕）→ 日报即数据。
运行: python3 examples/microfirm_demo.py   → 结尾 ✅ DEMO OK
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "packages" / "microfirm"))

from aidbow_microfirm import Agent, Roster, Kanban, DailyReport


def main() -> None:
    # ---- 1. 值班编排：3 个 Agent（内容/客服/运维）+ 升级链到自然人 ----
    roster = Roster(
        agents=[
            Agent("writer", "content", sync_hours=6),
            Agent("support", "customer", sync_hours=12),
            Agent("ops", "devops", sync_hours=6),
        ],
        escalation_chain=["ops", "support", "human"],
    )

    # ---- 2. 任务队列：派活（验收标准先行）----
    kb = Kanban()

    # 内容线：写一篇 blog
    t1 = kb.assign("写 ascii 艺术起源 blog", "writer", "≥800 词 + 0 AI 痕迹词")
    t1.start()
    t1.complete("完成，1080 词，密度 1.3%", {"words": 1080, "ai_artifacts": 0})

    # 客服线：处理一条用户反馈
    t2 = kb.assign("处理 ascii.im 用户反馈", "support", "24h 内回复 + 记录工单")
    t2.start()
    t2.complete("已回复，转产品 backlog", {"ticket": "T-1024"})

    # 运维线：一次故障（低优先级 Agent 自治失败 → 升级）
    t3 = kb.assign("修复 blog CRON 截断", "ops", "恢复自动运行 + 留痕")
    t3.start()
    t3.complete("已补跑节点 #26，CRON 恢复", {"resume_at": "16:59"})

    # 升级示例：Agent 卡住 → 沿链升到自然人
    escalation = roster.escalate("t-4", "ops agent stuck on deploy")

    # ---- 3. 日报即数据 ----
    report = DailyReport(roster, kb).generate()

    # ---- 输出 ----
    print("=== Microfirm OS · 一人公司（1 人 + 3 Agent）===")
    print(f"\n[值班] 当前值班: {roster.oncall_now().id}")
    print(f"[看板] open={len(kb.board()['open'])} doing={len(kb.board()['doing'])} done={len(kb.board()['done'])}")
    print(f"[结算] 待结算工作证明: {len(kb.pending_proofs())} 条")
    print(f"[升级] 示例: {escalation['task_id']} → {escalation['final_owner']}")
    print(f"\n[日报·获客素材] {report['content_asset']['hook']}")
    print(f"  {report['content_asset']['body']}")
    print(f"  {report['content_asset']['cta']}")
    print("\n✅ DEMO OK")


if __name__ == "__main__":
    main()
