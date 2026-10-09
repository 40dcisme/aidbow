# AGENTS.md — AI coding standards (Aidbow Creative OS)

Binding rules for any AI/agent contributing code here.

## 1. Zero-dependency core
- `packages/*` runtime code uses **stdlib only**. No third-party imports at runtime.
- Tests use the bundled `run_tests.py` (no pytest required).

## 2. Contract-first
- All public types/interfaces MUST match [`SPEC.md`](SPEC.md) exactly (names, fields, signatures).
- Implement `aidbow_core` protocols; never import a sibling package to reach its internals — depend **downward only** (`core` is the floor).

## 2b. Interface SSOT & cross-package integration
- Reuse `aidbow_core`'s protocols as the **single source of truth**; never redefine a same-named interface with a different shape.
- Every implementation of a core protocol MUST ship a **cross-package integration test** that injects it into its real consumer (not only its own unit tests). Method-name drift (e.g. `complete` vs `generate`) passes unit tests but breaks integration.

## 3. No fabrication
- Never invent data, scores or citations. Computed metrics (e.g. P3) must be reproducible; self-reported values must carry a `basis`.
- If information is missing, emit an explicit `待补/unknown` marker — do not guess.

## 4. Extension over fork
- To customize: implement an interface or provide an override (`overrides=`, `overlay_dir=`, `rubric=`). Do **not** copy-and-edit a package.

## 5. Data hygiene (red line)
- The public repo must contain **no** internal/confidential data: no internal IDs, no project-codenames, no secrets, no client assets.

## 6. Tests & clarity
- Every behavior change ships with a test; keep functions small and named for intent; comments in the repo's shared language are fine, public API names in English.

## 7. Commits
- Conventional, scoped messages (`core: add WorkflowSpec validation`); one logical change per commit.
