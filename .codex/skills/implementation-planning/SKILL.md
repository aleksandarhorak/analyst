---
name: implementation-planning
description: Convert completed technical research, architecture decisions, dependency choices, or multi-stage feature requests into an executable implementation plan. Use after research is complete, when a feature, refactor, dependency, CMake change, performance task, or architecture change needs a TODO.md plan, acceptance criteria, staged execution, verification commands, and commit strategy before editing code.
---

# Implementation Planning

## Purpose

Use this skill after research or design input exists and before implementation
starts. The output is a concrete plan that can be executed, verified, and
committed without losing the reasoning behind the choice.

This skill does not replace research. If the chosen approach depends on current
external evidence, first use `skills/technical-research/SKILL.md`.

## Inputs

Read the relevant inputs before planning:

- User request and acceptance criteria.
- `research/<topic-slug>/decision.md` when research was performed.
- Existing `TODO.md` and `MEMORY.md` when project history can affect the plan.
- Relevant repository files, build files, tests, docs, and skills.
- Git status and current branch.

If research is missing, stale, or contradictory for a research-dependent task,
pause planning and return to `skills/technical-research/SKILL.md`.

## Planning Procedure

1. Restate the goal, constraints, and accepted decision.
2. Identify the affected files, targets, libraries, tests, and documentation.
3. Split work into focused stages with observable completion criteria.
4. Define verification for each stage: configure, build, tests, analysis,
   sanitizer, benchmark, or manual inspection as appropriate.
5. Define rollback or fallback points for risky changes.
6. Decide which existing skills must be used during execution.
7. Classify the work as `fix/<slug>` or `feature/<slug>`, and define verified
   stage-commit boundaries on that one branch.
8. Update `TODO.md` for true multi-stage work.
9. Keep the plan short enough to execute; move only durable facts to
   `MEMORY.md` after they are proven.

## TODO.md Plan Shape

For full-workflow work, update `TODO.md` with:

- Current task title.
- Scope and acceptance criteria.
- Stage checklist.
- Work branch and stage-commit boundaries.
- Verification checklist.
- Automatic merge and merged-state verification items.

Keep checklist items tied to observable actions. Avoid vague items such as
"improve code" or "clean things up".

For micro-tasks, do not create a TODO plan. Use an inline checklist or direct
execution.

## Stage Design

Prefer stages in this order:

1. Context and constraints.
2. Design or dependency integration decision.
3. Small implementation slice.
4. Focused build or test.
5. Next implementation slice.
6. Broader build, test, sanitizer, or benchmark check.
7. Documentation and durable memory update.
8. Final diff, quality gate, and commit.

Commit every defined, completed stage on the same work branch after its focused
verification passes. Use one commit for a small single-stage task. Do not create
a branch per stage.

## Verification Planning

Map verification to risk:

- Docs or policy-only changes: inspect diff and run lightweight repository
  checks.
- Build-system or dependency changes: configure, build at least one affected
  target, and run dependency hygiene checks.
- C++ behavior changes: build and run focused tests.
- Public API or shared library changes: run focused tests and broader `ctest`
  when available.
- Concurrency changes: include deterministic tests and TSAN when practical.
- Hot-path changes: include benchmark baselines and comparisons.
- External-input, parsing, allocation, lifetime, or pointer changes: include
  sanitizer or memory validation when practical.

## Execution Handoff

After planning, execute stages using the relevant skills:

- `skills/cpp-build-fix-loop/SKILL.md` for C++/CMake/dependency edit loops.
- `skills/cpp-dependency-submodules/SKILL.md` for vendored dependency work.
- `skills/cpp-architecture-review/SKILL.md` for architecture and API shape.
- `skills/cpp-linux-toolchain-quality/SKILL.md` for formatting and static
  analysis.
- `skills/cpp-sanitizer-validation/SKILL.md` for sanitizer validation.
- `skills/tbb-concurrency/SKILL.md` for TBB and threading work.
- `skills/cpp-performance-optimization/SKILL.md` for tracing execution paths and
  implementing measured, behavior-preserving speedups.
- `skills/cpp-performance-benchmark/SKILL.md` for performance-sensitive work.
- `skills/git-tested-delivery/SKILL.md` for work-branch creation, stage commits,
  final verification, automatic merge into `dev`, and long-plan continuation.

## Completion

Before marking the plan done:

- Confirm all checklist items are completed or explicitly deferred.
- Confirm required verification ran and failures are resolved or documented.
- Reset `TODO.md` to the empty template or replace task details with a short
  completed summary.
- Run the repository quality gate when available.
- Finish commits on the matching `fix/*` or `feature/*` branch.
- Merge passing work automatically into `dev`, rerun the merged-state quality
  gate, and continue the next independent phase without waiting for approval.
