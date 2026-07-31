---
name: cpp-build-fix-loop
description: Build and repair C++/CMake changes until clean. Use after edits to C++ sources, headers, CMake files, dependency setup, tests, benchmarks, or generated build configuration; use when a build, configure, link, test, sanitizer, or warning-as-error failure must be diagnosed and fixed through an edit-build-test loop.
---

# C++ Build Fix Loop

## Purpose

Use this skill to close the gap between edited code and verified code. A code
task is not complete while required configure, build, link, test, sanitizer, or
warning checks are failing.

## Workflow

1. Identify the correct build entry point.
   - Prefer project presets when present.
   - Discover presets with `cmake --list-presets` and use the closest matching
     configure/build/test preset before inventing commands.
   - Otherwise inspect root CMake files, existing build directories, scripts,
     and README-like build notes.
   - Keep all build and test targets in one CMake configuration when possible.

2. Configure or reuse a build directory.
   - Reuse the project's stable compatible build directory for focused
     verification so incremental compilation remains effective.
   - Prefer `build_debug` for normal development and `build_release` for final
     validation and performance work when presets do not define the names.
   - Do not invent task-specific build directories for successive edits,
     diagnoses, or verification passes.
   - Use a separate stable directory such as `build_asan` or `build_tsan` only
     when the compiler, sanitizer, ABI, generator, or other configuration is
     incompatible with the normal Debug or Release tree.
   - Preserve user build artifacts unless the user asks for cleanup.
   - Typical fallback: `cmake -S . -B build_debug -DCMAKE_BUILD_TYPE=Debug`.

3. Build with strict diagnostics.
   - Use CMake build commands and the repository's generator.
   - Keep warnings-as-errors active for production targets.
   - Build incrementally during the edit-build-test loop; do not clean between
     ordinary iterations.
   - Build the smallest target that proves the edit first, then broaden when
     shared behavior or public interfaces changed.
   - Typical focused build: `cmake --build build_debug --target
     <target>`.

4. If the build fails, loop.
   - Read the first meaningful error, not only the final summary.
   - Classify the failure: configure, compile, link, runtime test, sanitizer,
     warning policy, missing dependency, generated file, or environment.
   - For missing required dependencies, switch to
     `skills/cpp-dependency-submodules/SKILL.md` before changing CMake or
     installing anything. Do not satisfy missing dependencies with package
     managers, PackageKit/`pkcon`, `apt`, `dnf`, `yum`, `pacman`, `zypper`,
     Homebrew, Conan, vcpkg, extracted RPMs, DEBs, APKs, release tarballs or zip
     files, prebuilt archives, `/tmp` downloads, copied libraries,
     install-prefix workarounds, or ignored `external/` directories.
   - Inspect the affected source, header, CMake target, and dependency wiring.
   - Plan the smallest correct fix.
   - Edit, rebuild, and repeat until clean or a real blocker is proven.

5. Run focused tests.
   - Start with tests closest to the edited target.
   - Run broader `ctest` when changing shared libraries, public APIs, CMake,
     dependencies, threading, or behavior used by multiple modules.
   - For test failures, reproduce the failing case, inspect the exact assertion
     or log, fix root cause, and rerun.
   - Typical focused test: `ctest --test-dir build_debug --output-on-failure -R
     <test-regex>`.

6. Run clean verification only when justified.
   - After the incremental repair loop is green, perform a clean build when the
     task's acceptance criteria require reproducibility, when build-system or
     dependency changes could leave stale artifacts, or when stale state is a
     plausible cause of a failure.
   - Prefer cleaning and rebuilding the stable final-verification tree once,
     for example `cmake --build build_release --clean-first`, instead of
     discarding the warm development tree or creating another directory.
   - Do not repeat clean builds after every source edit.

7. Report verification honestly.
   - State which configure/build/test commands were run.
   - State remaining failures or skipped checks exactly.
   - Do not claim success if required checks did not run or did not pass.

## Failure Heuristics

- Compile errors usually require reading both the source and the declaring
  header.
- Link errors usually require checking target linkage, symbol visibility,
  source membership, and dependency order.
- CMake configure errors usually require checking variable scope, target names,
  subdirectory order, package discovery, and third-party options.
- Missing dependency errors are dependency design failures, not an invitation to
  install system libraries or generate local prebuilt packages. Resolve the
  direct and transitive dependency graph as pinned submodules in the root CMake
  project unless the repository documents an explicit platform/toolchain
  exception. Do not skip a selected library because its dependency chain is
  deeper than expected, and do not turn selected features or integrations `OFF`
  merely to bypass missing lower-level libraries.
- Warning-as-error failures should be fixed, not suppressed, unless the warning
  is demonstrably wrong and the suppression is tightly scoped.
- Sanitizer failures are correctness bugs until proven otherwise.
- Repeated failures after a quick fix usually mean the plan was incomplete.
  Return to analysis rather than stacking guesses.
