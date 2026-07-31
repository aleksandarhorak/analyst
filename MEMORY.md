# Project Memory

Durable project facts only. Keep this file short, factual, and current. Do not
store chat notes, temporary failures, stale TODOs, guesses, or long copied
documentation here.

## Active Facts

- This repository is a reusable Codex C++23/TBB agent template.
- `AGENTS.md` is the always-loaded project guidance and skill router.
- Detailed reusable workflows live under `skills/<skill-name>/SKILL.md`.
- `scripts/install-agent-setup.sh` is Codex-only and installs every repo-local
  skill into the target project's `.codex/skills` directory.
- Its `--update` profile replaces template-managed setup in an existing Git
  project while preserving branch setup, skipping Linux tool checks, and
  installing the quality-gate hook; combine it with `--dry-run` to preview.
- The installer force-adds `.codex/skills` to a new project's initial commit so
  global Git ignore patterns cannot silently omit matching skill names.

## Build Notes

- Reuse stable `build_debug` and `build_release` directories; use additional
  stable build trees only for incompatible toolchain, sanitizer, ABI, or
  compile-affecting variants.
- Root CMake projects default top-level installation to the ignored
  `<project-root>/install` directory while preserving explicit user overrides.
- Shared build and environment configurations live in committed
  `CMakePresets.json`; project workflows do not create or rely on
  `CMakeUserPresets.json`.
- Keep generated build and install artifacts out of Git.
- Bootstrap checks Linux C++ tool availability by default; package installation
  is explicit with `--install-linux-tools`.
- `scripts/agent-quality-gate.sh` is the shared local hook and CI gate for
  branch, whitespace, TODO, generated artifact, and dependency-hygiene checks.

## Dependency Notes

- Important C++ dependencies should be vendored as pinned GitHub submodules
  under `external/<name>`.
- Do not ask users to install missing central dependencies; vendor them or pick
  another solution.
- Resolve direct and transitive dependency closure before CMake integration, and
  build/install dependencies only through the root CMake project.
- Project targets should drive external builds: link precise dependency targets,
  prefer `EXCLUDE_FROM_ALL` where suitable, and install only intentionally used
  artifacts from root install rules.

## Architecture Decisions

- Keep `AGENTS.md` compact and move detailed repeatable workflows into skills.
- Keep project memory clean; add only facts that future agents should rely on.
- Full-workflow implementation tasks should plan in `TODO.md`, update it during
  execution, and keep all verified stage commits for one cohesive deliverable on
  the same `fix/*` or `feature/*` branch.
- Every file-changing task uses a work branch; direct task edits and commits on
  `dev` are prohibited. Passing work is tested as a prepared merge, merged
  automatically into `dev`, and verified again without waiting for approval.
- Long plans merge each independently deliverable phase, then continue from the
  updated `dev` on a new work branch. Dependent stages remain together until
  their cohesive fix or feature is complete.
- Before the final work-branch gate and automatic merge, confirm `TODO.md` is
  reset to the empty template or contains only a completed summary.
- Stage commits use the shared quality gate in `--stage` mode. Final
  work-branch and merged `dev` states use the full gate. The optional pre-commit
  hook blocks direct `dev` task commits while allowing tested merge commits; CI
  runs the gate in `--ci` mode.
