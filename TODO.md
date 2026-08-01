# TODO

This template starts with no active project task.

Use this file only for active full-workflow implementation work. Do not use it
for answer-only requests, reviews, scoring, tiny documentation edits, or
temporary notes.

## Current Task

- [x] Make the exact command `do symbols research` execute and document a
  resumable, full-depth, applicable analytical pipeline for every active
  symbol, with deterministic checks that reject shallow coverage-only batches.

### Scope And Acceptance Criteria

- [x] Define one explicit command contract covering identity/evidence, price,
  company fundamentals, valuation, complete impersonal thesis, news, shared
  macro with symbol transmission, observable behavior, four-horizon forecasts
  or justified abstention, downside/5x risk, and durable histories.
- [x] Require the agent to continue all non-dependent research when one input is
  missing; a missing price may block price-dependent valuation/probabilities
  but must not excuse feasible filing, business, catalyst, macro, or risk work.
- [x] Distinguish mandatory per-symbol work from conditional portfolio,
  suitability, execution, historical-claim, and agent-evaluation workflows.
- [x] Make long batches resumable, checkpointed, and parallel by independent
  symbol/analysis lanes with one cutoff, one writer per path, and central
  verification/synthesis.
- [x] Extend templates and deterministic validators with an explicit depth
  ledger so generic `insufficient evidence` text cannot satisfy the command.
- [x] Add adverse regression fixtures for shallow blanket abstention, partial
  completion, invalid stop propagation, and conditional-workflow overreach.
- [x] Align AGENTS.md, skill metadata, README, prompt cookbook, quickstart, and
  troubleshooting guidance with the strengthened command.
- [ ] Validate the skill folder, forward-test behavior, pass focused tests and
  the full quality gate, then merge into clean local `dev`.

### Work Branch And Commit Boundaries

- [x] Work only on `feature/full-depth-symbol-research`.
- [ ] Commit the command/skill/template contract after focused validation.
- [ ] Commit deterministic validators, fixtures, and regression tests after
  their focused suite and stage gate pass.
- [ ] Commit documentation/metadata alignment and independent forward-test
  findings after link and skill validation.
- [ ] Reset this plan, run the final work-branch gate, merge non-fast-forward
  into local `dev`, and rerun the merged-state gate.

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

1. Audit the current trigger, contract, templates, validators, evaluations, and
   documentation against the user's full-depth semantics.
2. Implement the mandatory-versus-conditional workflow, depth ledger,
   continuation rules, checkpoints, and parallel ownership contract.
3. Add deterministic validator assertions and adverse evaluation fixtures that
   distinguish legitimate scoped abstention from shallow blanket abstention.
4. Align agent policy, metadata, README, prompt cookbook, quickstart, and
   troubleshooting guidance.
5. Forward-test the revised skill with an independent agent, review the diff,
   reset TODO.md, run final gates, commit, and merge into local `dev`.

### Verification Commands

- `python3 scripts/check-symbol-research.py`
- `python3 scripts/test-symbol-history.py`
- `python3 scripts/test-financial-evals.py`
- `python3 scripts/check-docs.py`
- `python3 /home/box/.codex/skills/.system/skill-creator/scripts/quick_validate.py .codex/skills/research-symbol-watchlist`
- `scripts/agent-quality-gate.sh --stage`
- `git diff --check`
- `scripts/agent-quality-gate.sh`

## Completion Rule

When all task items are done, replace temporary task details with a short
completed summary or reset this file to the empty template. Do not leave stale
task checklists behind after the final commit.
