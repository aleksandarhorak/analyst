# Financial Data And Model Governance Research

## Problem

Turn the analyst's prose-only evidence, forecast, and evaluation controls into
repeatable operational contracts without pretending that free public sources
provide licensed live prices or complete news coverage.

## Scope

- Point-in-time acquisition from SEC EDGAR, FRED/ALFRED, and CFTC public data.
- A provider-neutral contract for licensed price and news data.
- Immutable evidence, forecast, outcome, and symbol-research records.
- Executable regression evaluation and probability calibration.
- Commodity/futures product controls and client-data governance.

## Non-goals

- Order submission or autonomous trading.
- A substitute for legal, privacy, suitability, or compliance review.
- Circumventing API terms, redistribution rights, authentication, or rate limits.
- Claiming a current quote when only delayed, indicative, or settlement data is
  available.

## Decision Cutoff

Research was checked against primary sources available on 2026-08-01. Current
rules and provider terms must be rechecked at use time.

## Status

Decision accepted for implementation. See [decision.md](decision.md),
[sources.md](sources.md), and [the reviewed-document manifest](papers/manifest.md).
