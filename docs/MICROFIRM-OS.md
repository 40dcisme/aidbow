# Microfirm OS · 一人公司操作系统 —— 剖析 + 规划（aidbow 基座扩展）

> **来源**：777-014 头脑风暴 A-001-r2 创意 R2-03「一人公司 OS（Microfirm OS v1）」（P6=4 · S=0.83）
> **定位**：把 AgentSync 四件套纪律（798 registry / 800 assignments / 999 三件套 / 996 日报）产品化为 **「1 个自然人 + N 个 Agent」的最小公司运营系统**，作为 aidbow Creative OS 的 **W（Workflow）环节扩展**。
> **反共识**：AI 行业在卖模型和工具，被低估的是卖「纪律」这门生意——模型随时换，纪律越用越值钱。

---

## 一、概念剖析（为什么这是蓝海）

### 1.1 组织最小单位假说
- **2029 年 AI 把单人的生产能力推到企业级**：一个单人创业者带 5 个 Agent（内容/客服/结算/运维/增长）能同时跑三四个业务线。
- 组织的最小单位从「人 + 工具」变成 **「1 个自然人 + N 个 Agent」**——不是科幻，是成本算术。
- **瓶颈不是"不会用 AI"**，而是"没有一套公司壳把 Agent 团队的日常运营跑起来"：
  - 谁值班？活派给谁？谁验收？出了事升级给谁？每天产出记在哪？月底怎么算账？

### 1.2 市场空白
| 现有产品 | 卖什么 | 缺什么 |
|---|---|---|
| 协作工具（Notion/Linear）| 人与人的看板 | Agent 团队运营层 |
| Agent 平台（OpenAI/Claude）| 单个 Agent 的执行 | Agent 团队的公司化运营 |
| **Microfirm OS** | **Agent 团队运营层（公司壳）** | ← 填补空白 |

### 1.3 为什么是 aidbow 的扩展
aidbow = **DBOW 创意流水线**（Demand→Brainstorm→Overview→Workflow）。Microfirm OS 天然是 **W 环节**——把 Decision 变成可执行、可跟踪、可结算的 Workflow，并持续运营：
```
Demand → Brainstorm → Overview → Workflow（= Microfirm OS 的派活/值班/留痕/算账）
```

---

## 二、机制设计（三件机制，全部来自 AgentSync 实证）

### 机制 1 · 值班编排（Roster Orchestration）
- `roster.yaml` 定义 N 个 Agent 的 24×7 轮值与升级链
- 低优先级任务 Agent 自治；异常按链条升级到自然人；升级动作进 999 同款留痕
- **对齐 798 registry 的 sync_hours 节拍思想**

### 机制 2 · 任务队列即看板（Task Queue as Kanban）
- 把 999 inbox/TODO/PROGRESS 产品化为单人创业者的运营台
- 派活（给哪个 Agent）→ 验收（标准先行）→ 留痕（状态机 open/doing/done）
- **每张任务卡 = 一条可结算工作证明**（接 A-001#03 结算协议）

### 机制 3 · 日报即数据（Daily Report as Data）
- 996 式日报 + iPlan 快照自动生成
- 既是审计证据、也是结算依据、还是**获客素材**（真实单人公司的运营留痕 = 稀缺内容资产，喂 ascii.im Blog SEO 与 Ximo 地推素材池）

---

## 三、团队卡位（AgentSync 就是 v0）

| 真实资产 | 在 Microfirm OS 中的角色 |
|---|---|
| **798 registry**（16 Agent 在册 + synced_at 心跳）| 人事档案 + 心跳 = 值班编排的数据源 |
| **800 assignments**（编组 + DRI）| 角色/编组 = 派活的依据 |
| **999 inbox/TODO/PROGRESS**（派发/收交/验收）| 任务队列 = 看板机制 |
| **996 日报 + iPlan**（工时/产出留痕）| 日报 = 数据机制 |
| **ascii.im**（付费+API+统计+Blog SEO）| 计费 + 埋点 + 获客组件 |
| **TrayTool G-03**（本地优先零追踪）| 自托管形态背书 |
| **Ximo 地推池** | 获客素材 |

> **我们就是第一个客户**——AgentSync 已用四件套跑了两个多月（真实运行），Microfirm OS 的 v0 就是 AgentSync 本身。

---

## 四、时间表（2027-2029）

| 阶段 | 年份 | 动作 |
|---|---|---|
| **内部制度化** | 2027 | 四件套模板化（空仓库一键起项目：registry/assignments/inbox/TODO/PROGRESS/日报骨架），AgentSync 自身跑满一季作首批实证 |
| **试点** | 2028 | 在 ascii.im/TrayTool 的单人开发者与小工作室用户中试点（模板 + 脚本 + 部署位，免费尝鲜换案例）|
| **开源 + 托管** | 2029 | 双形态：自托管（守 G-03 本地优先）+ 托管版（挂结算层按席位订阅计费），「一人公司 OS」成为 Agent 经济供给侧新品类 |

---

## 五、风险与对策

| 风险 | 对策 |
|---|---|
| 「卖纪律」像咨询不像产品 | 交付物全部 git 化（模板/脚本/状态机），买走即自运转 |
| 与巨头免费协作工具竞争 | 先吃「Agent 员工」新人事品类（巨头没定义）|
| 单人客户付费能力弱 | 按年订阅 + 模板市场（新增 Agent 角色 = 可售模板）|
| 与 A-014#03 编制部重复 | 划界：雇主侧（企业 HR 台账）vs 业主侧（1 人公司壳），接口互补 |

---

## 六、落地：添加为 aidbow 包 `@aidbow/microfirm`

### 6.1 包定位
```
packages/microfirm
├── aidbow_microfirm/
│   ├── roster.py         # 值班编排（roster.yaml 解析 + 轮值 + 升级链）
│   ├── kanban.py         # 任务队列（open/doing/done 状态机 + 验收标准）
│   ├── ledger_report.py  # 日报即数据（996 式日报 + iPlan 快照生成）
│   └── __init__.py
├── pyproject.toml
├── README.md
└── tests/
```
- **依赖方向**：`microfirm ──▶ core`（数据模型），不依赖 p-system/harness（可独立用）
- **接口**：与 SPEC §1 数据模型对齐（Demand/Idea/Workflow Spec）

### 6.2 SPEC 扩展（§4 包清单加一行）
```
microfirm ──▶ core（一人公司运营层：值班/派活/留痕/算账）
```

### 6.3 与既有包的关系
- **harness**：Microfirm OS 是 W 环节的**执行器扩展**（workflow 派发 + 值班）
- **review-ui**：任务看板可复用 review-ui 的卡片交互
- **p-system**：任务验收可挂 P 值卡（工作证明的评分依据）

---

## 七、交付物（本次落地）

- [x] 本规划（剖析 + 机制 + 时间表 + 风险）
- [x] SPEC.md 扩展（§4 包清单 + §0 术语）
- [ ] packages/microfirm 骨架（roster/kanban/ledger_report）
- [ ] 示例（examples/microfirm_demo.py：单人 + 3 Agent 跑一周的演示）

---

*A-016 芙妮（AA001）· 2026-11-08 · 来源 777-014 A-001-r2 R2-03（P6=4 · S=0.83）· 规划基于 AgentSync 四件套真实运行实证*
