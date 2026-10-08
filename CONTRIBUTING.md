# Contributing

Thanks for helping aim AI better.

## Dev
- Python ≥ 3.9, **zero third-party runtime deps**.
- Run all tests: `python3 run_all_tests.py` (or a single package: `python3 packages/<pkg>/run_tests.py`).
- Style: see [`AGENTS.md`](AGENTS.md) (AI coding standards). Keep PRs focused; add/extend tests with every change.

## Contracts
- The extension-point interfaces live in [`SPEC.md`](SPEC.md). **Any breaking interface change is a major version** and must update SPEC + CHANGELOG.
- Implement interfaces; **do not fork** existing packages to customize — inject via `HarnessContext` / `overlay_dir` / `rubric=`.

## 协作规程（Agent 与人类一致）
1. **先同步基线**：`git fetch origin && git rebase origin/main`（**务必**：分支落后 main 会导致合并回退新代码）。
2. **在分支上工作**：`feat/<pkg>-<name>`，**不要直接 push main**。
3. **本地先跑测试**：`python3 run_all_tests.py` 全绿。
4. **push 分支**：`git push origin feat/<pkg>-<name>` → **GitHub Actions 自动为本分支开 PR**（无需本地 token）。
5. **回报**：把分支名 + commit SHA 写回你的任务卡 DONE 段。
6. 维护者：CI 绿 + `SPEC.md` 契约对齐后合并 main。

> 机制说明：CRON 会话**无本地 GitHub token**，故 PR 由 repo 内 `auto-pr.yml` 用 runner 的 `GITHUB_TOKEN` **自动创建**；Agent 只需**推分支 + 回报**。

## PR checklist
- [ ] tests pass (`run_all_tests.py`)
- [ ] no internal/confidential data, no secrets
- [ ] SPEC/CHANGELOG updated if interfaces changed
