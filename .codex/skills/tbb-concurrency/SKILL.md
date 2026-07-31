---
name: tbb-concurrency
description: Design, implement, test, and debug Intel TBB concurrency work. Use for task arenas, global control, parallel algorithms, pipelines, task groups, concurrent containers, deterministic parallel tests, TSAN checks, contention analysis, or replacing ad hoc thread distribution with TBB.
---

# TBB Concurrency

## Purpose

Use this skill for C++ concurrency work where Intel TBB is the required
thread-pool and task scheduling framework.

## Design

1. Identify the concurrency shape.
   - Independent ranges: use TBB parallel loops.
   - Reductions or scans: use TBB reduction/scan primitives.
   - Irregular work graphs: use task groups or arenas.
   - Streaming stages: use TBB pipelines.
   - Shared producer/consumer state: prefer TBB concurrent containers.

2. Define ownership and lifetime.
   - Prefer immutable shared data, value transfer, and message passing.
   - Make cancellation, shutdown, and exception/error propagation explicit.
   - Use `std::stop_token`, `tbb::task_group_context`, atomics, or a
     repository-local cancellation channel consistently; do not mix ad hoc flags
     with implicit task lifetime.
   - Surface worker errors through `std::expected`, stored exceptions, or a
     documented error sink that the owner joins and checks.
   - Avoid callbacks from workers into UI, scripting, plugin, or FFI layers
     unless the receiving layer's thread contract is clear.

3. Control parallelism.
   - Use `tbb::global_control` or arenas to avoid oversubscription.
   - Use arena isolation for latency-sensitive sections.
   - Do not mix independent thread pools without documenting interaction.

## Implementation

- Do not use `std::thread` for work distribution.
- Keep blocking waits out of TBB worker tasks unless starvation is impossible or
  explicitly handled.
- Prefer TBB concurrent containers before mutex-heavy shared-state designs.
- If a mutex is necessary, keep the critical section small and use RAII locking.
- Avoid custom lock-free data structures unless approved dependencies cannot
  meet the need.

## Testing

- Make tests deterministic with fixed arena sizes and stable inputs.
- Use `tbb::task_arena` or `tbb::global_control` to cap parallelism in tests.
- Prefer barriers, latches, explicit queues, and deterministic fixtures over
  sleeps or timing assumptions.
- Test ordering independence explicitly.
- Exercise cancellation before start, during work, and during shutdown.
- Exercise worker error propagation and confirm the owning thread observes it.
- Include small and realistic data sizes.
- Run TSAN or an equivalent race-focused check when the project supports it.
- Treat data races, lifetime bugs, and shutdown hangs as correctness failures.

## Performance

- Benchmark serial and parallel versions at realistic sizes.
- Measure overhead, scaling, contention, cache behavior, and tail latency when
  relevant.
- Keep the serial path or thresholding strategy when parallel overhead dominates
  small inputs.
- Do not claim a concurrency improvement without measurements.

## Failure Loop

For deadlocks, races, flakes, or poor scaling: reproduce with fixed settings,
reduce to the smallest failing path, inspect ownership and synchronization,
patch the smallest design flaw, rerun tests/sanitizers/benchmarks, and repeat.
