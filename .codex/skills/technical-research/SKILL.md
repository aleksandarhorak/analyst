---
name: technical-research
description: Conduct evidence-driven research using current primary sources, official standards, papers, datasets, documentation, and reproducible benchmarks. Use when a financial or agent-development decision depends on online research, competing methods, current rules, source selection, papers or PDFs, data quality, or an explicit best-choice recommendation.
---

# Technical Research

## Purpose

Use this skill before planning or implementation when a decision depends on
external evidence. Produce an auditable dossier under `research/<topic-slug>/`
and a clear decision that can be consumed without repeating the research.

## Research Directory

```text
research/<topic-slug>/
  README.md
  decision.md
  sources.md
  papers/
    manifest.md
    downloaded/
```

Keep locally reviewed PDFs in `papers/downloaded/` and ignore them when license
or repository size makes redistribution inappropriate. Stable links and review
notes remain tracked.

## Source Priority

Choose primary sources suited to the question:

1. Regulators, exchanges, central banks, statistical agencies, courts,
   standards bodies, filings, issuer releases, and official documentation.
2. Original datasets with methodology, vintages, and licensing terms.
3. Peer-reviewed papers, working papers, technical reports, and author copies.
4. Reproducible benchmarks and repositories with disclosed methodology.
5. Direct reputable reporting, professional analysis, and implementation
   postmortems.
6. Aggregators, blogs, forums, social posts, and comments as lower-confidence
   leads requiring corroboration.

Prefer current primary guidance. Preserve publication, event, access, version,
revision, and as-of dates. When sources conflict, show the conflict and explain
which evidence is most authoritative for the decision.

## Research Procedure

1. Restate the problem, non-goals, jurisdiction or platform, decision cutoff,
   constraints, and criteria.
2. Search primary sources and original data first.
3. Search papers, reports, competing methods, and adverse evidence.
4. Download relevant documents and read every relied-on document completely;
   do not equate an abstract or snippet with a full review.
5. Inspect data construction, sample, vintages, survivorship, revisions,
   conflicts, benchmark design, costs, and reproducibility.
6. Use subagents only when explicit instructions allow it and lanes are truly
   independent. Require links, dates, methods, limitations, and confidence.
7. Compare options against the stated decision criteria. Include a simple
   baseline and rejected alternatives.
8. Record source metadata, exact claims used, confidence, contradictions, and
   unresolved gaps.
9. Write `decision.md` with the selected choice, rationale, risks,
   implementation implications, and verification plan.
10. Stop when more evidence is unlikely to change the decision or remaining
    uncertainty is explicit.

## Required Files

`README.md` records problem, scope, non-goals, status, and links.

`sources.md` records title, URL or local path, access date, publication/version,
claims used, and confidence.

`papers/manifest.md` records title, authors, year, venue, source, local path when
applicable, methods, findings, limitations, and confirmation of full review.

`decision.md` uses:

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

- Do not choose a method, dependency, data source, strategy, or policy because
  it is popular. Tie it to evidence and constraints.
- Do not generalize historical anomalies without point-in-time data,
  out-of-sample testing, realistic costs, capacity, and regime limitations.
- Do not finalize while a relied-on document remains unread or decisive source
  contradictions remain hidden.
- Legal, regulatory, tax, and product conclusions require current primary
  sources and qualified review for actual deployment.
- State when no option has enough evidence.

## Handoff

Hand the completed `decision.md` to `implementation-planning` for repository
changes. For financial analysis, route the verified evidence to the relevant
finance skill and preserve the source ledger.
