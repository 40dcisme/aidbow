# Contributing

Thanks for helping aim AI better.

## Dev
- Python ≥ 3.9, **zero third-party runtime deps**.
- Run all tests: `python3 run_all_tests.py` (or a single package: `python3 packages/<pkg>/run_tests.py`).
- Style: see [`AGENTS.md`](AGENTS.md) (AI coding standards). Keep PRs focused; add/extend tests with every change.

## Contracts
- The extension-point interfaces live in [`SPEC.md`](SPEC.md). **Any breaking interface change is a major version** and must update SPEC + CHANGELOG.
- Implement interfaces; **do not fork** existing packages to customize — inject via `HarnessContext` / `overlay_dir` / `rubric=`.

## PR checklist
- [ ] tests pass (`run_all_tests.py`)
- [ ] no internal/confidential data, no secrets
- [ ] SPEC/CHANGELOG updated if interfaces changed
