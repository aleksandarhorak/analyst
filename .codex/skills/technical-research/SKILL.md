---
name: technical-research
description: Evidence-driven technical research for choosing technologies, libraries, algorithms, standards, papers, public benchmarks, documentation, and implementation approaches. Use when Codex must look online, compare current options, read papers or PDFs, evaluate upstream library documentation, inspect public benchmarks, or make a best-choice recommendation before planning a feature, dependency, architecture, or performance-sensitive solution.
---

# Technical Research

## Purpose

Use this skill before planning or implementation when the answer depends on
external evidence, current technology, papers, documentation, public benchmark
results, or tradeoffs between multiple viable options.

The output is a research dossier under `research/<topic-slug>/` and a clear
decision that another agent can use without repeating the research.

## Research Directory

Create or update this structure:

```text
research/
  <topic-slug>/
    README.md
    decision.md
    sources.md
    papers/
      manifest.md
      downloaded/
```

Use a short lowercase topic slug. Keep downloaded papers and PDFs in
`research/<topic-slug>/papers/downloaded/`. Read every downloaded PDF completely
before finalizing the decision.

## Source Priority

Prefer sources in this order:

1. Official specifications, standards, reference manuals, and project
   documentation.
2. Upstream repository documentation, release notes, examples, build files,
   issues, and maintainer guidance.
3. Published papers, preprints, technical reports, conference material, and
   author-maintained project pages.
4. Reproducible public benchmarks, benchmark repositories, and benchmark
   methodology writeups.
5. Reputable engineering blogs, migration reports, and production postmortems.
6. Forums, social threads, Q&A sites, and comments as low-confidence signals.

Prefer primary sources over summaries. When sources conflict, keep the conflict
visible and explain which source is more authoritative for this repository's
decision.

## Subagent Research

Use subagents when the research splits into independent lanes and the available
tools support them. Assign narrow prompts and require evidence, links, dates,
and confidence levels.

Useful lanes:

- Official docs and standards.
- Papers and PDFs.
- Library ecosystem, maintenance, API stability, and build integration.
- Public benchmarks and reproducibility.
- Security, reliability, portability, and operational risks.
- Competing options and rejected alternatives.

The main agent owns the final synthesis. Do not accept a subagent conclusion
without checking its cited evidence.

## Research Procedure

1. Restate the problem, constraints, required platform, and decision criteria.
2. Search official documentation and upstream repositories first.
3. Search for papers, technical reports, and implementation notes.
4. Download relevant PDFs into the research folder and read each one completely.
5. Search for public benchmarks and inspect methodology before trusting results.
6. Search blogs and forums only after primary sources have been checked.
7. Compare options with a decision matrix tied to repository constraints.
8. Record all sources with access dates, URLs, versions, commits, or paper
   metadata.
9. Write `decision.md` with the selected choice, rationale, rejected
   alternatives, risks, and verification plan.
10. Stop research when additional sources are unlikely to change the decision,
    or when the remaining uncertainty is clearly documented.

## Required Files

`README.md`:

- Problem summary.
- Scope and non-goals.
- Research status.
- Pointers to the decision and source files.

`sources.md`:

- Source title.
- URL or local file path.
- Access date.
- Version, commit, publication venue, or publication date when available.
- Key claims used in the decision.
- Confidence level: high, medium, or low.

`papers/manifest.md`:

- Paper title.
- Authors.
- Year or publication date.
- Source URL.
- Local PDF path when downloaded.
- Key methods, findings, and limitations.
- Confirmation that the PDF was read completely.

`decision.md`:

```markdown
# Decision: <topic>

## Problem
## Constraints
## Decision Criteria
## Options Considered
## Evidence Summary
## Recommended Choice
## Why This Choice
## Rejected Alternatives
## Risks And Unknowns
## Implementation Implications
## Verification Plan
## Source Index
## Open Questions
```

## Decision Rules

- Do not choose a dependency, architecture, algorithm, or technology because it
  is popular. Tie the choice to evidence and repository constraints.
- Prefer current official guidance over old tutorials.
- Prefer reproducible benchmarks over headline numbers.
- Do not finalize a decision while any downloaded PDF remains unread, partially
  read, or only skimmed.
- Prefer simpler standard-library or local solutions when evidence does not
  justify a new dependency.
- For C++ dependencies, pass dependency decisions to
  `skills/cpp-dependency-submodules/SKILL.md` after research.
- For architecture decisions, pass structure decisions to
  `skills/cpp-architecture-review/SKILL.md` after research.
- For hot-path or parallel performance decisions, pass validation needs to
  `skills/cpp-performance-benchmark/SKILL.md` and
  `skills/tbb-concurrency/SKILL.md` after research.

## Handoff

When research is complete, hand off `research/<topic-slug>/decision.md` to
`skills/implementation-planning/SKILL.md`. Planning should consume the decision
instead of restarting the research unless gaps or contradictions remain.
