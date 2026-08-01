# Decision: Operational Financial Evidence And Model Governance

## Problem

The agent has strong analytical instructions but lacks a shared machine-readable
evidence contract, executable outcome evaluation, calibrated forecast history,
and enforced write-once research records.

## Constraints

- Standard-library tooling only; no package-manager or hidden service dependency.
- No committed API keys, client data, licensed payloads, or provider credentials.
- Public official data is not mislabeled as live price/news coverage.
- Research remains analysis-only and cannot submit orders.
- Historical decisions must be reproducible from what was knowable at cutoff.

## Decision Criteria

Temporal integrity, exact identity, unit/currency safety, provenance,
deterministic failure behavior, auditability, privacy, provider portability,
low operational complexity, and testability without live network access.

## Options Considered

1. Keep prose-only workflows.
2. Build one monolithic watchlist fetcher around free unofficial endpoints.
3. Adopt shared versioned contracts with official-source adapters, pluggable
   licensed providers, append-only ledgers, and deterministic evaluations.

## Evidence Summary

Official sources expose different temporal semantics: EDGAR filings and XBRL
facts carry filing/context/unit structure; ALFRED distinguishes historical
vintages; COT distinguishes report and release dates; futures distinguish trade,
close, and official settlement. Revised model-risk guidance emphasizes outcome
analysis, recalibration, monitoring, documentation, inventory, and third-party
oversight. These differences cannot be safely flattened into a price plus URL.

## Recommended Choice

Choose option 3. Establish `evidence-packet-v1` as the acquisition boundary;
validate its complete contract before analysis. Bind acquisition to a versioned
instrument registry seeded from current official identity data, while retaining
explicit unresolved states for broker, commodity, and index aliases. Implement
SEC, FRED/ALFRED, and CFTC adapters over official HTTPS APIs. Define a
provider-neutral stdin/stdout contract for price and news adapters so licensed
services can be connected without repository secrets. Fail closed on unresolved
or inconsistent identity, absent timestamps, ambiguous cutoff-day dates or units,
partial responses, stale decisive data, or unsupported provider semantics.

Add separate append-only forecast and outcome ledgers, deterministic Brier/log
scores and calibration bins, an executable candidate-output evaluation runner,
and hash-manifested symbol snapshots. Use versioned, non-destructive template
migrations. Add specialist commodity/futures and client-data governance skills,
then route watchlist, valuation, suitability, evidence, and evaluation through
the new controls.

## Why This Choice

It separates acquisition from judgment, makes time and identity explicit,
supports offline regression tests, avoids dependence on an unlicensed free
quote source, and permits stronger providers later without changing analytical
contracts. Append-only facts and outcomes prevent hindsight editing while Git
adds a second audit layer.

## Rejected Alternatives

- Prose-only controls are hard to execute consistently and cannot be regression
  tested for exact temporal or arithmetic failures.
- A monolithic unofficial fetcher couples analysis to unstable schemas, unclear
  rights, and misleading coverage; it also prevents clean provider replacement.
- A database or external orchestration service is unnecessary at this scale and
  would add deployment and secret-management requirements not requested here.

## Risks And Unknowns

- Official schemas and endpoint limits can change; adapters require contract
  tests, raw hashes, explicit user-agent policy, backoff, and observable errors.
- Exact broker aliases, leverage, margin, and price/news licensing remain
  provider-specific and must not be inferred.
- Forecast samples will initially be small; calibration summaries must publish
  sample sizes and avoid conclusions from sparse bins.
- Files plus locks are suitable for this repository, not a multi-host writer.
- Privacy and suitability conclusions still require current jurisdictional
  research and qualified human review.

## Implementation Implications

- Add four repo skills: acquisition, forecast calibration, commodity/futures
  analysis, and client-data governance.
- Add schemas, an official-source-seeded versioned instrument registry,
  standard-library adapters, deterministic
  fixtures/tests, evaluation/calibration/history scripts, and quality gates.
- Strengthen evidence, watchlist, valuation, suitability, macro, fundamental,
  risk, and evaluation skills to consume shared contracts.
- Treat API secrets as environment/runtime input and client facts as prohibited
  repository content.

## Verification Plan

- Validate schemas and every skill folder.
- Replay SEC, FRED, CFTC, price, and news fixtures without network access.
- Test stale data, complete identity, revisions, units, aliases,
  partial/rate-limit errors, futures
  lag/settlement, PII leakage, exact probability scoring, immutable overwrite,
  and migration preservation.
- Run syntax checks, focused test suites, stage gates, and the final repository
  quality gate before tested merge into `dev`.

## Source Index

See [sources.md](sources.md) and [papers/manifest.md](papers/manifest.md).

## Open Questions

- Which licensed price/news provider and broker contract catalogue will be
  authorized for production use?
- What client jurisdiction, regulated capacity, storage system, retention
  schedule, and reviewer roles apply in a real deployment?
