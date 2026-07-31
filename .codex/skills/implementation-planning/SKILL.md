---
name: implementation-planning
description: Convert completed research, architecture decisions, evaluation findings, or multi-stage agent-development requests into an executable repository plan. Use before substantial skill, policy, script, data-contract, evaluation, workflow, or documentation changes that need TODO.md stages, acceptance criteria, verification, and commit boundaries.
---

# Implementation Planning

## Purpose

Turn an accepted decision into a plan that can be executed, verified, reviewed,
and rolled back without losing its reasoning. This skill plans repository work;
it does not replace financial research or analysis.

## Inputs

Read the user request, acceptance criteria, relevant
`research/<topic-slug>/decision.md`, `TODO.md`, durable facts in `MEMORY.md`,
affected repository files and validators, Git status, and current branch.
Return to `technical-research` when a material external decision is missing,
stale, or contradictory.

## Procedure

1. Restate the goal, non-goals, constraints, and accepted decision.
2. Inventory affected policy, skills, references, scripts, tests, data
   contracts, documentation, and evaluation fixtures.
3. Identify safety invariants: evidence provenance, point-in-time integrity,
   numerical correctness, uncertainty, client protection, market integrity, and
   order-authority boundaries as applicable.
4. Split work into focused stages with observable completion criteria and
   rollback points.
5. Map each stage to validation: schema or skill validation, deterministic
   scripts, regression fixtures, manual adverse-case review, shell checks, or
   the repository quality gate.
6. Select the specialist finance and development skills needed for execution.
7. Use one `fix/<slug>` or `feature/<slug>` branch and define verified stage
   commits on that branch.
8. Update `TODO.md` for true multi-stage work. Keep durable proven facts for
   `MEMORY.md`, not the task diary.

## TODO.md Shape

Include current task, scope and acceptance criteria, work branch, stage-commit
boundaries, task checklist, verification commands, final diff review, TODO
reset, automatic tested merge into local `dev`, and merged-state validation.
Every checklist item must describe an observable action.

## Stage Design

Prefer this sequence:

1. Context, evidence, and constraints.
2. Architecture or policy decision.
3. Small implementation slice and focused validation.
4. Further independently reviewable slices.
5. Regression, safety, and adverse-case evaluation.
6. Documentation and durable memory.
7. Final diff, quality gate, commit, prepared merge, and merged-state gate.

Use one commit for a small single-stage task. For a multi-stage task, commit
each coherent verified stage; never create a branch per stage.

## Verification Planning

- Policy or docs: inspect links and diff, then run lightweight integrity checks.
- Skills or metadata: run the skill validator and representative trigger/output
  cases.
- Financial logic or templates: add exact calculation, temporal, uncertainty,
  and adverse compliance fixtures through `evaluate-financial-agent`.
- Scripts and workflow: run syntax, focused regressions, stage gate, and final
  gate.
- Data connectors: verify provenance, licensing, timestamps, revisions,
  identifiers, units, failure behavior, and secrets handling.
- Execution or personalized-client capabilities: test authority, abstention,
  conflict, suitability, manipulation, and non-public-information boundaries.

## Execution Handoff

Use the relevant financial-analysis skills for domain behavior,
`evaluate-financial-agent` for regression evidence, and `git-tested-delivery`
for branches, commits, final verification, and automatic merge into `dev`.

## Completion

Confirm all checklist items are complete or explicitly deferred, required
checks passed, `TODO.md` is reset or reduced to a completed summary, the final
quality gate passed, and passing work was merged into local `dev`.
