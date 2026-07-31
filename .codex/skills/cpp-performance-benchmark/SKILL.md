---
name: cpp-performance-benchmark
description: Benchmark and validate C++ performance-sensitive changes. Use for hot-path code, algorithms, data layout, allocation strategy, TBB scaling, cache behavior, SIMD decisions, benchmark targets, regression baselines, or claims that an optimization improves speed or memory behavior.
---

# C++ Performance Benchmark

## Purpose

Use this skill when correctness alone is not enough and the change affects a
hot path, allocation behavior, data layout, concurrency, or public performance
expectation.

## Benchmark Plan

1. Identify the performance claim.
   - Faster runtime, lower latency, better throughput, less allocation, smaller
     memory footprint, improved scaling, or reduced contention.
2. Identify the baseline.
   - Existing benchmark, previous implementation, serial path, or a committed
     baseline result.
3. Choose representative inputs.
   - Include realistic sizes and distributions.
   - Include small sizes when overhead or threshold behavior matters.
4. Define pass/fail criteria before tuning.
   - A small regression may be acceptable only when the tradeoff is documented
     and the user-facing benefit justifies it.

## Implementation

- Prefer existing benchmark targets and local benchmark conventions.
- Keep benchmarks in the unified CMake project.
- Do not benchmark debug builds for performance claims.
- Use optimized builds and the repository's release flags.
- Use host-specific flags only when the project accepts them or the result is
  explicitly local-only.
- Avoid measuring unrelated setup costs unless setup is part of the real hot
  path.

## Measurement

- Run enough iterations for stable signal.
- Include warmup where the benchmark framework or workload needs cache,
  allocator, JIT-like, or one-time initialization effects to settle.
- Repeat runs and compare medians plus variance; investigate noisy results
  before claiming a win.
- Use CPU pinning, fixed governor/performance mode, isolated machines, or
  reduced background load when local noise hides the signal.
- Record benchmark command lines, build type, compiler, important flags, CPU,
  thread count, and input set for any result used as evidence.
- Watch for allocation rate, cache misses, branch behavior, lock contention,
  thread scaling, and tail latency when relevant.
- Compare serial and parallel versions for TBB work.
- Keep raw commands and key results in the final response or durable notes when
  they become a project baseline.

## Pass/Fail Guidance

- Require a clear margin over run-to-run noise before calling an optimization
  faster.
- Treat regressions above the noise floor as failures unless the tradeoff was
  pre-approved or the user-facing benefit is documented.
- For parallel work, report scaling efficiency and small-input overhead, not
  only best-case throughput.

## Optimization Rules

- Prefer clearer code unless the measured gain matters.
- Prefer layout and algorithm improvements before intrinsics.
- Use SIMD only after auto-vectorization is insufficient and the fallback path is
  clear.
- Prefer `std::pmr` or TBB allocators before custom memory pools.
- Avoid virtual dispatch, heap churn, and shared mutable state in hot loops when
  measured cost justifies a change.

## Failure Loop

If the benchmark regresses or is noisy: verify the build mode, isolate the
changed code path, inspect inputs and measurement overhead, revise the smallest
design detail, rebuild, rerun, and repeat until the result is understood.
