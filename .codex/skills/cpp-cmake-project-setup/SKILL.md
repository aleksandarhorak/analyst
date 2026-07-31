---
name: cpp-cmake-project-setup
description: Set up or repair a root CMake project contract for C++ targets, stable Debug and Release presets, a project-local install prefix, target and header installation, exported package targets, and downstream install verification. Use when bootstrapping a CMake project, adding CMakePresets.json, adding install() or package-config rules, standardizing build directories, creating environment-specific presets, or making a library consumable with find_package().
---

# C++ CMake Project Setup

## Purpose

Create one reproducible root CMake workflow for developers, agents, CI, and
downstream consumers. Keep normal builds incremental, make the default install
tree predictable, and preserve user overrides and package relocatability.

## Workflow

1. Inspect the project before editing.
   - Read the root `CMakeLists.txt`, existing presets, target definitions,
     public headers, resources, install rules, `.gitignore`, and documented
     minimum CMake version.
   - Preserve the existing generator and target names when they are sound.
   - Keep dependencies and project targets in the root CMake target graph.
   - Determine whether each target is an executable, an internal library, or a
     public library that downstream projects must consume.

2. Establish the root install contract.
   - Default top-level installs to `<project-root>/install` without overriding
     a prefix supplied by the user or a parent project:

```cmake
if(PROJECT_IS_TOP_LEVEL AND CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
  set_property(
    CACHE CMAKE_INSTALL_PREFIX
    PROPERTY VALUE "${CMAKE_SOURCE_DIR}/install"
  )
endif()
```

   - Place this default after the root `project()` call so
     `PROJECT_IS_TOP_LEVEL` and the initialized install-prefix cache entry are
     available.
   - Add `/install/` to the project-root `.gitignore`.
   - Use `include(GNUInstallDirs)` and relative destinations such as
     `${CMAKE_INSTALL_BINDIR}`, `${CMAKE_INSTALL_LIBDIR}`, and
     `${CMAKE_INSTALL_INCLUDEDIR}`. Do not prepend
     `CMAKE_INSTALL_PREFIX` to install destinations.
   - Continue to allow `-DCMAKE_INSTALL_PREFIX=<path>` and
     `cmake --install <build-dir> --prefix <path>` overrides.
   - Do not create or rely on `CMakeUserPresets.json`.

3. Install owned targets and public files.
   - Give public targets correct build-tree and install-tree usage
     requirements:

```cmake
target_include_directories(project_library
  PUBLIC
    "$<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/include>"
    "$<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>"
)
```

   - Install only targets and artifacts intentionally owned or redistributed by
     the project. Do not install every third-party target merely because it is
     present in the root graph.
   - Use target-scoped install rules. Adapt the destinations to the target kind:

```cmake
install(
  TARGETS project_library
  EXPORT ProjectTargets
  RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
  LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
  ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
  FILE_SET HEADERS DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
)
```

   - Prefer a target `FILE_SET HEADERS` for public headers when the project's
     minimum CMake version supports it. Otherwise install the explicit public
     header set while preserving its include layout.
   - Install required runtime resources, licenses, and configuration templates
     explicitly. Keep generated build-only files out of the install tree.

4. Export public libraries as relocatable CMake packages.
   - Export namespaced imported targets to a conventional package directory:

```cmake
install(
  EXPORT ProjectTargets
  FILE ProjectTargets.cmake
  NAMESPACE Project::
  DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/Project"
)
```

   - Use `CMakePackageConfigHelpers`,
     `configure_package_config_file()`, and
     `write_basic_package_version_file()` for public libraries.
   - Put `@PACKAGE_INIT@` in the package-config template and include the
     installed targets file from it.
   - Keep installed package files relocatable. Do not embed absolute source,
     build, dependency, or default-prefix paths.
   - Ensure exported public link dependencies are available to consumers and
     are found explicitly in the package config when required.

5. Add shared project presets.
   - Commit `CMakePresets.json` as the single project-supported preset source
     for users, agents, and CI.
   - Select the oldest preset schema that supports the required fields and is
     compatible with the project's documented minimum CMake version.
   - Define a hidden base configure preset and derive stable Debug and Release
     presets from it. Use `installDir` to expose the same root install contract:

```json
{
  "version": 3,
  "cmakeMinimumRequired": {
    "major": 3,
    "minor": 21,
    "patch": 0
  },
  "configurePresets": [
    {
      "name": "base",
      "hidden": true,
      "generator": "Ninja",
      "installDir": "${sourceDir}/install",
      "cacheVariables": {
        "CMAKE_EXPORT_COMPILE_COMMANDS": "ON"
      }
    },
    {
      "name": "debug",
      "inherits": "base",
      "binaryDir": "${sourceDir}/build_debug",
      "cacheVariables": {
        "CMAKE_BUILD_TYPE": "Debug"
      }
    },
    {
      "name": "release",
      "inherits": "base",
      "binaryDir": "${sourceDir}/build_release",
      "cacheVariables": {
        "CMAKE_BUILD_TYPE": "Release"
      }
    }
  ],
  "buildPresets": [
    {
      "name": "debug",
      "configurePreset": "debug"
    },
    {
      "name": "release",
      "configurePreset": "release"
    }
  ],
  "testPresets": [
    {
      "name": "debug",
      "configurePreset": "debug",
      "output": {
        "outputOnFailure": true
      }
    },
    {
      "name": "release",
      "configurePreset": "release",
      "output": {
        "outputOnFailure": true
      }
    }
  ]
}
```

   - Adapt the generator and minimum version to the repository rather than
     copying the example blindly.
   - Keep standard build presets incremental. Do not set `cleanFirst` on the
     normal Debug or Release preset.
   - Use `cacheVariables` for CMake options and `environment` only for real
     process-environment requirements. Never commit secrets.

6. Model environment variants without unnecessary rebuilds.
   - Put test-only or runtime-only environment differences in inherited test
     presets. Reuse the same `build_release` output when those values cannot
     affect compilation or linking:

```json
{
  "name": "release-service-a",
  "inherits": "release",
  "environment": {
    "PROJECT_RUNTIME_PROFILE": "service-a"
  }
}
```

   - Give compiler-, ABI-, dependency-, generated-code-, or feature-affecting
     variants their own inherited configure preset and stable binary directory,
     such as `build_release_cuda`. Never alternate incompatible configurations
     in one build tree.
   - Reuse each compatible stable directory across runs. Do not create
     task-named preset or build directories.
   - Install only the selected final variant into the shared root `install`
     tree. Do not overlay incompatible variants or assume `cmake --install`
     removes stale files.

7. Verify the complete contract.
   - List and configure presets:

```bash
cmake --list-presets
cmake --preset debug
cmake --build --preset debug --target <affected-target>
ctest --preset debug
cmake --preset release
```

   - Keep edit-build-test iterations incremental. When final acceptance needs a
     clean proof, clean and rebuild the stable Release tree once:

```bash
cmake --build build_release --clean-first
ctest --preset release
cmake --install build_release
```

   - Confirm the default install lands in `<project-root>/install` and contains
     only intended artifacts.
   - For a public library, configure and build a minimal out-of-tree consumer
     that uses `find_package(Project CONFIG REQUIRED)` and links
     `Project::<target>` from the installed prefix.
   - Verify relocatability with a temporary `cmake --install ... --prefix`
     destination when package files or install paths changed.
   - After C++ or CMake edits, use
     `skills/cpp-build-fix-loop/SKILL.md` until required builds and tests pass.

## Completion

Report the presets, build directories, install prefix, installed targets,
package exports, and exact verification commands. State whether clean Release,
install-tree, relocatability, and downstream-consumer checks passed or were
skipped. Do not claim the setup is complete while required install or consumer
checks fail.
