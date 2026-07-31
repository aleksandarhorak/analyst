---
name: cpp-architecture-review
description: Review or design C++ library architecture, layering, APIs, ABI, and duplication. Use for new libraries, refactors, public interface changes, dependency direction checks, plugin or FFI boundaries, module ownership questions, or architecture reviews before implementation.
---

# C++ Architecture Review

## Purpose

Use this skill when the task changes structure, ownership, public interfaces, or
dependency direction. The goal is to keep libraries small, agnostic, testable,
and easy to reuse.

## Layering

Check dependency direction:

- Foundation/TBB may depend on the C++ standard library, atomics, OS primitives
  where justified, and TBB.
- Core may depend on Foundation and standard C++ facilities.
- Abstraction may depend on Core and Foundation.
- Application may depend on all lower layers.

Lower layers must not depend on upper layers. Circular dependencies are not
allowed. If a lower layer needs behavior from above, define an interface or
policy in an allowed lower layer and inject the implementation from above.

## Library Boundary Review

- Each library should own one bounded capability.
- Public APIs should expose only what the next layer needs.
- Internal details belong in implementation files, private headers, `.ipp`
  files, or `impl` namespaces.
- Public ABI is expensive. Document migration when changing exported types,
  symbols, or CMake targets.
- Data models should stay independent from transport, storage, UI, scripting,
  and binding layers.
- Plugin and FFI boundaries must make ownership, allocation, exceptions, and
  threading explicit.

## CMake Target Boundary Review

- Check that target linkage mirrors architecture: lower-layer targets must not
  link application, UI, CLI, plugin, test, or binding targets.
- Keep include directories private unless they are part of the installed or
  consumed public API.
- Public compile definitions and options are part of the downstream contract;
  keep them minimal and documented.
- Prefer namespaced aliases for consumed targets and avoid global include paths,
  global definitions, or directory-wide compile options.
- Treat exported CMake targets as public API. Renames, visibility changes, and
  dependency leaks need migration notes.

Bad dependency directions:

- Core model or algorithm target linking a CLI/app target for logging,
  formatting, flags, or configuration.
- Foundation/TBB utility depending on domain types from Core or Application.
- A public library exposing private third-party headers or compile definitions
  through its interface without making that dependency part of the API.
- Test helpers leaking into production target linkage instead of staying in test
  targets or fixtures.

## Duplication And Reuse

- Search for existing implementations before creating a new abstraction.
- If two libraries need the same behavior, move it to the lowest common layer.
- Do not add an abstraction unless it removes real complexity, prevents
  duplication, or isolates a genuine variability point.
- Prefer standard library and local helpers over bespoke utilities.

## Review Procedure

1. Map affected files, targets, and layers.
2. Inspect headers and source together.
3. Search for similar code and existing patterns.
4. Check public/private target linkage and include directories.
5. Identify ABI/API changes and downstream impact.
6. Confirm tests can exercise the library without requiring application context.
7. Report findings by severity with file and line references when reviewing.

## Output

For design work, state the selected structure, rejected alternatives, layer
ownership, dependency direction, CMake targets, and verification plan.

For review work, lead with bugs, layering violations, API risks, dependency
leaks, duplication, and missing tests before summarizing positives.
