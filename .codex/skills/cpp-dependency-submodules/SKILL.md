---
name: cpp-dependency-submodules
description: Research, select, vendor, and integrate C++ third-party libraries as GitHub submodules. Use when adding or changing important dependencies, CMake dependency wiring, `external/` contents, library setup options, or when a missing common library must be vendored instead of asking the user to install it.
---

# C++ Dependency Submodules

## Purpose

Use this skill when the task needs a nontrivial third-party C++ library. The
goal is to choose the best maintained library, vendor it reproducibly, and
integrate only the library/runtime features the project needs.

## Research

1. Define the capability needed and why C++23/TBB/local code is insufficient.
2. Search upstream sources and documentation for established candidates.
3. Read the selected upstream library's documentation for intended usage,
   supported CMake integration, required features, and dependency setup before
   editing this repository's CMake.
4. Compare candidates by license, maintenance, release cadence, issue health,
   CMake quality, transitive dependencies, size, platform support, and fit with
   the repository architecture.
5. Prefer permissive licenses and active upstreams.
6. Select the best solution directly unless the tradeoff is strategic,
   destructive, license-sensitive, or impossible to decide from repo context.

## Vendoring Rules

- Use GitHub submodules under `external/<name>` for every required third-party
  C or C++ library dependency.
- Pin submodules to known commits. Do not track floating branch heads.
- If a required library is not available from GitHub, choose a suitable
  GitHub-hosted alternative or ask the user before using a non-GitHub source.
- Before editing repository CMake for a new dependency, write down the full
  recursive dependency closure: direct dependency, required transitive
  dependencies, GitHub URLs, pinned commits or tags, licenses, required CMake
  targets, upstream options, and add order. Continue until every required C or
  C++ library in the chain is accounted for.
- Inspect required transitive dependencies. Vendor required transitive
  libraries as pinned GitHub submodules too unless they are already provided by
  the repository.
- Do not use system-installed versions, package-manager development files,
  extracted packages, prebuilt archives, or copied install trees for required C
  or C++ libraries.
- Dependency work must not install packages or run system package managers. Do
  not use PackageKit/`pkcon`, `apt`, `dnf`, `yum`, `pacman`, `zypper`, Homebrew,
  Conan, vcpkg, or similar tools to satisfy required C or C++ libraries.
- System discovery is allowed only for explicitly documented platform or
  toolchain interfaces, such as OS APIs, compiler runtimes, POSIX threads, or
  project-approved SDKs. A normal C or C++ library dependency is not a platform
  exception.
- Do not use package managers, PackageKit/`pkcon`, `apt`, `dnf`, `yum`,
  `pacman`, `zypper`, RPMs, DEBs, APKs, release tarballs or zip files,
  `FetchContent`, `ExternalProject`, or generated downloads.
- If configure, build, or link fails because a dependency is missing, treat that
  as dependency integration work. Do not try package installation, prebuilt
  archives, `/tmp` downloads, copied libraries, install-prefix workarounds, or
  ignored `external/` folders.
- Do not skip a selected library because it has its own dependencies. Map the
  deeper dependency chain, vendor the required GitHub submodules, choose a
  smaller suitable alternative with evidence, or ask the user to approve a
  strategic tradeoff.
- Do not set selected project features, libraries, or dependency integrations to
  `OFF` merely to bypass missing transitive dependencies. Once the repository or
  user selects a capability, its direct and recursive build dependencies are
  required unless the user explicitly approves a scope reduction.
- Required dependencies must be reproducible from Git. Do not satisfy a CMake
  configure failure by downloading archives into ignored directories such as
  `external/<name>/`.
- If CMake references `external/<name>`, expect a matching `.gitmodules` path
  unless the repository documents a narrow exception.
- Treat `.gitignore` entries for required `external/<name>/` directories as a
  failure to fix, not as normal dependency setup.
- Do not modify files inside third-party submodules. All fixes, wrappers,
  option choices, aliases, warning policy, include visibility, and adaptation
  code must live in this repository.

## CMake Integration

1. Read upstream setup documentation before editing CMake.
2. Centralize dependency logic in `cmake/dependencies.cmake` or
   `cmake/third_party/`.
3. Add external dependencies to the same CMake target graph. Do not build them
   separately in `/tmp`, copy installed headers or libraries into the
   repository, or expose them with global `include_directories()` or
   `link_directories()`.
4. Configure, build, test, and install dependencies only through the root CMake
   project. The normal flow is one root configure, one root build, and one root
   `<project-root>/install` prefix unless the user explicitly overrides it.
5. Prefer clean upstream targets. If upstream CMake is poor, isolate the wrapper
   in one local module.
6. Integrate from the root CMake graph with `add_subdirectory` or a local
   wrapper module, and set documented upstream options before adding the
   subdirectory.
7. Build only the library targets and required runtime/features. Disable
   upstream docs, tests, examples, samples, demos, tools, standalone binaries,
   benchmarks, installers, packages, language bindings, and Python components
   unless this repository explicitly needs one.
8. Use target-based linkage and namespaced aliases.
9. Make headers visible through target usage requirements so repository
   libraries and applications consume them by linking targets, not through
   global include paths.
10. Preserve license files and attribution metadata.

## Minimal External Build Policy

The project should build project targets, not dependency `all` targets. External
submodules are source inputs under `external/`; project libraries and
applications decide which external targets are needed by linking to exact CMake
targets.

- Add external subdirectories with `EXCLUDE_FROM_ALL` when upstream supports
  being consumed that way. Needed dependency targets will still build when a
  project target links to them.
- Prefer `SYSTEM` on external subdirectories or include directories when
  supported so third-party warnings do not inherit this repository's warning
  policy.
- Set documented upstream options before `add_subdirectory()`. Disable
  non-required tests, examples, samples, tools, command-line apps, docs,
  benchmarks, installers, packages, language bindings, Python, and bundled or
  downloaded dependency copies unless the project target truly needs one.
- Do not confuse non-library artifact disabling with feature disabling. Keep
  selected library targets, codec backends, renderer/plugin backends, and
  runtime integrations enabled when project targets require them; vendor their
  missing lower-level dependencies instead of turning the feature off.
- Prefer upstream component, feature, or target options that enable only the
  library/runtime pieces actually linked by this repository.
- Link repository targets only to the precise dependency targets they consume.
  Do not link umbrella targets when a narrower component target exists.
- Use `PUBLIC` linkage only when the dependency is part of a public header or
  usage requirement. Use `PRIVATE` for implementation-only dependencies.
- Verify by building the consuming repository target, not by building the
  external dependency's `all` target. If the focused build pulls in too much,
  inspect the upstream target graph and option documentation before accepting
  the integration.
- Install from root install rules only. Install repository targets and required
  runtime dependency artifacts; do not let upstream install rules publish
  examples, tools, package configs, or development files this repository does
  not intentionally ship.
- Use component installs only when the repository defines clear runtime and
  development components. Keep install destinations relative so
  `cmake --install <build_dir>` uses the root install contract and
  `cmake --install <build_dir> --prefix <alternate-prefix>` remains
  relocatable.

If `EXCLUDE_FROM_ALL` would ignore install rules that this repository needs,
prefer a repository-owned wrapper target and explicit root install rules for the
required artifacts instead of enabling the upstream project's broad install
surface.

## Superbuild Include And Library Setup

In this repository, "superbuild" means one root CMake configure, build, and
install that owns all project and dependency targets in the same target graph.
It does not mean `ExternalProject_Add`, `FetchContent`, separate dependency
prefix builds, copied install trees, or `find_package()` against locally
generated prefixes for required C or C++ libraries.

Use this shape for library/include wiring:

- Add vendored dependencies from centralized dependency CMake with
  `add_subdirectory(... EXCLUDE_FROM_ALL)` or a repository-owned wrapper target.
- Set upstream options before adding the dependency subdirectory.
- Create repository-owned alias or wrapper targets when upstream names are
  awkward or inconsistent. Do not alias an upstream ALIAS target; wrap it with a
  local real target instead.
- Expose project headers with target usage requirements such as
  `target_include_directories()` and generator expressions for build and install
  interfaces.
- Expose third-party headers only by linking dependency targets. Do not add
  dependency include directories globally or copy them into project include
  trees.
- Link exact dependency targets with `PUBLIC` only when the dependency appears
  in public headers or usage requirements. Use `PRIVATE` for implementation-only
  dependencies.
- Build and verify the consuming project target. Do not accept an integration
  that only works because an external dependency's broad `all` or install target
  was built separately.

The intended pattern is:

```cmake
# cmake/dependencies.cmake
set(FOO_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(FOO_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
add_subdirectory(${PROJECT_SOURCE_DIR}/external/foo EXCLUDE_FROM_ALL)

add_library(project_foo INTERFACE)
target_link_libraries(project_foo INTERFACE foo::foo)
add_library(Project::Foo ALIAS project_foo)
```

```cmake
add_library(project_core src/core.cpp)

target_include_directories(project_core
    PUBLIC
        $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/libs/project_core/include>
        $<INSTALL_INTERFACE:include>
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_link_libraries(project_core
    PRIVATE Project::Foo
)
```

## Dependency Closure Plan

Before adding submodules or editing CMake, produce a compact plan with one row
per dependency:

- Dependency name and whether it is direct or transitive.
- GitHub repository URL and pinned commit or tag.
- License and upstream license file path.
- Required CMake target or wrapper target name.
- Required upstream options, including options that disable bundled, downloaded,
  test, example, tool, package, Python, or install artifacts.
- Dependencies that must be added before this one.
- Public or private linkage reason for consumers.

No row may list a system package, extracted RPM/DEB/APK, downloaded archive,
copied install tree, or missing transitive dependency as the source for a
required C or C++ library. A row may use a platform/toolchain exception only
when the exception is explicitly documented and not a normal library dependency.

If any row cannot be completed from repository context and upstream
documentation, resolve that uncertainty before editing CMake unless the user has
explicitly accepted the risk.

## Transitive External Dependencies

When an external library depends on another external library, vendor both as
pinned submodules and add them in dependency order from the root CMake graph:
the lower-level dependency first, then the library that consumes it.

- Prefer upstream options that make the consuming library use the
  repository-provided dependency, such as `*_USE_SYSTEM_*`,
  `*_BUILD_BUNDLED_*=OFF`, or documented package/target override options.
- If an external project needs lower-level libraries such as image codecs,
  compression libraries, math libraries, or format backends, treat those as
  required transitive dependencies when the selected feature needs them. Do not
  make the parent dependency configure by disabling the selected feature.
- Set all upstream options before `add_subdirectory()`.
- Do not install one external dependency into another dependency's source tree
  or build output.
- If upstream target names are inconsistent, create repository-owned alias
  targets such as `Project::LibA` and `Project::LibB`.
- If an upstream project lacks a usable target or CMake package, create a local
  wrapper target in `cmake/third_party/`; do not patch the submodule unless the
  user explicitly asks to carry a fork.
- Make the consuming target link the dependency with `PUBLIC` only when the
  dependency appears in public headers or usage requirements. Use `PRIVATE` for
  implementation-only dependencies.
- If the consuming external project does not express its dependency correctly,
  fix the relationship in the repository-owned wrapper CMake.
- If the dependency chain is too tangled to represent cleanly, choose a smaller
  suitable library with evidence or ask the user to approve the tradeoff. Do not
  silently omit required transitive dependencies.

## Dependency Hygiene Audit

Before and after dependency integration, check for shortcuts that make builds
depend on local-only state:

- Search repository-owned CMake files for `file(DOWNLOAD)`, `FetchContent`, and
  `ExternalProject_Add`.
- Compare `external/<name>` references in CMake with `.gitmodules` paths.
- Inspect `.gitignore` for ignored `external/<name>/` dependency directories.
- Run `scripts/check-dependency-hygiene.sh` when this repository provides it.
- If a generated or ignored dependency is intentional, document the exception
  near the CMake integration and in `MEMORY.md` when durable.

## CMake Option Checklist

Look for documented upstream options before adding the subdirectory. Common
option families to inspect and set explicitly include:

- `BUILD_TESTING`, `<LIB>_BUILD_TESTS`, `<LIB>_BUILD_TESTING`
- `<LIB>_BUILD_EXAMPLES`, `<LIB>_BUILD_SAMPLES`, `<LIB>_BUILD_DEMOS`
- `<LIB>_BUILD_TOOLS`, `<LIB>_BUILD_CLI`, `<LIB>_BUILD_APPS`
- `<LIB>_BUILD_DOCS`, `<LIB>_BUILD_BENCHMARKS`
- `<LIB>_INSTALL`, `<LIB>_PACKAGE`, `<LIB>_BUILD_PYTHON`

Keep only options that enable the library targets and features this repository
uses. If an upstream option name is ambiguous, confirm behavior in upstream
documentation or generated target lists before relying on it.

Never use CMake options such as `ENABLE_<FEATURE>=OFF`, `WITH_<LIB>=OFF`,
`USE_<LIB>=OFF`, or similarly named switches to hide a missing dependency for a
selected capability. Use those switches only when the feature is genuinely
outside project scope, and document that scope decision in the dependency plan.

## Verification

- Configure from a clean or dependency-safe build directory.
- Build at least one target that links the new dependency.
- Run focused tests that exercise the integration.
- If setup fails, use the build-fix loop: inspect exact error, read upstream
  docs, adjust the smallest CMake/dependency detail, rebuild, and repeat.

## Documentation

Record the dependency rationale near the CMake integration or in repository
memory when durable: selected candidate, rejected alternatives, license,
submodule path, important CMake options, and verification performed.

For license records, include the SPDX identifier when known, the upstream
license file path, whether attribution is required in binary/source
distribution, and any bundled transitive dependency licenses.
