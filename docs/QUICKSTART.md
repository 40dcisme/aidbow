# QUICKSTART · 跑通 Aidbow DBOW（小白 / 新 Agent 专用）

> 目标：**独立克隆后，一条命令跑通完整技术框架，并看到预期成果。**
> 全程 **零配置、零第三方依赖、无需联网、无需 API Key**。只要机器有 **Python 3.9+**。

---

## 0. 前置检查

```bash
python3 --version     # 需要 >= 3.9
```

> 没有 Python？Ubuntu/Debian：`sudo apt-get install -y python3`；macOS：`brew install python`；Windows：到 python.org 下载安装。
> **本项目只用标准库**，因此不需要 `pip install` 任何东西。

---

## 1. 获取代码（浅克隆，快）

```bash
git clone --depth 1 https://github.com/40dcisme/aidbow.git
cd aidbow
```

---

## 2. 一条命令跑通（推荐先跑这个）

```bash
python3 examples/run_demo.py
```

**预期成果**：依次打印 `[1/5]…[5/5]`，末尾出现：

```
✅ DEMO OK
```

以及一段 `OverviewResult` JSON（`method: "llm"`，含 `clusters / shortlist / provenance`）。

> 它走了完整 DBOW：**Demand → Brainstorm → (P 值评估) → Overview → Workflow**。

---

## 3. 跑全部测试（确认环境完好）

```bash
python3 run_all_tests.py
```

**预期成果**：每个包 `N passed, 0 failed`，最后一行：

```
✅ ALL GREEN
```

---

## 4. 自检脚本（逐项体检）

```bash
python3 scripts/check_env.py
```

**预期成果**：逐项 `[OK]`，末尾 `✅ READY`。若某项 `[FAIL]`，按提示修。

---

## 5. 打开可视化评审台（可选，看创意全貌）

```bash
python3 examples/run_review.py       # 用示例数据生成一个自包含 HTML
# 然后在浏览器打开打印出的文件（review_demo.html）
```

---

## 6. 你自己动手：最小可改代码

```python
import sys
sys.path[:0] = [f"packages/{p}" for p in ["core","p-system","prompts","harness"]]

from aidbow_core import Demand, Idea, Decision
from aidbow_p_system import BasePEvaluator
from aidbow_harness import BaseHarness

demand = Demand(id="d1", prompt="给你的产品想 3 个增长点子")
ideas  = [Idea(id="a:1", author="me", round="R1", title="t", oneLiner="o",
               body="**正文**：" + "内容"*300, P={"P2":4})]

ev = BasePEvaluator()
print("P 值:", ev.evaluate(ideas[0], demand).P)     # {'P3': 5, ...}(篇幅自动算)

h = BaseHarness(evaluator=ev)
print("流程:", h.run(demand)["trace"])              # ['demand','brainstorm','overview','workflow']
```

---

## 7. 接真实大模型（进阶，可选）

`@aidbow/adapters` 内置 `OpenAICompatAdapter`，**密钥只从环境变量读**：

```bash
export AIDBOW_LLM_BASE_URL="https://<你的兼容端点>/v1"
export AIDBOW_LLM_API_KEY="<你的密钥>"
```
```python
import sys; sys.path[:0]=[f"packages/{p}" for p in ["core","adapters","harness"]]
from aidbow_adapters import OpenAICompatAdapter
llm = OpenAICompatAdapter()                 # 读上面两个环境变量
# 传给 BaseOverviewLLM(llm) 即可让 Overview 走真实模型
```

> 不配置也能跑：`examples/run_demo.py` 用的是内置**离线 DemoLLM**。

---

## 8. 概念速查（30 秒看懂）

| 词 | 含义 |
|---|---|
| **DBOW** | Demand→Brainstorm→Overview→Workflow 四段流水线 |
| **Idea** | 一条创意（正文 + P 值卡） |
| **P 值** | 7 维评分（P1 相关…P7 可行）；P3 篇幅由代码自动计算；P6 拆成 R1/R2 |
| **Overview** | 汇总收敛；可**人审**、可 **LLM**、可 **Agent** 三条路径（`OverviewResult`） |
| **扩展不 fork** | 用 `overrides=` / `overlay_dir=` / `rubric=` 注入，不改源码 |

---

## 9. 常见问题

| 症状 | 处理 |
|---|---|
| `ModuleNotFoundError: aidbow_core` | 你直接跑的是包内脚本；用仓库根的 `examples/run_demo.py`（已自动配好路径） |
| `python3: command not found` | 装 Python 3.9+（见 §0） |
| 测试里有 `GraphQL`/网络报错 | 本框架**不需要联网**；是你加的第三方代码在联网，移除即可 |
| 中文乱码 | 终端设 UTF-8：`export PYTHONUTF8=1`（或 `chcp 65001` on Windows） |

---

**跑通了？** 恭喜——你已经掌握了 Aidbow 的全部入口。下一步看 [`SPEC.md`](../SPEC.md)（接口契约）与 [`CONTRIBUTING.md`](../CONTRIBUTING.md)（如何贡献）。
