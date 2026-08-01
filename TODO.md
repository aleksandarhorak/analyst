# TODO

This template starts with no active project task.

Use this file only for active full-workflow implementation work. Do not use it
for answer-only requests, reviews, scoring, tiny documentation edits, or
temporary notes.

## Current Task

- [ ] Complete the `2026-08-01T023654Z` evidence-led symbol-research batch for
  every active row in `SYMBOLS.md` and merge the verified result into local
  `dev`.

### Scope And Acceptance Criteria

- [ ] Use one decision cutoff (`2026-08-01T02:36:54Z`), USD reporting, an
  impersonal-research capacity, and a news window beginning no later than
  `2026-07-25T02:36:54Z` while carrying unresolved material events from the
  prior 60 days.
- [ ] Cover all 38 active symbols, reconcile each exact instrument against the
  registry, and retain explicit stop conditions for unresolved aliases.
- [ ] Search current public sources for every symbol, preserving source,
  timing, claim class, contradictions, and gaps; never treat web results as an
  authorized quote/news packet.
- [ ] Publish four-horizon probabilities only when a validated start value and
  defensible calibration exist; otherwise preserve `insufficient evidence`.
- [ ] Create one immutable `latest-v2` history snapshot and decision row per
  active symbol exclusively through `symbol_research_history.py`.
- [ ] Replace `REPORT.md`, update `SYMBOLS.md` analysis records, and reconcile
  summary, probability, risk, link, manifest, and active-universe counts.
- [ ] Pass focused symbol-history/template checks, the stage gate, the final
  work-branch gate, and the merged-state gate.

### Work Branch And Commit Boundaries

- [ ] Work only on `feature/symbol-research-2026-08-01` until verification
  passes.
- [ ] Commit the complete immutable research batch after focused verification.
- [ ] Reset this task plan, commit the clean final state if needed, and merge
  the tested branch non-fast-forward into local `dev`.

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

1. Reconcile universe, registry, prior batch, provider availability, source
   hierarchy, cutoff, and stop conditions.
2. Run independent read-only public-evidence lanes for disjoint symbol groups;
   centrally inspect the seven unresolved commodity/index aliases and the
   cross-market evidence boundary.
3. Normalize the evidence record, generate all 38 snapshots/decision rows,
   replace `REPORT.md`, and update `SYMBOLS.md` without fabricating prices,
   catalysts, probabilities, valuation, or leverage precision.
4. Verify append-only histories, templates, coverage, links, counts, and
   probability treatment; run stage and final repository gates.
5. Review the final diff, reset `TODO.md`, commit, prepare and test the local
   `dev` merge, create the merge commit, and rerun the merged-state gate.

### Verification Commands

- `python3 .codex/skills/research-symbol-watchlist/scripts/sync_symbol_research.py --check`
- `python3 .codex/skills/research-symbol-watchlist/scripts/migrate_symbol_templates.py --check`
- `python3 .codex/skills/research-symbol-watchlist/scripts/symbol_research_history.py verify --repo-root .`
- `scripts/agent-quality-gate.sh --stage`
- `git diff --check`
- `scripts/agent-quality-gate.sh`

## Completion Rule

When all task items are done, replace temporary task details with a short
completed summary or reset this file to the empty template. Do not leave stale
task checklists behind after the final commit.
