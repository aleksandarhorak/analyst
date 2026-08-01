---
name: acquire-point-in-time-financial-data
description: Acquire and normalize point-in-time financial evidence from official SEC EDGAR, FRED/ALFRED, and CFTC sources or a licensed price/news provider into versioned evidence packets. Use before financial analysis needs current or historical prices, filings, fundamentals, macro vintages, positioning, or news and exact identity, timestamps, units, provenance, licensing, and failure state must be preserved.
---

# Acquire Point-In-Time Financial Data

## Boundary

Acquire evidence; do not draw an investment conclusion. Never relabel delayed,
indicative, prior-close, report-date, or settlement data as a live quote. Never
place orders. Keep credentials in runtime environment variables or the external
provider process, not arguments, packets, logs, fixtures, or repository files.

Read [the evidence-packet schema](references/evidence-packet-v1.schema.json) when
creating or validating packets. Read [the provider contract](references/provider-contract.md)
before connecting price or news services.
Use [the versioned instrument registry](references/instrument-registry-v1.json)
as the identity allowlist. An unresolved registry entry is an explicit stop, not
permission to infer an instrument from ticker similarity.

## Procedure

1. Set a UTC decision cutoff and state the required claim, instrument, venue,
   share class or contract, currency, field, frequency, and latency.
2. Resolve a stable identifier in `instrument-registry-v1`. Reconcile ID,
   symbol, venue, asset class, and source-specific identifier. Do not map a
   broker alias, index, spot reference, fund, future, CFD, ADR, or share class
   by ticker similarity.
3. Select the primary source. Prefer SEC for filings/XBRL, ALFRED real-time
   periods for historical macro vintages, CFTC PRE for COT positioning, an
   exchange for contract/settlement facts, and an authorized provider for price
   or news coverage.
4. Run `scripts/acquire_financial_data.py` with explicit identifiers, cutoff,
   units, and fixture or network source. For live SEC requests set a descriptive
   `FINANCIAL_DATA_USER_AGENT`; for FRED set `FRED_API_KEY`.
5. Preserve the raw SHA-256, source URL without secrets, access time, event/as-of
   time, first-known or publication time, revision identifiers, units, currency,
   classification, and rights note.
6. Validate the output. Validation enforces the full dependency-free packet
   contract and registry identity. Treat `quality.status=fail`, any identity
   field mismatch,
   after-cutoff evidence, missing decisive timestamps, ambiguous units,
   truncation, partial response, or provider error as unavailable evidence.
7. Hand passing packets to `verify-financial-evidence`. Preserve conflicts as
   separate packets; do not silently choose or average them.

## Adapter Rules

- SEC: reconcile response CIK and issuer name to the registry, use explicit
  taxonomy, concept, and reported unit, and preserve accession, form, filing
  date, period, frame, and raw unit.
- FRED/ALFRED: request explicit `realtime_start` and `realtime_end`; preserve
  each observation's real-time interval and do not substitute today's revision.
- CFTC: use the official dataset and contract-market code; preserve report date
  separately from a verified publication time and state classification limits.
- Price/news provider: require `provider-response-v1`, exact ID/symbol/venue/
  asset-class identity, session/latency/adjustment semantics, requested currency,
  maximum age, timestamps, entitlement/redistribution note, and a complete/error
  indicator. Reject stale, mismatched, or partial responses.

## Output

Emit `evidence-packet-v1` JSON. A packet is transport evidence, not proof that a
claim is correct or sufficient. Cite its source near every downstream material
claim and retain the packet or its immutable hash with the decision record.
