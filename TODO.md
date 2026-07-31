# TODO

This template starts with no active project task.

Use this file only for active full-workflow implementation work. Do not use it
for answer-only requests, reviews, scoring, tiny documentation edits, or
temporary notes.

## Current Task

- [ ] Build a researched, repeatable `do symbols research` workflow with current
      online prices/news, per-symbol long memory, directional-probability reports,
      behavioral-market analysis, USD reporting, and explicit 5x leverage risk.

### Scope And Acceptance Criteria

- [x] Research primary behavioral-finance evidence on attention, sentiment,
      underreaction, overreaction, loss aversion, extrapolation, herding, and
      trader response; record full-review findings and limitations.
- [x] Add a bounded market-behavior skill and a batch symbol-research skill that
      triggers on `do symbols research` and composes existing evidence, news,
      macro, company, valuation, portfolio, and execution skills.
- [x] Create deterministic per-symbol research folders from the active universe
      in `SYMBOLS.md`, preserving decision history as symbols are added or
      archived.
- [x] Add root `REPORT.md` and per-symbol templates for current price/news,
      behavioral response, short-term and long-term up/flat/down probabilities,
      confidence, risks, invalidation, and evidence links.
- [x] Define short-term horizons as 1 trading day and 2 weeks, long-term horizons
      as 1 month and 2 months, with USD as reporting currency and separate
      unlevered and 5x linear-exposure risk before financing, margin calls, and
      liquidation effects.
- [x] Require current online sources, exact instrument resolution, probability
      sums of 100%, explicit flat bands, no invented probabilities, and a visible
      `insufficient evidence` result when calibration is not defensible.
- [ ] Validate skills, folder synchronization, report coverage, adverse cases,
      shell scripts, and the final repository gate; commit stages and merge the
      passing branch into local `dev`.

### Work Branch And Commit Boundaries

- Branch: `feature/symbol-research-workflow`.
- Stage 1: behavioral-finance research dossier and architecture decision.
- Stage 2: skills, templates, symbol-memory folders, report, and agent routing.
- Stage 3: deterministic integrity checks, evaluation fixtures, durable memory,
  and final cleanup.

### Staged Checklist

- [x] Stage 1: complete behavioral-finance paper review and write research
      `README.md`, `sources.md`, `papers/manifest.md`, and `decision.md`.
- [x] Stage 1: verify research inventory, run the stage gate, review, and commit.
- [x] Stage 2: initialize and implement `analyze-market-behavior` and
      `research-symbol-watchlist` with references and deterministic helpers.
- [x] Stage 2: create/synchronize every active symbol folder and root report,
      then update `AGENTS.md`, `SYMBOLS.md`, and skill routing.
- [x] Stage 2: validate both skills, templates, links, horizons, probability
      controls, and leverage safeguards; run the stage gate and commit.
- [ ] Stage 3: extend integrity checks and add representative regression fixtures
      for stale prices, missing news, ambiguous aliases, probability arithmetic,
      narrative-only psychology, and 5x downside.
- [ ] Stage 3: update durable memory, run syntax/regression/skill/final gates,
      reset `TODO.md`, commit, prepare a tested merge, and verify clean `dev`.

### Verification Plan

- Skill creator `quick_validate.py` for both new skills and all changed skills.
- Run the symbol-folder synchronization/check helper twice to prove idempotence.
- Assert 38 active universe symbols, 38 research folders, four required horizons,
  USD and 5x disclosure, working relative evidence links, and empty placeholders
  rather than fabricated prices or probabilities before a live run.
- `bash -n scripts/*.sh scripts/git-hooks/pre-commit` and focused regression tests.
- `scripts/check-financial-agent.sh`, stage gates, final gate, prepared-merge
  gate, and clean merged-state gate.

## Full Workflow Template

When a full-workflow task starts, replace `None` with:

- [ ] Define scope and acceptance criteria.
- [ ] Create or resume the matching `fix/*` or `feature/*` branch.
- [ ] Inspect relevant files and existing patterns.
- [ ] Plan implementation stages.
- [ ] Implement and commit each completed, verified stage on the work branch.
- [ ] Run affected validators or builds.
- [ ] Run focused tests.
- [ ] Run broader checks when risk requires them.
- [ ] Update durable memory if new project facts were learned.
- [ ] Review final diff and status.
- [ ] Confirm `TODO.md` is reset or contains only a completed summary.
- [ ] Run the final work-branch quality gate.
- [ ] Merge automatically into `dev` and verify the merged state.

## Staged Work

Add task-specific stages here when a real task needs them. Keep each stage tied
to an observable edit, check, or decision.

## Completion Rule

When all task items are done, replace temporary task details with a short
completed summary or reset this file to the empty template. Do not leave stale
task checklists behind after the final commit.
