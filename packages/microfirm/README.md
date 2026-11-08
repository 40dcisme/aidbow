# @aidbow/microfirm — Microfirm OS（一人公司操作系统）

> **1 个自然人 + N 个 Agent 的最小公司壳。**
> 来源：777-014 头脑风暴 A-001-r2「一人公司 OS」（P6=4 · S=0.83）· 规划见 [`docs/MICROFIRM-OS.md`](../../docs/MICROFIRM-OS.md)

## 定位

2029 年 AI 把单人的生产能力推到企业级后，组织最小单位从「人 + 工具」变成 **「1 个自然人 + N 个 Agent」**。
开这家公司需要的不是更好的模型，而是把 **派活、值班、留痕、算账** 跑起来的操作系统。

Microfirm OS 把 AgentSync 四件套纪律（798 registry / 800 assignments / 999 三件套 / 996 日报）产品化为三件机制：

| 机制 | 模块 | 对应 AgentSync |
|---|---|---|
| 值班编排（On-call Roster）| `roster.py` | 798 registry（轮值 + 升级链）|
| 任务队列即看板（Task Kanban）| `kanban.py` | 999 inbox/TODO/PROGRESS（派活/验收/留痕/工作证明）|
| 日报即数据（Daily Ledger）| `ledger_report.py` | 996 日报 + iPlan（审计/结算/获客素材）|

## 快速使用

```python
from aidbow_microfirm import Agent, Roster, Kanban, DailyReport

# 1. 值班编排：5 个 Agent 轮值 + 升级链
roster = Roster(
    agents=[
        Agent("writer", "content", sync_hours=6),
        Agent("support", "customer", sync_hours=12),
        Agent("ops", "devops", sync_hours=6),
    ],
    escalation_chain=["ops", "human"],   # 异常升级：Agent → 自然人
)
oncall = roster.oncall_now()             # 当前值班者（确定性轮值）
print("on call:", oncall.id)

# 2. 任务队列：派活（验收标准先行）→ 完成（生成工作证明）
kb = Kanban()
task = kb.assign("写一篇 blog", "writer", "≥800 词且 0 AI 痕迹词")
task.start()
task.complete("完成，1080 词", {"words": 1080})
print("proof:", task.proof["result_hash"])   # 可结算工作证明

# 3. 日报即数据：一天的公司运营留痕
report = DailyReport(roster, kb).generate()
print(report["content_asset"]["hook"])        # 获客素材（可发布）
```

## 设计要点

- **零依赖**（纯 stdlib），可独立使用；依赖方向 `microfirm ──▶ core`
- **验收标准先行**：`assign()` 无验收标准直接报错（标准不明不派活）
- **确定性轮值**：同一时刻同一值班者（小时级节拍，可测试）
- **工作证明**：每张完成的任务卡生成 `proof`（含 result_hash），接结算层入账
- **日报即获客**：运营留痕自动转内容素材（喂 ascii.im Blog SEO / Ximo 地推池）

## 测试

```bash
python3 packages/microfirm/tests/test_microfirm.py   # 8 tests OK
python3 run_all_tests.py                              # 全仓 ALL GREEN
```

## 时间表（规划）

- **2027**：四件套模板化（空仓库一键起项目），AgentSync 自跑一季作实证
- **2028**：ascii.im / TrayTool 单人开发者试点（免费尝鲜换案例）
- **2029**：开源 + 托管双形态（自托管本地优先 / 托管版按席位订阅）
