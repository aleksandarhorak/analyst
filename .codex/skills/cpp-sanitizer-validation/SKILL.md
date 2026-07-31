---
name: cpp-sanitizer-validation
description: Configure, run, diagnose, and report C++ sanitizer validation with ASAN, UBSAN, TSAN, LSAN, and MSAN. Use for memory, undefined-behavior, lifetime, leak, data-race, concurrency, parsing, allocation, pointer, container, serialization, or shutdown changes, and whenever sanitizer failures need a focused repair loop.
---

# C++ Sanitizer Validation

## Purpose

Use this skill when normal build and tests are not enough to prove C++ safety.
Sanitizer findings are correctness issues until inspected and either fixed or
documented as a specific false positive.

## Sanitizer Choice

- ASAN: Use for heap/stack/global buffer bugs, use-after-free,
  use-after-scope, double-free, and many lifetime errors.
- UBSAN: Use for undefined behavior such as signed overflow, invalid shifts,
  bad enum loads, nullability violations, misalignment, and invalid casts.
- LSAN: Use for leak checks. It is often included with ASAN on Linux.
- TSAN: Use for TBB, atomics, mutexes, callbacks, shared state, shutdown,
  cancellation, or any code that can run concurrently.
- MSAN: Use for uninitialized reads when Clang and fully instrumented
  dependencies are practical. Skip when third-party/system libraries make the
  result too noisy to be useful.

Common pairings:

- Memory/lifetime/parsing/container work: ASAN + UBSAN, with LSAN enabled.
- Threading/TBB work: TSAN in a separate build, never combined with ASAN.
- Coverage or performance work: do not use sanitizer results as performance
  evidence; sanitizer builds are intentionally slower.

## Configure

Prefer repository presets if present. Otherwise create disposable build
directories so sanitizer flags do not contaminate normal builds.

```bash
cmake -S . -B build_asan -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_CXX_FLAGS="-fsanitize=address,undefined -fno-omit-frame-pointer"

cmake -S . -B build_tsan -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_CXX_FLAGS="-fsanitize=thread -fno-omit-frame-pointer"

cmake -S . -B build_msan -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_CXX_COMPILER=clang++ \
  -DCMAKE_CXX_FLAGS="-fsanitize=memory -fno-omit-frame-pointer"
```

If the project has target-scoped sanitizer options, use those instead of broad
`CMAKE_CXX_FLAGS`.

## Run

1. Build the smallest affected target first:

```bash
cmake --build build_asan --target <target>
ctest --test-dir build_asan --output-on-failure -R <test-regex>
```

2. Broaden when the affected code is shared, public, or cross-module.
3. Run TSAN separately from ASAN/UBSAN.
4. Keep test inputs deterministic. For TSAN, prefer fixed TBB arena/global
   control sizes and explicit synchronization over sleeps.

Useful runtime options:

```bash
ASAN_OPTIONS=detect_leaks=1:strict_init_order=1:halt_on_error=1
UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1
TSAN_OPTIONS=halt_on_error=1:second_deadlock_stack=1
LSAN_OPTIONS=report_objects=1
```

Set options only for the command being run unless the repository already has a
sanitizer wrapper.

## Diagnose

- Read the first sanitizer error completely, including allocation/free stacks
  and the thread creation stack for TSAN.
- Map the report to ownership, lifetime, indexing, synchronization, or integer
  assumptions in the source.
- Fix root cause, not only the reported symptom.
- If a report involves third-party code, inspect whether repository code passed
  invalid inputs, violated lifetime rules, or misused the API before blaming the
  dependency.
- Use suppressions only for proven external false positives. Keep suppressions
  narrow, named, and local to sanitizer configuration.

## Repair Loop

1. Reproduce the failing sanitizer command.
2. Inspect the smallest relevant source/header/CMake path.
3. Make one focused fix.
4. Rebuild only what is needed.
5. Rerun the failing sanitizer check.
6. Broaden to adjacent tests after the direct failure is clean.

Do not report a C++ task as complete while required sanitizer checks are still
failing.

## Reporting

State the sanitizer, build directory, target, and test command. For failures,
summarize the report type and the root cause fixed. For skipped sanitizer
checks, state the exact blocker, such as missing compiler support, incompatible
dependencies, excessive runtime, or unavailable test coverage.
