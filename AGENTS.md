# Agent Guidelines for This Repository

Operate as a senior C++23 engineer: small diffs, strong architecture, measured
performance, reusable libraries, no duplication, and high autonomy. Prefer the
standard library first, use Intel TBB for thread-pool and task scheduling, and
keep the repository buildable and reviewable at every step.

This file is intentionally compact for local models. Follow the spirit and the
hard rules below; scale ceremony to task risk.

Detailed workflows live in repo-local skills under `skills/<name>/SKILL.md`;
after installation they live under project-local skill directories such as
`.codex/skills/<name>/SKILL.md`. References to `skills/<name>/SKILL.md` below
mean the installed Codex equivalent. When a task matches a skill, read that
skill before planning or editing. Install these repo skills for Codex discovery
with `scripts/install-agent-setup.sh`.

Decision order when rules compete:

- Correctness first, then safety, then maintainability, then performance, then
  convenience.
- Existing repository patterns beat generic preference unless they are unsafe or
  clearly obsolete.
- A small, boring, verified change beats a clever rewrite.
- Do not invent infrastructure when the standard library, CMake, TBB, or a
  local helper already solves the problem.
- Prefer evidence over assertion. If performance, safety, or dependency quality
  matters, verify it.

## 0. Skill Routing

The available repo skills are the directories under `skills/` in this template
and under `.codex/skills/` after installation. The current skill inventory is
listed below. If a task depends on skills and the list looks stale, inspect the
skill directories first and update this inventory as part of the change.

- `skills/cpp-build-fix-loop/SKILL.md`: use after C++/CMake/dependency edits,
  or when configure, build, link, test, sanitizer, or warning failures need a
  repair loop.
- `skills/cpp-cmake-project-setup/SKILL.md`: use when bootstrapping or repairing
  root CMake setup, shared presets, install rules, exported package targets, or
  downstream install verification.
- `skills/git-tested-delivery/SKILL.md`: use for every file-changing task to
  choose or resume a work branch, commit verified stages, merge passing work
  automatically into `dev`, and continue long plans.
- `skills/cpp-linux-toolchain-quality/SKILL.md`: use when choosing or running
  Linux C++ quality tools such as `clang-format`, `clang-tidy`, `cppcheck`,
  `include-what-you-use`, `bear`, `gdb`, `valgrind`, `perf`, or `gcov`.
- `skills/cpp-sanitizer-validation/SKILL.md`: use for ASAN, UBSAN, TSAN, LSAN,
  or MSAN validation of memory, undefined behavior, leaks, data races,
  lifetimes, parsing, allocation, pointer, container, or shutdown changes.
- `skills/cpp-dependency-submodules/SKILL.md`: use when adding or changing
  third-party C++ dependencies, GitHub submodules, `external/` contents, or
  dependency CMake setup.
- `skills/tbb-concurrency/SKILL.md`: use for TBB task arenas, global control,
  parallel algorithms, pipelines, task groups, concurrent containers,
  deterministic parallel tests, TSAN, or contention work.
- `skills/cpp-performance-benchmark/SKILL.md`: use for hot paths, benchmark
  targets, baseline comparisons, allocation/layout changes, SIMD decisions, or
  performance claims.
- `skills/cpp-performance-optimization/SKILL.md`: use to trace real execution
  paths, rank measured bottlenecks, implement focused speedups, and prove
  observable behavior is preserved.
- `skills/cpp-architecture-review/SKILL.md`: use for library boundaries,
  layering, public APIs, ABI risk, plugin/FFI boundaries, refactors, and
  duplication audits.
- `skills/technical-research/SKILL.md`: use when a task needs online research,
  latest technology checks, papers, PDFs, upstream documentation, public
  benchmarks, or evidence-based technology selection before planning.
- `skills/implementation-planning/SKILL.md`: use after research or design input
  exists to turn the chosen approach into a staged `TODO.md` plan with
  acceptance criteria, verification, and commit readiness.

## 1. C++23 Baseline

- C++23 is the minimum standard for all production C++ targets.
- Prefer `std::` facilities over custom utilities. Do not write containers,
  algorithms, option/result types, formatting helpers, or ownership wrappers
  when the standard library already has the right tool.
- Use `std::span` and `std::string_view` for non-owning parameters, `std::optional`
  for optional values, `std::expected` for fallible operations, `std::format` or
  `std::print` for formatting, ranges where they improve clarity, concepts for
  real constraints, and `std::mdspan` where multidimensional views are useful.
- No raw `new` or `delete` in application/library code. Use RAII, value types,
  smart pointers, `std::pmr`, or proven allocator strategies.
- Keep abstractions zero-cost in hot paths. If an indirection is claimed to be
  optimized away, verify it with optimized builds and benchmarks when it matters.
- Public APIs should be narrow, explicit, and documented with preconditions,
  postconditions, thread-safety guarantees, and complexity where relevant.
- Comments explain why, not what. Avoid filler comments and obvious narration.
- Naming: types use `PascalCase`; functions and variables use `snake_case`;
  constants and macros use `UPPER_SNAKE_CASE`.
- Keep source files and compilation units focused. Split files near 1000 lines
  unless a local convention clearly supports a larger unit.
- Avoid macros for constants, feature switches, and small utilities when
  `constexpr`, templates, concepts, or normal functions are sufficient.
- Prefer value semantics and explicit ownership. Borrowed references should not
  outlive their source; async callbacks must make lifetime ownership obvious.
- Keep exception policy consistent with the surrounding code. If exceptions are
  disabled or avoided locally, use `std::expected` and structured error types.
- Do not add global mutable state unless it is part of a deliberate process-wide
  service such as a scheduler, logger, or configuration registry.

## 2. Architecture And Libraries

Design in dependency-directed layers. Lower layers never depend on upper layers,
and circular dependencies are not allowed.

- Foundation/TBB layer: thread-pool integration, synchronization primitives,
  cache-line alignment, allocators, and low-level utilities. It may depend on
  the C++ standard library, atomics, OS primitives where justified, and TBB.
- Core layer: domain models, value types, data layouts, and algorithms. It may
  depend on Foundation but should avoid external dependencies unless the project
  explicitly requires one.
- Abstraction layer: interfaces, traits, policy types, and strategy boundaries
  that decouple core algorithms from concrete integrations.
- Application layer: CLI, GUI, services, bindings, orchestration, and other
  product-level workflows.

Library rules:

- One library owns one bounded capability.
- Header-only code is acceptable for small, template-heavy, non-ODR-sensitive
  units. Otherwise compile into a static, shared, or object library based on
  the target's usage and ABI needs.
- Prefer shared libraries for public runtime components and plugin-facing APIs.
  Static or object libraries are fine for internal code, benchmarks, tests, and
  tightly coupled implementation units when this reduces complexity.
- Internal details stay in implementation files, private headers, `.ipp` files,
  or `impl` namespaces.
- If two libraries need the same behavior, move it to the lowest common layer.
- Do not bypass layering to make a quick fix. Refactor the boundary instead.
- Treat public ABI as expensive. Once a type, function, or CMake target is
  public, keep it stable or document the migration.
- Keep data models independent from transport, storage, UI, and binding layers.
- Introduce interfaces only at real variability points. Do not wrap concrete
  code in abstract factories unless multiple implementations are expected.
- For plugin or FFI boundaries, keep C++ ownership, allocation, exceptions, and
  threading rules explicit at the boundary.

## 3. TBB And Concurrency

Intel TBB is the mandatory framework for work distribution and thread-pool
management. `std::thread` is reserved for top-level process/OS integration or
cases where a native thread is truly required.

- TBB is always provided as a real Git submodule from the official GitHub
  repository.
- TBB must not be discovered from system paths with `find_package(TBB)`.
- There is no option to disable TBB when project code depends on parallelism.
- Use the correct TBB primitive for the concurrency shape; prefer TBB concurrent
  containers before mutex-heavy shared state.
- Control parallelism with `tbb::global_control` or arenas where domains can
  interfere.
- Test parallel code deterministically and run TSAN or equivalent race checks
  when practical.
- For nontrivial concurrency work, read `skills/tbb-concurrency/SKILL.md`.

## 4. Performance Policy

- Benchmark before optimizing. Do not rely on intuition for hot-path changes.
- Use optimized builds for performance claims, normally with `-O3` and the
  project's release flags. Use `-march=native` only when the project accepts
  host-specific binaries or for local benchmarking.
- Prefer cache-friendly layouts. Use SoA, compact value types, and contiguous
  storage when access patterns justify them.
- Prefer `std::pmr` or TBB allocators before writing custom memory pools. A
  custom allocator or pool needs profiling evidence and a clear owner.
- Do not implement custom lock-free structures unless TBB, the standard library,
  or an approved dependency cannot meet the need.
- Use SIMD, branch hints, dispatch changes, and invasive layout changes only
  when measurements justify them.
- Do not trade away clarity for micro-optimizations in cold paths.
- For hot-path work or performance claims, read
  `skills/cpp-performance-benchmark/SKILL.md`.

## 5. CMake And Dependencies

CMake is the build source of truth. Make, Ninja, MSBuild, or IDE project files
are allowed only as CMake generators, not as separate build systems.

CMake rules:

- Enforce C++23 with target properties, not broad directory variables.
- Use target-based CMake: `target_link_libraries`, `target_include_directories`,
  `target_compile_features`, `target_compile_options`, and namespaced targets.
- Every project should provide root-owned install rules. When the user has not
  selected another prefix, default top-level installation to the ignored
  `<project-root>/install` directory by checking
  `CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT`; never unconditionally override
  a user or parent project's prefix.
- Use `GNUInstallDirs` with relative install destinations. Install intended
  targets, public headers, required resources, licenses, and public CMake
  package exports; keep installed packages relocatable.
- Keep dependency setup centralized in `cmake/dependencies.cmake` or a clearly
  named `cmake/third_party/` module.
- In this repository, "superbuild" means one root CMake project and target
  graph. Do not turn it into separately configured dependency builds, copied
  install prefixes, or path-based include/library discovery.
- Integrate third-party libraries from the root CMake graph with
  `add_subdirectory` or a local wrapper module. Configure upstream options
  before adding the subdirectory so only the needed library targets and required
  features are built.
- Configure, build, test, and install third-party libraries only through the
  root CMake project. Do not configure or install external libraries in separate
  build trees and then point the project at those outputs.
- Let project targets drive external builds. Do not build dependency `all`
  targets unless the consuming project target genuinely requires them; prefer
  documented upstream options, `EXCLUDE_FROM_ALL`, precise target linkage, and
  root-owned install rules for only the artifacts this repository uses.
- Disable upstream docs, tests, examples, samples, demos, command-line tools,
  standalone applications, benchmarks, installers, packages, language bindings,
  and Python components unless the project explicitly needs one of them.
- Expose third-party headers through target usage requirements. Libraries and
  applications in this repository must consume dependency headers through linked
  CMake targets, not through ad hoc global include paths.
- Commit `CMakePresets.json` as the shared source of Debug, Release, sanitizer,
  benchmark, and supported environment configurations for users, agents, and
  CI. Use preset inheritance instead of duplicating configuration.
- Do not create or rely on `CMakeUserPresets.json`; shared workflows belong in
  the project presets. Never commit secrets in preset environment values.
- Reuse stable build directories so CMake and the compiler can build
  incrementally. Use `build_debug` for normal development and focused tests,
  and `build_release` for final validation and benchmarks. Do not create a new
  task-named build directory for each edit or verification pass.
- Use additional stable directories such as `build_asan` or `build_tsan` only
  for configurations whose compiler, sanitizer, ABI, or generator settings are
  incompatible with the normal Debug or Release tree.
- Environment variants that cannot affect compiled output may share a stable
  build tree. Compiler-, ABI-, dependency-, generated-code-, or feature-
  affecting variants require their own inherited preset and stable build
  directory.
- Do not clean before ordinary rebuilds. When a clean build is needed to prove
  reproducibility or rule out stale artifacts, clean and rebuild the appropriate
  stable tree once during final verification; keep the normal incremental
  `build_debug` tree warm whenever practical.
- Enable strict warnings for production C++ targets: `-Wall`, `-Wextra`,
  `-Wpedantic`, `-Werror`, and relevant library warnings such as
  `-Wnon-virtual-dtor`, `-Wold-style-cast`, and `-Wcast-align=strict`.
- Public libraries should install headers when the repository has install rules
  and should export namespaced CMake package targets.
- Keep include paths private by default. Use public include directories only for
  headers that are part of the target's actual API.
- Keep compile definitions, include paths, install rules, and generated files
  target-scoped and reproducible.
- For root CMake, preset, install, export, or package-consumer setup, read
  `skills/cpp-cmake-project-setup/SKILL.md`.

Dependency policy:

- Prefer C++23 standard library solutions first.
- For required third-party C or C++ libraries, use pinned GitHub submodules
  under `external/<name>`. Do not rely on system-installed versions,
  package-manager development files, extracted packages, prebuilt archives, or
  copied install trees.
- Dependency work must not install packages or run system package managers. Do
  not use PackageKit/`pkcon`, `apt`, `dnf`, `yum`, `pacman`, `zypper`, Homebrew,
  Conan, vcpkg, or similar tools to satisfy required C or C++ libraries.
- System discovery is allowed only for explicitly documented platform or
  toolchain interfaces, such as OS APIs, compiler runtimes, POSIX threads, or
  project-approved SDKs. A normal C or C++ library dependency is not a platform
  exception.
- If a required library is not available from GitHub, choose a suitable
  GitHub-hosted alternative or ask the user before using a non-GitHub source.
- Before adding a GitHub submodule, read the upstream documentation for how the
  library is meant to be used and built. Use documented CMake options and
  targets first.
- Before editing CMake for a new dependency, identify the full direct and
  recursive transitive dependency closure: GitHub repositories, pinned commits
  or tags, licenses, CMake targets, upstream options, dependency order, and
  public or private linkage. Continue until every required C or C++ library in
  the chain is accounted for as a repository submodule or a documented
  platform/toolchain exception.
- Inspect upstream transitive dependencies before integration. If a required
  transitive dependency is not already provided by this repository, add it as a
  pinned GitHub submodule too.
- Do not use package managers, PackageKit/`pkcon`, `apt`, `dnf`, `yum`,
  `pacman`, `zypper`, RPMs, DEBs, APKs, release tarballs or zip files,
  `FetchContent`, `ExternalProject`, or generated download steps for required
  dependencies.
- If configure, build, or link fails because a required dependency is missing,
  route to `skills/cpp-dependency-submodules/SKILL.md` before changing CMake or
  installing anything. Do not use system packages, prebuilt archives, `/tmp`
  downloads, copied libraries, install-prefix workarounds, or ignored
  `external/` directories to satisfy the missing dependency.
- Do not skip a selected library because it has its own dependencies. Map the
  deeper dependency chain, vendor the required GitHub submodules, choose a
  smaller suitable alternative with evidence, or ask the user to approve a
  strategic tradeoff.
- Do not set selected project features, libraries, or dependency integrations to
  `OFF` merely to bypass missing transitive dependencies. If the repository or
  user selected a feature, backend, format, or runtime integration, its build
  dependencies are required until the user explicitly approves a scope
  reduction.
- Required dependencies must be reproducible from Git. Do not hide them in
  ignored generated directories such as `external/<name>/`; an `external/`
  dependency used by CMake should normally have a matching `.gitmodules` entry.
- Treat `.gitignore` entries for required `external/<name>/` dependencies as
  dependency hygiene failures until the dependency is converted to a pinned
  submodule or a narrow documented exception.
- External dependencies must be integrated into the same CMake target graph. Do
  not build them separately in `/tmp`, copy installed headers or libraries into
  the repository, or expose them with global `include_directories()`. Add them
  from centralized dependency CMake and make consumers use
  `target_link_libraries`.
- For required third-party C or C++ libraries, do not use `find_package` against
  system paths. Use `find_package` only for platform/toolchain exceptions or for
  package configs produced inside the same root build from vendored sources.
- A completed dependency build should be reproducible from one root configure,
  one root build, and, when install rules exist, one root install into an ignored
  `<project-root>/install` prefix unless the user explicitly overrides it.
- Do not modify files inside third-party submodules. Put all integration fixes,
  option settings, target aliases, warning suppression, include visibility, and
  adaptation code in this repository's own CMake modules, wrappers, or source
  files.
- Before adding a library, research upstream documentation, prefer permissive
  licenses and active maintenance, pin submodules, disable upstream non-library
  artifacts such as docs, examples, tests, tools, and Python bindings, preserve
  selected library features and runtime integrations, preserve license files,
  and document the rationale.
- Run `scripts/check-dependency-hygiene.sh` after dependency policy, CMake,
  `.gitmodules`, `.gitignore`, or `external/` changes. The full agent quality
  gate runs the same dependency hygiene check.
- For dependency work, read `skills/cpp-dependency-submodules/SKILL.md`.

## 6. Testing, Verification, And Security

Scale verification to risk.

- Tiny docs, scoring, comments, or policy edits: inspect the diff and run the
  lightest useful checks.
- Build-system, dependency, C++ behavior, threading, or multi-file changes:
  configure/build through CMake and run focused tests.
- Shared library, public API, architecture, and concurrency changes: run focused
  tests plus broader `ctest` when available.
- Allocation, pointer, parsing, serialization, or external-input changes: run
  sanitizer or memory-safety checks when the project supports them.
- Parallel code paths require TSAN or an equivalent race-focused validation path
  where practical.
- Performance-sensitive API, algorithm, allocator, layout, or TBB changes need
  benchmark coverage and baseline comparison.
- For ASAN, UBSAN, TSAN, LSAN, or MSAN validation, read
  `skills/cpp-sanitizer-validation/SKILL.md`.
- After C++/CMake/dependency edits, read
  `skills/cpp-build-fix-loop/SKILL.md` for the verification loop.
- When a change needs Linux C++ formatting, static analysis, include hygiene,
  debugging, profiling, or coverage tools, read
  `skills/cpp-linux-toolchain-quality/SKILL.md`.

Quality gates for code changes:

- Build succeeds with no warnings under the target warning policy.
- Existing focused tests pass.
- New behavior has tests unless the change is purely mechanical or unreachable
  from automated tests.
- Benchmarks show acceptable performance for hot-path changes.
- No duplicated implementation was introduced.
- Layering is preserved.
- Security review finds no obvious regressions.

Build failure loop:

- After any C++/CMake/dependency edit, build before declaring success.
- If the build fails, read the exact error, inspect the affected code and build
  files, plan the smallest correct fix, edit, rebuild, and repeat until clean.
- If repeated build failures reveal a deeper design issue, return to analysis
  and revise the plan instead of stacking guesses.
- Never report a code task as complete while build errors or required test
  failures remain.

Security review checklist:

- Validate external input before use.
- Avoid unchecked indexing; use spans, range checks, or provably safe loops.
- Preserve RAII for files, sockets, memory, locks, and handles.
- Check thread-safety for shared state and callbacks.
- Use vetted crypto libraries only; never create custom crypto.
- Treat UB, data races, lifetime bugs, and integer overflow as correctness and
  security issues.
- Tests should exercise observable behavior, not private implementation details,
  unless the private detail is a critical algorithm with no better public seam.
- Regression tests should fail before the fix and pass after it whenever the
  bug can be reproduced locally.
- Prefer deterministic fixtures over sleeps, timing assumptions, and live
  network dependencies.
- For CMake/dependency changes, verify both configuration and at least one
  target build that links the affected dependency.
- For public APIs, include compile-time coverage where concepts, templates, or
  target exports are part of the contract.

## 7. Workflow And Autonomy

Default posture: research, decide, implement, verify, and report. Do not stop
for clarifying questions unless the missing answer is impossible to discover and
a reasonable choice would be destructive, unsafe, or materially wrong.

Project state files:

- `MEMORY.md` and `TODO.md` are normal repository files, not automatic agent
  memory. Read or edit them directly when the rules below say they are relevant.
- All agents must follow the full workflow rule for full-workflow tasks: before
  editing code, CMake, dependencies, public documentation, or generated
  configuration, update `TODO.md` with the task plan, acceptance criteria,
  staged checklist, and verification plan.
- Keep `MEMORY.md` for durable facts future agents should rely on: architecture
  decisions, dependency setup, build quirks, benchmark baselines, and resolved
  constraints. Do not use it as a chat log or task diary.
- Use `TODO.md` only for active full-workflow implementation work. Write the
  plan there before the first code/build/dependency edit, update items as they
  progress, then replace completed task details with a short summary or reset it
  to the empty template.

Micro-task fast path:

- Use for answer-only work, reviews, scoring, small docs edits, formatting, and
  narrow policy updates.
- Inspect the relevant file or diff.
- Edit if the user asked for edits.
- Run the smallest useful verification.
- Report what changed and what was checked.
- Do not create `TODO.md`, planning documents, goals, or stage commits for this
  path unless the user explicitly asks.
- Read-only micro-tasks need no branch. A micro-task that edits repository files
  still uses one `fix/*` or `feature/*` branch, one focused commit, and the
  automatic tested merge workflow.

Full workflow:

- Use for C++ behavior changes, public APIs, architecture, CMake/dependency
  changes, threading/performance work, security-sensitive work, or multi-stage
  refactors.
- Read repository context first. Read root `MEMORY.md` only when existing
  project history can affect the task; create it only if the full workflow needs
  persistent project context and it is missing.
- Before editing code, CMake, dependencies, public documentation, or generated
  configuration, create or update `TODO.md` with a concise task plan, acceptance
  criteria, staged checklist, and verification plan.
- Research relevant open-source libraries before choosing a nontrivial external
  dependency. Pick the best solution without asking the user unless approval is
  needed for network access, licensing risk, destructive actions, or a strategic
  tradeoff the repository cannot answer.
- Execute in focused stages from `TODO.md`: understand, design, edit, build,
  test, benchmark when relevant, security-review, and final quality gate. Update
  `TODO.md` as each item starts or completes.
- Keep all stages of one cohesive task on the same `fix/*` or `feature/*`
  branch. Commit each completed, verified stage when a multi-stage plan defines
  it as a useful review or rollback point.
- Update `MEMORY.md` only for durable project facts: architecture decisions,
  dependency setup, build quirks, benchmark baselines, and resolved constraints.
- After all TODO items are complete and required verification passes, clean up
  `TODO.md` according to its completion rule, inspect the final diff and status,
  finish the work-branch commits, and merge the passing branch automatically
  into `dev`.
- The final diff/status review for a full-workflow task must explicitly confirm
  that `TODO.md` is reset to the empty template or contains only a completed
  summary before the final work-branch gate and merge.
- If a command fails, read the exact error, identify the source, make one focused
  fix, and rerun the relevant check. If the quick fix exposes a deeper issue,
  return to analysis instead of stacking guesses.
- If verification cannot be completed, report exactly what was not run and why.
- If the user asks a direct question, answer directly. Do not create process
  artifacts just to answer a question.
- If the user asks for a review, lead with findings ordered by severity and cite
  file/line references.
- If the user asks to research, browse or otherwise verify online, do it and cite
  the sources used.
- If a task needs current external evidence, papers, upstream documentation, or
  public benchmark comparison, read `skills/technical-research/SKILL.md` before
  choosing an approach, then read `skills/implementation-planning/SKILL.md` to
  turn the research decision into executable stages.
- If network access or filesystem permissions block required work, request the
  minimal approval needed and continue once granted.
- For architecture-heavy tasks, read
  `skills/cpp-architecture-review/SKILL.md` before choosing the design.

Subagents:

- Use subagents only when work splits into independent files, modules, audits,
  or verification tasks with no shared write targets.
- Do not parallelize edits to the same file.
- Merge results deterministically in one final pass.
- Avoid subagent overhead for fewer than three small independent tasks.
- Subagents can gather evidence, run independent checks, or prepare isolated
  edits. The main agent owns final integration and the final answer.

## 8. Git Discipline

- Before doing any task work, verify that the workspace is inside an initialized
  Git repository. If Git is not initialized, stop and tell the user that work
  cannot continue until the repository is initialized.
- Before every file-changing task, read
  `skills/git-tested-delivery/SKILL.md`.
- Read-only answers, reviews, investigations, and status checks do not require a
  work branch. Every task that edits repository files must use `fix/<slug>` for
  corrective work or `feature/<slug>` for all other changes.
- Start new work from a clean local `dev`, create the work branch before the
  first task edit, and never make task edits or direct task commits on `dev`.
  If already on the matching work branch, resume it instead of creating another.
- Inspect `git status --short --branch` before branching, staging, committing,
  merging, or publishing.
- Preserve unrelated user changes. Never revert work you did not make unless the
  user explicitly asks.
- Do not use destructive Git commands unless explicitly requested.
- If the user says `commit`, commit the current task changes on the current
  branch after status review and appropriate verification.
- If the user says `commit all changes`, stage the whole worktree after status
  review unless there is an obvious conflict or dangerous generated output.
- For a multi-stage task, commit every completed, verified stage on the same
  work branch. Use `scripts/agent-quality-gate.sh --stage` for stage commits
  while `TODO.md` remains active.
- Before the final work-branch commit or merge, finish the TODO plan, run
  required tests, reset `TODO.md`, stage the intended files, run
  `git diff --check`, review the staged diff, and run
  `scripts/agent-quality-gate.sh` without `--stage`.
- Do not auto-commit when the user explicitly says not to commit, required
  checks fail or cannot run, unrelated user changes are mixed into the worktree,
  the branch is not the matching `fix/*` or `feature/*` branch, Git identity or
  permissions block the commit, or the remaining diff no longer matches the
  task.
- Use one focused commit for a small single-stage task. Do not create a branch
  per stage or mix unrelated phases on one branch.
- When a work branch is complete and current with local `dev`, prepare a
  non-fast-forward merge on clean `dev` without committing it, run required
  tests and the final quality gate on the combined tree, then create the merge
  commit automatically. Do not wait for user approval.
- If the prepared merge conflicts or fails checks, abort it only after
  confirming pre-merge `dev` was clean, repair and verify on the same work
  branch, and retry. Keep incomplete or failing work off `dev`.
- After a successful merge, rerun the quality gate on clean `dev`. For a long
  plan, immediately start the next independently deliverable phase from the
  updated `dev`; keep dependent stages on the current branch until their
  cohesive feature is complete.
- New project bootstrap should initialize Git on `main`, create the first
  template commit when possible, create `dev` from `main`, switch to `dev`, and
  keep generated `build*` and `install*` directories ignored.
- Publish `dev` to `main` or `master` only after the user explicitly says
  `publish`.
- Do not initialize repositories, change remotes, or alter Git identity unless
  the user asks.
- Commit messages should be concise and describe the behavioral or structural
  change, not the tool that made it.
- Before committing, review `git diff --check` and the staged diff when practical.
- Never hide failed checks in a commit message or final response.
- If generated or unrelated files appear, classify them before staging. Leave
  unrelated user work untouched unless the user requested all changes.

## 9. Final Checklist

Before declaring a task done, confirm the relevant subset:

- Scope understood and existing patterns followed.
- C++23 and standard-library preference honored.
- TBB used for work distribution where concurrency is needed.
- CMake target structure and dependency policy preserved.
- Build and tests run according to risk.
- Benchmarks run for hot-path or parallel performance changes.
- Security and thread-safety reviewed.
- Git status is understood, and only intended files changed.
- Final response states what changed, what was verified, and any remaining risk.
