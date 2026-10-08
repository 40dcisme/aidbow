# Aidbow Creative OS

> **AI, aimed.** — Draw ideas. Loose outcomes.
> The open-core framework for the **DBOW** pipeline: **D**emand → **B**rainstorm → **O**verview → **W**orkflow.

Aidbow gives AI agents the one thing they lack — **aim**. Your agents execute brilliantly; this framework makes them *think first, verify, and only then act*. It is the open-core base; a closed **precision layer** (project-tuned P-metrics, production harness, refined prompts) builds on top **without forking**.

## Why
Modern agents converge, hallucinate and misread cross-domain context. Aidbow structures divergence, grounds synthesis, and keeps a human in the loop before anything ships.

## Packages
| Package | Role |
|---|---|
| [`@aidbow/core`](packages/core) | DBOW data model + extension contracts (zero deps) |
| [`@aidbow/p-system`](packages/p-system) | P-metric engine, base rubric (P6 split into R1/R2) |
| [`@aidbow/prompts`](packages/prompts) | Base prompt pack (anti-hallucination, cross-domain consistency) |
| [`@aidbow/harness`](packages/harness) | Orchestration harness, swappable steps |
| `@aidbow/context` | Context providers (text / link / file) |
| `@aidbow/review-ui` | Review & decision board |
| `@aidbow/adapters` | LLM / retrieval adapters |

## Quick start
> **New here? → [QUICKSTART (5-minute, zero-config run)](docs/QUICKSTART.md)**

```bash
git clone --depth 1 https://github.com/40dcisme/aidbow.git && cd aidbow
python3 examples/run_demo.py      # end-to-end DBOW demo → ends with: ✅ DEMO OK
python3 run_all_tests.py          # all package tests   → ends with: ✅ ALL GREEN
python3 scripts/check_env.py      # environment check   → ends with: ✅ READY
```
No third-party dependencies, no network, no API key required.
```python
import sys; [sys.path.insert(0, f"packages/{p}") for p in ["core","p-system","prompts","harness"]]
from aidbow_core import Demand, Idea
from aidbow_p_system import BasePEvaluator
from aidbow_harness import BaseHarness

idea = Idea(id="a:1", author="anon", round="R1", title="t", oneLiner="o", body="**正文**：" + "字"*500)
print(BasePEvaluator().evaluate(idea).P)          # {'P3': 3, ...}
print(BaseHarness(evaluator=BasePEvaluator()).run(Demand(id="d1", prompt="..."))["trace"])
```

## Extending (no fork)
The closed precision layer implements the same interfaces and injects via `HarnessContext` / `overlay_dir` / `rubric=`.
See [`SPEC.md`](SPEC.md) for the extension-point contract.

## License
MIT — see [LICENSE](LICENSE).

> A bow without tension is just a stick.
