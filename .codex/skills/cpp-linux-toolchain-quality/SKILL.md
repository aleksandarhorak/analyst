---
name: cpp-linux-toolchain-quality
description: Run and interpret the Linux C++ development toolchain for formatting, building, testing, static analysis, include hygiene, debugging, profiling, and coverage. Use when Codex needs to choose or run tools such as cmake, ninja, ctest, gcc/g++, clang/clang++, clang-format, clang-tidy, cppcheck, include-what-you-use, bear, gdb, valgrind, perf, or gcov for C++ code quality verification.
---

# C++ Linux Toolchain Quality

## Purpose

Use this skill to choose the smallest useful Linux C++ quality workflow for a
change. Prefer the repository's existing presets, scripts, and build
directories before inventing commands.

## Tool Order

1. Inspect build entry points.
   - Use `cmake --list-presets` when presets exist.
   - Reuse stable compatible build directories so incremental compilation is
     preserved. Prefer `build_debug` for normal work and `build_release` for
     final or performance checks when presets do not define the names.
   - Do not create task-specific build directories. Use a separate stable tree
     only for incompatible compilers, sanitizers, ABIs, or generators.
   - Generate `compile_commands.json` with CMake when possible. Use `bear` only
     for non-CMake or legacy build commands.

2. Format.
   - Run `clang-format` on edited C++ headers and sources when formatting is in
     scope or the repository has a known style file.
   - Do not mass-format unrelated files.

3. Configure and build.
   - Prefer `cmake -S . -B <build_dir> -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`.
   - Build with `cmake --build <build_dir> --target <target>` or the
     closest existing preset.
   - Keep ordinary edit-build-test iterations incremental. Use `--clean-first`
     once on the stable final-verification tree only when a clean build is
     required by the acceptance criteria or stale artifacts are plausible.
   - Use GCC or Clang according to the repository default. Switch compiler only
     when diagnosing compiler-specific issues or sanitizer/tooling support.

4. Test.
   - Run focused tests first with `ctest --test-dir <build_dir>
     --output-on-failure -R <regex>`.
   - Broaden to all relevant tests when shared libraries, public APIs,
     dependency wiring, or behavior used by multiple modules changed.

5. Static analysis.
   - Run `clang-tidy` for normal C++ edits when `compile_commands.json` is
     available.
   - Run `cppcheck` for medium or high risk changes, especially pointer,
     bounds, lifetime, parsing, or error-handling work.
   - Treat tool findings as leads: inspect the code and fix real issues; note
     false positives with the reason.

6. Include hygiene.
   - Run `include-what-you-use` for public header, library boundary, dependency,
     or compile-time cleanup changes.
   - Review IWYU output manually; do not blindly apply changes that break
     transitive API expectations.

7. Runtime diagnostics.
   - Use `valgrind` for memory errors and leaks when sanitizers are unavailable
     or when a slower independent memory check is valuable.
   - Use `gdb` to inspect crashes, hangs, core dumps, or failing tests with
     unclear stack traces.

8. Profiling and coverage.
   - Use `perf` for CPU hotspots and performance investigations.
   - Use `gcov` for GCC coverage evidence when coverage is requested or tests
     changed enough that coverage is part of the quality gate.

## Common Commands

```bash
cmake -S . -B build_debug -DCMAKE_BUILD_TYPE=Debug -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build build_debug
ctest --test-dir build_debug --output-on-failure
clang-tidy path/to/file.cpp -p build_debug
cppcheck --enable=warning,style,performance,portability --std=c++23 --project=build_debug/compile_commands.json
include-what-you-use -p build_debug path/to/file.cpp
valgrind --leak-check=full --error-exitcode=1 ./build_debug/path/to/test
perf record --call-graph=dwarf ./build_release/path/to/benchmark
gcov path/to/file.cpp
```

Adapt paths, build directory names, and targets to the repository. Prefer
project wrappers when they exist.

## Availability And Fallbacks

- If a tool is missing, do not fail the task solely for that reason. Run the
  closest available check, state exactly which tool was missing, and suggest
  `scripts/install-linux-cpp-tools.sh --yes` when this template script is
  available.
- If `compile_commands.json` is missing, configure CMake with
  `-DCMAKE_EXPORT_COMPILE_COMMANDS=ON`; use `bear` only when CMake cannot
  produce the database.
- If a command is too broad for the change, narrow it to edited files, affected
  targets, or focused tests first, then broaden only when risk justifies it.

## Reporting

In the final response, list the commands actually run and their result. If a
tool reports findings, summarize only actionable findings and the fixes made.
If a check was skipped, state why and whether the remaining risk is low,
medium, or high.
