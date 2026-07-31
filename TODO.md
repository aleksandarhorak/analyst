# TODO

This template starts with no active project task.

Use this file only for active full-workflow implementation work. Do not use it
for answer-only requests, reviews, scoring, tiny documentation edits, or
temporary notes.

## Current Task

- [x] Define scope and acceptance criteria for the approved analyst-agent
  operational foundation.
- [x] Create `feature/analyst-operational-foundation` from clean local `dev`.
- [x] Complete current primary-source research and record the selected design.
- [ ] Add point-in-time financial-data acquisition contracts and adapters.
- [ ] Add an executable financial-agent evaluation runner and regression cases.
- [ ] Add forecast registration, outcome resolution, and calibration scoring.
- [ ] Enforce immutable symbol-research history and versioned migrations.
- [ ] Add commodity/futures analysis and client-data governance skills.
- [ ] Integrate the new controls into existing skills, templates, and policy.
- [ ] Run focused tests, all skill validators, and the full quality gate.
- [ ] Reset this file, review the final diff, and merge passing work into `dev`.

Acceptance criteria:

- Official SEC, FRED/ALFRED, and CFTC adapters emit a versioned evidence packet;
  price/news providers use a documented pluggable contract with no secrets.
- Evaluation cases execute deterministically and gate critical evidence,
  temporal, numerical, privacy, and decision-safety failures.
- Forecasts and outcomes are append-only and produce reproducible calibration
  metrics by horizon and instrument class.
- Symbol history rejects overwrite and verifies hashes; template migrations
  preserve populated content.
- New and updated skills validate and route correctly, including commodities,
  client data, sector valuation, acquisition, calibration, and watchlist use.
- Repository checks pass and the completed feature is merged locally into
  `dev`; publication remains out of scope.

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

1. Research dossier and architecture decision; verify with documentation checks
   and a stage quality gate.
2. Evidence schema, instrument registry, acquisition adapters, fixtures, and
   deterministic adapter tests; verify with focused tests and a stage gate.
3. Evaluation runner, forecast ledgers/calibration, cases, and exact numerical
   tests; verify critical-failure behavior and a stage gate.
4. Immutable history, migration tooling, watchlist integration, and repository
   validation; verify write-once and preservation tests plus a stage gate.
5. Commodity/futures and client-data skills plus valuation/evidence/suitability
   integrations; validate every skill and run a stage gate.
6. Final documentation, durable memory, full test/quality gates, TODO reset,
   work-branch commit, tested non-fast-forward merge, and clean-`dev` gate.

## Completion Rule

When all task items are done, replace temporary task details with a short
completed summary or reset this file to the empty template. Do not leave stale
task checklists behind after the final commit.
