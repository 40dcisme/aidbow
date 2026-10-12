# Changelog

All notable changes to this project are documented here. SemVer.

## [Unreleased]
- `@aidbow/prompts`: base pack 新增 `select` 模板（TOP-N 优选：固定权重 P1/1.0·P2/0.8·P4/1.0·P5/0.8·P6/1.5·P7/1.2，P3 为门槛，同机制去重 ×0.6；**不产新创意**）。
- **Overview 自动化**：新增 `BaseOverviewLLM`（LLM 路径）与 `AgentOverview`（Agent 路径），产出统一 `OverviewResult`（clusters/conflicts/shortlist + idea_id 溯源）。
- core 扩展：`OverviewResult`/`OverviewCluster`/`OverviewConflict` + `LLMAdapter`/`AgentAdapter` 协议；`HarnessContext.summarizer`。
- SPEC §2.5：Overview 三路径（human/llm/agent）契约与抗幻觉约束。
- Added `@aidbow/core` (data model + extension contracts).
- Added `@aidbow/p-system` (base P rubric; **P6 split into P6-R1 / P6-R2**).
- Added `@aidbow/prompts` (base prompt pack; anti-hallucination + cross-domain consistency).
- Added `@aidbow/harness` (DBOW orchestration; swappable steps).
- Added `SPEC.md` (G1 extension-point contract), CI-smoke `run_all_tests.py`, MIT license.
