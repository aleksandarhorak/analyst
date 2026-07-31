---
name: git-tested-delivery
description: Deliver repository changes through mandatory fix or feature branches, verified stage commits, and automatic tested merges into dev. Use for any task that edits repository files, when starting or resuming a work branch, planning multi-stage commits, completing a fix or feature, repairing a merge conflict, or continuing a long plan across independently deliverable phases.
---

# Git Tested Delivery

## Purpose

Keep `dev` continuously integrated without doing task work directly on it.
Group every cohesive fix or feature on one branch, verify useful stage commits,
and merge automatically only after the combined result passes.

## Invariants

- Use `fix/<slug>` for bug fixes, regressions, and corrective maintenance.
- Use `feature/<slug>` for features, refactors, dependencies, build-system
  changes, policy changes, documentation changes, and other repository edits.
- Use a short lowercase kebab-case slug.
- Do not edit or make task commits directly on `dev`.
- Keep all stages of one cohesive deliverable on the same work branch.
- Merge passing work into local `dev` automatically. Do not wait for approval.
- Keep failing, incomplete, or conflicted work off `dev`.
- Do not publish `dev` to `main`, `master`, or a remote unless separately
  authorized.

Read-only answers, reviews, investigations, and status checks that do not alter
repository files do not need a work branch.

## Start Or Resume Work

1. Verify the workspace is an initialized Git repository with a `dev` branch.
2. Inspect `git status --short --branch`, the active `TODO.md`, and recent
   history before switching or editing.
3. If already on the matching `fix/*` or `feature/*` branch, continue there.
4. If another work branch contains unrelated unfinished work, do not mix tasks
   or discard it. Finish the active task or report the concrete conflict.
5. Start new work only from a clean `dev`:

```bash
git switch dev
git status --short --branch
git switch -c feature/<slug>
```

Use `fix/<slug>` instead when the task corrects faulty behavior. Do not create a
new branch for each implementation stage.

## Plan And Commit Stages

- Create or update `TODO.md` after entering the work branch when the task
  requires the full workflow.
- Treat a stage as a verified, reviewable, and useful rollback point.
- When a multi-stage task defines stages, commit every completed stage on the
  same work branch. Do not postpone all stage commits until the end or create a
  branch per stage.
- Before a stage commit:
  - Complete that stage's focused acceptance criteria.
  - Run the smallest relevant build and tests.
  - Inspect the intended staged diff and preserve unrelated user work.
  - Run `scripts/agent-quality-gate.sh --stage` when available. Stage mode may
    retain the active `TODO.md` plan.
- Do not commit a known broken intermediate state merely to mark progress.
- Use concise commit messages that describe the completed behavior or
  structure.

For a small single-stage change, make one verified work-branch commit.

## Finish The Work Branch

1. Complete every required task item and run all risk-appropriate tests.
2. Reset `TODO.md` to its empty template or a summary without active checklist
   items.
3. Stage only intended final files.
4. Run `git diff --check`, review the staged diff, and confirm the worktree has
   no unrelated or unstaged changes.
5. Run the final `scripts/agent-quality-gate.sh` without `--stage`.
6. Commit any remaining final changes on the same work branch.
7. If the final gate or a required test fails, repair the failure on this
   branch and repeat. Do not merge.

If the last stage commit already contains the final state, still run the final
gate from the clean work branch before merging.

## Reconcile With Dev

Before the final merge, ensure the work branch contains current local `dev`.
If `dev` advanced after the branch was created:

1. Merge `dev` into the work branch without rewriting published or shared
   history.
2. Resolve conflicts on the work branch.
3. Rerun affected tests and the final gate.
4. Commit the reconciliation on the same work branch.

Do not resolve the first integration conflict directly on `dev`.

## Merge Automatically After Tests

Use a tested, non-fast-forward merge so the branch's stage commits remain
grouped:

```bash
git switch dev
git status --short --branch
git merge --no-ff --no-commit feature/<slug>
```

Adapt the branch name for a fix. With the merge prepared but not committed:

1. Confirm there are no conflicts.
2. Run the required final tests on the combined tree.
3. Run `scripts/agent-quality-gate.sh`.
4. Only when all checks pass, create the merge commit:

```bash
git commit -m "Merge feature/<slug> into dev"
scripts/agent-quality-gate.sh
```

Do not ask for approval between passing checks and the local merge.

If the prepared merge conflicts or a check fails:

1. Run `git merge --abort` only after confirming `dev` was clean before the
   merge attempt.
2. Return to the same work branch.
3. Merge current `dev` into it, repair the issue, and rerun verification.
4. Retry the automatic merge.

After the merge succeeds, remain on clean `dev`.

## Continue Long Plans

- Keep dependent implementation stages for one cohesive feature on the same
  branch until that feature is complete.
- When a long plan contains independently deliverable phases, finish, test, and
  merge the current phase first.
- Start the next phase from the newly updated `dev` on a new appropriately named
  `feature/*` or `fix/*` branch.
- Repopulate `TODO.md` with the active phase and continue automatically. Do not
  pause merely because the previous phase merged.
- Do not split a still-incomplete cohesive feature only to produce an early
  merge.

## Stop Conditions

Do not auto-commit or auto-merge when:

- The user explicitly requested no commit or no merge.
- Required checks fail or cannot run.
- The worktree contains unrelated user changes that cannot be isolated safely.
- The intended diff no longer matches the task.
- A merge conflict requires a product or design choice that repository context
  cannot resolve.
- Git identity, permissions, or repository state prevents a safe commit.

Exhaust safe repairs on the work branch before reporting a blocker.

## Completion Report

State the work branch, stage commits when relevant, checks run, merge commit,
final `dev` status, and any skipped verification. Report publishing separately;
a successful local merge does not imply that `dev` was pushed or published.
