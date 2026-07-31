# TODO

This template starts with no active project task.

Use this file only for active full-workflow implementation work. Do not use it
for answer-only requests, reviews, scoring, tiny documentation edits, or
temporary notes.

## Current Task

- [ ] Transform the reusable C++ agent template into an evidence-led financial
      analyst and broker-support agent while preserving tested development and
      Git delivery workflows.

### Scope And Acceptance Criteria

- [x] Record at least 10 fully reviewed primary papers in each required lane:
      trading, company analysis, economic foundations, and financial-news
      research, with URLs, methods, findings, limitations, and skill
      implications.
- [x] Replace C++/CMake/TBB operating policy and skills with a compact
      finance-first policy and bounded, nonduplicative finance skills.
- [x] Preserve and adapt technical research, implementation planning, tested Git
      delivery, CI, branch checks, and repository quality gates so the agent can
      continue improving safely.
- [x] Encode professional controls for source provenance, point-in-time data,
      uncertainty, valuation ranges, forecast calibration, transaction costs,
      portfolio risk, client suitability, conflicts, and jurisdiction-sensitive
      compliance.
- [ ] Validate every new skill, add automated repository integrity checks, pass
      the final quality gate, commit verified stages, and merge into `dev`.

### Work Branch And Commit Boundaries

- Branch: `feature/financial-analyst-agent`.
- Stage 1 commit: research dossier, paper manifest, and architecture decision.
- Stage 2 commit: finance-first `AGENTS.md`, skill migration, and retained-skill
  adaptation.
- Stage 3 commit: financial-agent integrity checks, memory/update cleanup, and
  final verification.

### Staged Checklist

- [x] Stage 1: write `research/financial-analyst-agent/README.md`,
      `sources.md`, `papers/manifest.md`, and `decision.md` from the completed
      research; verify category counts and source links.
- [x] Stage 1: run the stage quality gate, inspect the staged diff, and commit
      the evidence dossier.
- [x] Stage 2: remove nine C++/CMake/TBB skills and their UI metadata.
- [x] Stage 2: replace root agent policy with finance-first mission, research,
      analysis, brokerage, risk, safety, workflow, and Git standards.
- [x] Stage 2: create and validate the ten selected finance skills and adapt the
      retained technical-research and implementation-planning skills.
- [x] Stage 2: run all skill validators and the stage quality gate, inspect the
      staged diff, and commit the capability migration.
- [x] Stage 3: replace dependency-specific checks and ignore rules with
      financial-agent integrity and generic project-development checks.
- [x] Stage 3: update durable project memory, verify paper/skill inventory,
      validate shell scripts, run regression checks, and complete a security and
      compliance review.
- [ ] Reset `TODO.md`, run `git diff --check` and the full quality gate, commit
      the final state, prepare and test a non-fast-forward merge into `dev`, and
      verify the clean merged state.

### Verification Plan

- `python3 .../quick_validate.py .codex/skills/<skill>` for every new or changed
  skill.
- `bash -n scripts/*.sh scripts/git-hooks/pre-commit`.
- `scripts/test-agent-branch-policy.sh`.
- `scripts/check-financial-agent.sh` after it is introduced.
- `scripts/agent-quality-gate.sh --stage` before stage commits.
- `git diff --check` and `scripts/agent-quality-gate.sh` before the final commit,
  prepared merge, and merged-state handoff.

## Full Workflow Template

When a full-workflow task starts, replace `None` with:

- [ ] Define scope and acceptance criteria.
- [ ] Create or resume the matching `fix/*` or `feature/*` branch.
- [ ] Inspect relevant files and existing patterns.
- [ ] Plan implementation stages.
- [ ] Implement and commit each completed, verified stage on the work branch.
- [ ] Build affected targets.
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
