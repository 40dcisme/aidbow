# review-ui · 评审决策台

> 状态：R1 完成 · 承包人 A-003（墨格）· Reviewer A-016
> 约束：**零三方运行时依赖**（仅 Python 标准库 + 浏览器原生 JS），离线自包含，双击即用。

SPEC §2.4 扩展点 #4 对应包。把一轮收齐的创意做成**离线评审台**：勾选入选 → 定优先级
（P0/P1/P2/搁置）→ 写评审备注 → 一键导出 SPEC §1 Decision（Markdown / JSON）。

## 为什么这样设计

- **评审人只需要一个浏览器**：生成单个 HTML，CSS/JS/数据全部内联，零外链、无网络、
  无服务端；飞书/邮件发出去就能评，评完把导出的 `.md/.json` 回传即可。
- **数据契约就是 SPEC**：输入严格校验 §1 的 `Idea[]`，输出严格产出 §1 的 `Decision`，
  校验失败带「第几条、哪个字段、为什么」的可读错误，不静默吞数据。
- **Python 与浏览器同一口径**：Markdown 排版同时存在于 `decision_export.py`（CLI /
  测试）与页面 JS（浏览器），并有测试锁定一致行为。

## 用法

### CLI：生成评审页

```bash
# 输入 JSON 顶层为 Idea[] 或 {"demandId": "...", "ideas": [...]}
PYTHONPATH=packages/review-ui python -m aidbow_review_ui ideas.json -o review.html
PYTHONPATH=packages/review-ui python -m aidbow_review_ui ideas.json \
    --demand-id demo-001 --title "春季选题评审" -o review.html
```

打开 `review.html`：勾选卡片 → 选优先级 → 写备注 → 底部导出（预览/复制/下载）。
决策实时保存在浏览器 localStorage（刷新不丢，与输入 demandId 绑定）。

### CLI：从状态文件直接导出（CI / 二次集成）

状态 JSON 结构：`{idea_id: {picked, priority, note}}`

```bash
PYTHONPATH=packages/review-ui python -m aidbow_review_ui ideas.json \
    --print-markdown state.json
PYTHONPATH=packages/review-ui python -m aidbow_review_ui ideas.json \
    --print-json state.json   # 输出 SPEC §1 Decision JSON
```

### Python API

```python
from aidbow_review_ui import (
    load_ideas, write_page,            # 校验加载 / 生成 HTML
    decision_to_json, decision_to_markdown, validate_decision,
)

ideas = load_ideas("ideas.json")
write_page(ideas, "review.html", demand_id="demo-001")

state = {i["id"]: {"picked": True, "priority": "P0", "note": "做"} for i in ideas[:2]}
validate_decision(ideas, decision_to_json(ideas, state))   # 交叉校验
print(decision_to_markdown(ideas, state))
```

## 页面功能

- 卡片：编号 / 作者 / 轮次（R1·R2 双色标签）/ R2 递进来源（deepen·pivot·rebut 来自 lineage）/
  P 值徽章（≥4 高亮）/ 正文展开 / 评分依据（basis）。
- 筛选：轮次、作者、仅看已勾选；一键清空勾选。
- 决策：勾选 + 优先级（P0 立即做 / P1 本轮做 / P2 排期做 / 搁置）+ 备注。
- 导出：Markdown 决策单（选中/备选/搁置分区）与 Decision JSON，支持预览、复制、下载。
- 安全：所有插入 DOM 的内容走 HTML 转义；数据经定向转义内联，无法闭合 `<script>`。

## 文件

```
packages/review-ui/
├── aidbow_review_ui/
│   ├── models.py            # Idea[] 加载与校验（SPEC §1）
│   ├── decision_export.py   # 状态 → Decision JSON / Markdown + 交叉校验
│   ├── page.py              # 模板 + 数据 → 自包含 HTML
│   ├── cli.py               # 命令行入口
│   └── static/
│       ├── index.html       # 页面模板（内联 CSS）
│       └── app.js           # 原生 JS 前端（内联进产物）
├── examples/ideas.demo.json # 去敏示例（通用"城市公园周末活动"主题）
├── tests/test_review_ui.py  # 31 个用例
├── smoke_cdp.py             # CDP 无头交互冒烟（渲染/勾选/导出/筛选）
├── run_tests.py
└── pyproject.toml
```

## 测试

```bash
python packages/review-ui/run_tests.py          # 31 个单元测试（unittest，零依赖）
python packages/review-ui/smoke_cdp.py <url>    # Edge 无头交互冒烟
```

覆盖：必填校验 / P 值 1-5 整数且拒绝 bool / round 与 lineage 校验 / id 唯一 /
自包含性（无外链、模板占位符全部填充）/ XSS 转义 / Python 与 JS 导出分区口径一致 /
Decision 交叉校验（selected 必须存在、priority 合法）。

## 设计边界（不做的事）

- 不做服务端、不做账号体系、不做多评审人合并——评审是单人离线动作；多评审人各导一份
  Decision，由调用方（harness 或人工）合并。
- 不打分：P 值由 agent 在创意卡内填写并自证 basis，本组件只展示，不替创意方改分。
- 不绑定具体项目文案：示例数据全部为通用去敏主题，无任何内部话题/客户信息。
