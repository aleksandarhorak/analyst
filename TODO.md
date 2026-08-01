# TODO

This template starts with no active project task.

Use this file only for active full-workflow implementation work. Do not use it
for answer-only requests, reviews, scoring, tiny documentation edits, or
temporary notes.

## Current Task

- [x] Define scope and acceptance criteria for the financial-agent hardening.
- [x] Create `feature/strengthen-financial-agent` from clean local `dev`.
- [x] Inspect the audit findings, affected contracts, scripts, fixtures, and tests.
- [x] Plan implementation stages and verification commands.
- [x] Remove evaluation-answer leakage and add complete regression metadata.
- [x] Expand public adverse cases across every analytical and safety lane.
- [x] Add a versioned instrument registry and validate all adapter identities.
- [x] Enforce evidence schema, freshness, session, currency, and timestamp rules.
- [x] Correct forecast-ledger integrity wording or implement the documented chain.
- [x] Expand client-data leak detection and synthetic self-tests.
- [ ] Run focused validators and the stage quality gate after each implementation stage.
- [ ] Commit each completed stage on the feature branch.
- [ ] Run the complete current watchlist workflow or record explicit evidence-bounded abstentions.
- [ ] Run a leakage-safe baseline/candidate evaluation and review every critical result.
- [ ] Update durable memory and operational documentation.
- [ ] Review final diff and status, reset this task plan, and run the final gate.
- [ ] Merge automatically into `dev` and verify the clean merged state.

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

### Stage 1 — Evaluation integrity

- Candidate stdin contains only case ID, lane, prompt, and cutoff; scoring
  assertions and expected values never cross the candidate boundary.
- Runner records separate public/holdout hashes, scorer/rubric hash, candidate
  command hash, repeat count, baseline/candidate comparison, and critical cases.
- Tests prove scoring-key leakage is impossible and cover malformed case fields.
- Public cases include evidence, company, valuation, macro, news, portfolio,
  execution, suitability, privacy, market integrity, and abstention behavior.
- Commit boundary: `Harden financial agent evaluations`.

### Stage 2 — Evidence identity and time

- A versioned registry covers resolved securities and explicitly unresolved
  commodity/index aliases without converting ticker similarity into identity.
- Provider responses match ID, symbol, venue, asset class, requested currency,
  requested session, and maximum age; stale or inconsistent data fails closed.
- SEC fixture acquisition reconciles the response CIK and does not accept an
  issuer mismatch.
- Existing packet validation enforces the complete `evidence-packet-v1`
  structure without external dependencies.
- Regression tests cover stale observations, same-ID identity mismatches,
  wrong currency/session, SEC identity mismatch, and malformed packets.
- Commit boundary: `Enforce evidence identity and freshness`.

### Stage 3 — Ledger and privacy integrity

- Forecast and outcome ledgers use an accurately documented integrity model;
  any chain implementation is verified across appended records.
- Outcome inputs remain evidence-linked and scoring output exposes sparse-sample
  limitations and baseline comparisons.
- Client-data checks cover common identity, account, contact, payment, and
  credential representations in operational artifacts with synthetic tests.
- Commit boundary: `Strengthen ledger and privacy safeguards`.

### Stage 4 — Operational proof

- Focused regressions and `scripts/agent-quality-gate.sh --stage` pass.
- Every active watchlist symbol receives a current, sourced snapshot or an
  explicit, reasoned `insufficient evidence` result; aliases remain unresolved
  unless exact product specifications are available.
- Any published probabilities are preregistered before publication; otherwise
  the four horizons remain explicit abstentions.
- A complete root report reconciles all active symbols and immutable histories.
- Leakage-safe evaluation artifacts show baseline/candidate results; fixture
  replay is labeled only as harness verification.
- Commit boundary: `Complete verified operational evidence`.

### Stage 5 — Delivery

- Durable facts are updated in `MEMORY.md`; temporary task details are removed.
- Final diff, focused tests, and full quality gate pass on the feature branch.
- A prepared non-fast-forward merge passes the full gate on `dev`, the merge is
  committed, and the clean merged tree passes again.

## Verification Commands

- `python3 scripts/test-financial-evals.py`
- `python3 scripts/test-financial-data.py`
- `python3 scripts/test-forecast-calibration.py`
- `python3 scripts/check-client-data.py --self-test`
- `python3 scripts/check-symbol-research.py`
- `python3 .codex/skills/research-symbol-watchlist/scripts/symbol_research_history.py verify --repo-root .`
- `scripts/agent-quality-gate.sh --stage`
- `scripts/agent-quality-gate.sh`

## Completion Rule

When all task items are done, replace temporary task details with a short
completed summary or reset this file to the empty template. Do not leave stale
task checklists behind after the final commit.
