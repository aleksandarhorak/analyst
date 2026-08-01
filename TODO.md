# TODO

## Current Task

- [x] Define scope and acceptance criteria for the operational agent upgrade.
- [x] Create `feature/operational-agent-guide` from clean local `dev`.
- [x] Inventory affected policy, documentation, provider contracts, evaluations,
  fixtures, tests, and quality gates.
- [x] Add bounded parallel-agent policy and regression coverage.
- [x] Replace the long root guide with a concise task map and five-minute path.
- [x] Move copy-ready recipes to `docs/PROMPTS.md`.
- [x] Add a worked example, expected outputs, and troubleshooting guidance.
- [x] Document authorized provider onboarding and add a safe preflight diagnostic.
- [ ] Document real-candidate, controlled-holdout, and blinded-review operations.
- [ ] Record licensed feeds, external candidates/reviewers, secret holdouts, and
  matured outcomes as external prerequisites; never fabricate their presence.
- [ ] Run focused regressions and the stage gate for every commit boundary.
- [ ] Update durable memory, reset this task plan, and run the final gate.
- [ ] Merge automatically into local `dev` and verify the clean merged state.

## Scope And Acceptance Criteria

- The lead agent uses available subagents for two or more genuinely independent,
  useful workstreams, with one cutoff, explicit ownership, safe data boundaries,
  centralized synthesis, and no shared-file collisions.
- Skill reading, regulated final judgments, client-data authorization, Git
  integration, and final verification remain lead-agent responsibilities.
- An adverse evaluation case rejects unsafe or incoherent delegation behavior.
- Root `README.md` provides a short orientation, task-selection table, five-minute
  walkthrough, limitations, and links to deeper material.
- `docs/PROMPTS.md` holds copy-ready prompts; provider and evaluation runbooks
  provide exact commands, prerequisites, failure states, and troubleshooting.
- A provider preflight invokes an adapter without a shell, keeps credentials in
  its environment, uses registry-bound identity, validates price and news
  responses, and leaves no licensed payload in the repository.
- The evaluation runbook distinguishes fixture verification from a real model,
  protects holdouts, requires repeated baseline comparison and blinded human
  review, and does not claim forecast skill without registered outcomes.

## Staged Work

### Stage 1 — Parallel Policy And Evaluation

- Update `AGENTS.md` with bounded parallel-work rules.
- Add an adverse public case and passing fixture for delegation governance.
- Extend deterministic checks for the policy and changed case count.
- Verify with `python3 scripts/test-financial-evals.py` and the stage gate.
- Commit boundary: `Govern parallel financial analysis`.

### Stage 2 — User Guide And Prompt Cookbook

- Make root `README.md` concise and task-oriented.
- Add `docs/QUICKSTART.md`, `docs/PROMPTS.md`, and
  `docs/TROUBLESHOOTING.md` with a worked example and output map.
- Validate local links, documentation claims, and the stage gate.
- Commit boundary: `Add operational agent guides`.

### Stage 3 — Provider Operations

- Add provider onboarding documentation and an executable preflight diagnostic
  with synthetic command-path regressions.
- Harden subprocess environment/output bounds, exact schemas, news identity and
  timing, cutoff enforcement, and validate-before-write behavior.
- Verify provider focused tests and the stage gate.
- Commit boundary: `Secure provider onboarding`.

### Stage 4 — Evaluation Operations

- Add a real-candidate/hidden-holdout/blinded-review runbook and reviewer
  template or validation where useful.
- Update durable operational limits without implying external services exist.
- Verify evaluation focused tests and the stage gate.
- Commit boundary: `Operationalize real model evaluation`.

### Stage 5 — Delivery

- Review the final diff, reset `TODO.md`, and run the full feature-branch gate.
- Prepare a non-fast-forward merge into local `dev` and run the full gate.
- Commit the merge and rerun the full gate on clean `dev`.

## Verification Commands

- `python3 scripts/test-financial-evals.py`
- `python3 scripts/test-financial-data.py`
- `python3 scripts/check-client-data.py --self-test`
- `scripts/agent-quality-gate.sh --stage`
- `scripts/agent-quality-gate.sh`
- Local Markdown-link existence check for root and `docs/` files.

## Completion Rule

Reset this file to the empty template after every observable task item is
complete and before the final full gate. Do not mark licensed data, secret
holdouts, independent review, a real candidate run, or matured outcomes complete
unless those external resources actually exist and have been verified.
