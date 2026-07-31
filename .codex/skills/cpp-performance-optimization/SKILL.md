---
name: cpp-performance-optimization
description: Profile, trace, optimize, and validate C++ runtime performance while preserving observable behavior. Use when Codex must follow real execution paths, analyze CPU hotspots, allocations, cache behavior, branches, contention, I/O waits, or TBB scaling; form and implement measured optimization hypotheses; and prove functional equivalence plus benchmark improvement.
---

# C++ Performance Optimization

## Purpose

Use measured execution evidence to improve end-to-end performance without
changing required behavior. Treat correctness and performance as separate
gates: pass the correctness gate first, then accept an optimization only when
the improvement is larger than measurement noise.

## Required Handoffs

- Read `skills/cpp-performance-benchmark/SKILL.md` to define the baseline,
  measurement protocol, comparison, and pass/fail threshold.
- Read `skills/cpp-linux-toolchain-quality/SKILL.md` before choosing or running
  Linux profiling and analysis tools.
- Read `skills/cpp-build-fix-loop/SKILL.md` after editing C++ or CMake and use
  its build-test repair loop until clean.
- Read `skills/cpp-architecture-review/SKILL.md` before changing data ownership,
  layout, public APIs, ABI, library boundaries, or dependency direction.
- Read `skills/cpp-sanitizer-validation/SKILL.md` for allocation, lifetime,
  pointer, container, parsing, or synchronization changes.
- Read `skills/tbb-concurrency/SKILL.md` for parallelism, contention, task
  scheduling, concurrent containers, arenas, or scaling changes.
- Use `skills/technical-research/SKILL.md` before selecting an unfamiliar
  algorithm, compiler technique, or hardware-specific approach that depends on
  current external evidence.

## 1. Lock The Correctness Contract

Before changing production code:

1. Identify the user-visible operation and representative workload.
2. Define observable behavior: outputs, error handling, side effects, ordering,
   determinism, precision, API/ABI, ownership, and thread-safety requirements.
3. Run the focused tests that exercise the path and record their baseline
   result.
4. Add a characterization or regression test first when no existing test can
   detect a behavioral change in the proposed optimization area.
5. Compare exact outputs when exactness is part of the contract. For floating
   point or approximate algorithms, use the repository's existing justified
   tolerances and record the comparison method.

Do not weaken assertions, golden outputs, tolerances, invariants, or coverage to
make an optimization pass. If the baseline already fails, understand and
separate that failure before editing the hot path; do not claim preservation
against an unverified baseline.

## 2. Establish The Performance Baseline

1. Select realistic inputs, sizes, distributions, thread counts, and operating
   modes. Include small inputs when startup or parallel overhead matters.
2. Use an optimized build with usable symbols. Keep production-equivalent
   optimization flags; record local profiling-only flags such as debug symbols
   or frame-pointer changes.
3. Separate setup from steady-state work unless setup belongs to the real
   operation.
4. Warm up when needed, repeat measurements, and record median plus variance.
5. Record the command, build type, compiler, important flags, CPU, thread count,
   input, and relevant environment controls.

Do not use Debug or sanitizer timings as performance evidence. Keep raw profiler
artifacts in an ignored build or temporary directory unless the repository has a
documented location for them.

## 3. Trace The Real Execution Path

Build both a static and dynamic view of the selected operation.

1. Start at the executable, API, event, test, or benchmark entry point.
2. Follow callers and callees through the affected libraries. Map major loops,
   allocations, copies, conversions, synchronization, TBB tasks, and I/O.
3. Profile the same representative workload used for the baseline. Use
   `perf stat` for high-level counters. Use `perf record --call-graph=dwarf`,
   `perf report`, and `perf annotate` when available and appropriate.
4. Verify that symbols and stacks resolve well enough to support conclusions.
   Fix profiling fidelity before interpreting broken call graphs.
5. Distinguish CPU computation from allocation overhead, cache or memory stalls,
   branch behavior, lock contention, scheduler overhead, I/O waits, and one-time
   initialization.
6. Rank candidate bottlenecks by inclusive cost, self cost, invocation count,
   and end-to-end contribution. Inspect hot functions together with their
   callers, callees, inputs, and ownership.
7. Estimate the maximum end-to-end gain from removing each cost. Do not optimize
   a locally expensive function whose total contribution cannot meet the goal.

Treat profiles as evidence about the recorded workload, not proof about every
input. Add representative workloads when different execution modes take
materially different paths.

## 4. Form One Optimization Hypothesis

For each candidate, record:

- the trace or measurement showing the cost;
- the mechanism causing it;
- the proposed change and expected end-to-end benefit;
- the correctness, architecture, memory, and concurrency risks;
- the focused tests, sanitizer checks, and benchmark that will decide whether
  to keep it.

Choose the highest-confidence material bottleneck. Prefer, in order, eliminating
work, improving algorithmic complexity, improving data locality and layout,
removing copies or allocations, reducing contention, helping compiler
optimization, and finally low-level micro-optimization. Use the standard library
and existing local helpers first. Use TBB for work distribution.

## 5. Implement A Focused Change

- Change one hypothesis at a time so its effect remains attributable.
- Preserve public API, ABI, error behavior, ownership, ordering, and threading
  contracts unless the user explicitly approved a change.
- Keep layer direction and library ownership intact. Do not move application
  concerns into lower layers to shorten a hot path.
- Avoid unrelated cleanup, broad rewrites, speculative caches, custom allocators,
  custom lock-free structures, and new dependencies without measured need.
- Do not modify third-party submodules. Optimize repository-owned callers,
  adapters, data flow, or integration instead.
- Keep a serial path or threshold when TBB overhead dominates small inputs.

## 6. Prove Correctness Before Speed

1. Configure and build with the repository warning policy.
2. Run the focused regression or characterization tests.
3. Compare observable outputs and invariants against the baseline.
4. Run broader tests when the path is shared or the change affects a public
   library, API, data model, or common algorithm.
5. Run ASAN/UBSAN for relevant memory, lifetime, allocation, indexing, or layout
   changes. Run TSAN separately for TBB or synchronization changes when
   practical.

Stop performance evaluation when correctness fails. Revise or remove only the
optimization edits made for the current hypothesis; never preserve a known
behavioral regression for a possible speedup.

## 7. Prove The Performance Change

1. Rebuild the optimized benchmark or workload from the final source.
2. Repeat the baseline protocol under comparable conditions.
3. Compare median, variance, and the metric tied to the claim. Include tail
   latency, allocation rate, memory footprint, cache behavior, contention, or
   scaling when relevant.
4. Re-profile when needed to confirm that the predicted cost moved and that work
   did not merely shift to another part of the path.
5. Check small-input overhead and serial-versus-parallel behavior for TBB work.

Keep the change only when the improvement exceeds noise and all correctness
gates pass. If the result is neutral, noisy, or slower, investigate the
measurement once, then revise or remove the optimization rather than claiming a
win.

## Failure And Stop Conditions

- If no representative workload exists, derive one from tests or real usage and
  add a benchmark seam before optimizing. Ask the user only when repository
  evidence cannot identify a safe representative case.
- If profiling tools are unavailable, use the closest available evidence and
  report the limitation. Do not infer precise hotspots from source inspection
  alone.
- If results are noisy, stabilize the workload and environment before editing
  further.
- If the bottleneck is in a submodule, verify repository-side API use and data
  flow before attributing the cost upstream.
- If multiple focused hypotheses fail, return to the execution-path model and
  reconsider the design instead of stacking speculative changes.

## Reporting And Completion

Report:

- the workload and correctness contract;
- the traced path and ranked hotspot evidence;
- the selected hypothesis and files changed;
- before/after measurements with variance and environment details;
- build, test, sanitizer, and benchmark commands actually run;
- rejected hypotheses, skipped checks, and remaining risk.

Store a proven reusable benchmark baseline or resolved constraint in `MEMORY.md`
when future agents should rely on it. Finish the repository's full workflow,
quality gate, TODO cleanup, diff review, and commit discipline before declaring
the optimization complete.
