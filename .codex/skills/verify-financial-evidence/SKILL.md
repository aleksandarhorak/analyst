---
name: verify-financial-evidence
description: Verify financial claims with primary, point-in-time sources and an auditable evidence ledger. Use before relying on prices, filings, estimates, economic releases, news, client facts, regulations, or any disputed or time-sensitive input to an investment, portfolio, execution, or suitability decision.
---

# Verify Financial Evidence

## Purpose

Build a decision-time-safe evidence base before analysis. Preserve what was
known, when it was knowable, who reported it, and what remains uncertain.

## Procedure

1. Define the claim, entity or instrument, jurisdiction, currency, horizon, and
   decision-time cutoff.
2. Acquire repeatable inputs with `acquire-point-in-time-financial-data` when an
   adapter applies. Validate `evidence-packet-v1`, recompute its content hash,
   and reject failed quality, unresolved identity, after-cutoff evidence,
   partial output, or a secret-bearing request/source record.
3. Search current primary sources first: filings, issuer releases, exchanges,
   regulators, central banks, statistical agencies, courts, and original data.
4. Record event, publication, revision, access, and as-of timestamps separately.
5. Classify each item as reported fact, derived fact, estimate, scenario, or
   opinion. Show derivations and units.
6. Check fiscal periods, release vintages, restatements, corporate actions,
   currencies, share counts, survivorship, and licensing constraints.
7. Reconcile the packet's exact source locator, native value/unit/currency, and
   instrument identifiers to the cited primary record. A valid packet proves
   transport integrity, not economic correctness or sufficiency.
8. Corroborate material or surprising claims. Record contradictions instead of
   silently resolving them.
9. Grade source authority, temporal fitness, and claim confidence separately.
10. State missing evidence and abstain when it could reverse the decision.

Use [the evidence-ledger template](references/evidence-ledger.md). Cite every
decision-relevant claim near its use.

## Source Priority

Prefer original official records, then original research and reputable direct
reporting. Treat aggregators, vendor-normalized fields, search snippets, social
posts, anonymous claims, and generated summaries as leads requiring validation.
Do not treat a later revised series as data available at an earlier decision.

## Required Output

- Scope and decision-time cutoff.
- Evidence ledger with stable links and timestamps.
- Packet ID and raw SHA-256 for adapter-backed evidence.
- Reconciled calculations and source-to-claim mapping.
- Contradictions, staleness, and point-in-time risks.
- Confidence and unresolved gaps.

## Stop Conditions

Stop and clearly limit the conclusion for suspected material non-public
information, inaccessible decisive evidence, unresolved entity identity,
materially inconsistent primary records, or an unknowable historical vintage.
