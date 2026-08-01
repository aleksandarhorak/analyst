# Symbol Research Batch Contract

## Required Batch Metadata

- Batch ID in UTC: `YYYY-MM-DDTHHMMSSZ`.
- Decision-time cutoff and access completion time.
- Reporting currency: USD.
- Price policy: live, delayed, official close, indicative, or unavailable.
- News search window: since the preceding decision when known; otherwise at
  least the last 7 calendar days, plus material unresolved events from the last
  60 days.
- Leverage convention: unlevered results plus 5x gross linear exposure, before
  costs and broker liquidation mechanics.
- Research capacity: impersonal analysis unless suitability was completed.
- Batch state: one `RUN.json`, active-universe hash, shared cutoff, lane status,
  blockers, resumption metadata, and the frozen ordered symbol/instrument/asset-
  class/description records used to select each analytical schema.
- Depth contract: `full-depth-v1` from `full-depth-contract.md`.

## Per-Symbol Evidence Minimum

1. Exact instrument, venue/product, quote currency, and units.
2. Current or most recent valid price/value, timestamp, session, source, and any
   delay. Convert to USD only with a sourced USD-per-native FX rate observed by
   the cutoff, retain the native value, and reconcile the multiplication.
3. Verified material news or an explicit no-material-news result with searched
   sources and window.
4. Reconciled fundamentals and valuation for equities, including numeric
   statement, cash-flow, net-debt, share-count, valuation, and equity-value
   bridges; or complete numeric product, physical, contract, curve/basis,
   index/payoff, and scenario analysis appropriate to the asset.
5. Shared macro regime plus instrument-specific transmission.
6. Observed market response and evidence-bounded behavioral analysis.
7. Complete impersonal thesis with base/bull/bear drivers, market-implied view,
   catalysts, contrary case, disconfirmers, invalidation, and monitoring.
8. Four registered probability distributions with forecast ID, base rate,
   calibration basis, scenario mapping, confidence, future outcome time, and
   resolution definition; or horizon-specific evidence-bearing abstentions.
9. Unlevered and 5x downside with liquidity, financing, spread, slippage, path,
   gap, margin, and liquidation effects.
10. A machine-readable terminal status for every full-depth lane. A missing
    dependency blocks only the outputs that depend on it.

## Durable Files

- `research/symbols/<SYMBOL>/LATEST.md`: current decision-time snapshot.
- `research/symbols/<SYMBOL>/DECISIONS.md`: append-only decision index.
- `research/symbols/<SYMBOL>/history/<batch-id>.md`: immutable full snapshot.
- `research/symbols/<SYMBOL>/history/MANIFEST.jsonl`: hash-chained snapshot and
  decision-row manifest.
- `research/batches/<batch-id>/RUN.json`: resumable batch and lane checkpoint.
- `research/batches/<batch-id>/MACRO.md`: shared point-in-time macro regime and
  source ledger, mapped to per-symbol transmission.
- `research/batches/<batch-id>/symbols/<SYMBOL>/`: resumable latest/decision
  drafts, calculations, and eligible/ineligible evidence and attempt ledger.
- `research/batches/<batch-id>/{IDENTITY,PREFLIGHT,RECONCILIATION,PUBLICATION}.md`:
  persisted shared-stage work.
- `research/batches/<batch-id>/CORRECTIONS.jsonl`: hash-chained pre-snapshot
  terminal-state corrections whose current head is stored in `RUN.json`.
  Prepared but unapplied corrections are recovered with `recover-correction`;
  post-snapshot corrections use a new batch.
- `REPORT.md`: complete cross-symbol current summary linking each `LATEST.md`.

On a new run, prepare a complete `latest-v3` draft and decision JSON, then use
`scripts/symbol_research_history.py snapshot`. It exclusively creates the
history file, appends the hash-chained manifest and decision row, and atomically
replaces `LATEST.md`. Never write these four operations by hand. Run `verify`
afterward. If an earlier record was wrong, add a dated correction linked to the
original; never rewrite or delete the prior snapshot or manifest line.

Use `scripts/migrate_symbol_templates.py --apply` only for a versioned,
non-destructive migration. It may insert a marker or a missing section but must
preserve every existing byte of substantive research. Unknown/newer versions
stop the migration.

Existing `latest-v2` and `report-v2` artifacts remain valid immutable history.
Do not rewrite them merely to change template version. Every new live batch uses
v3 and passes the full-depth control-block validator before snapshot or report
publication.

## Probability Record

| Horizon | Start | Flat band | Up | Flat | Down | Calibration | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| 1 trading day | — | — | — | — | — | Insufficient evidence | Insufficient |
| 2 weeks | — | — | — | — | — | Insufficient evidence | Insufficient |
| 1 month | — | — | — | — | — | Insufficient evidence | Insufficient |
| 2 months | — | — | — | — | — | Insufficient evidence | Insufficient |

Use `—`, not fabricated zeroes, when no distribution is defensible. When values
are present, each row must sum to 100%.

## Report Cell Convention

The compact `REPORT.md` probability cell is `U/F/D`, for example `45/30/25`.
The detailed linked file owns band, start value, evidence, and calibration.
`—` means insufficient evidence, never a 0% outcome.

## Coverage Reconciliation

- Active-universe count equals summary-table count.
- Active-universe count equals probability-table count.
- Active-universe count equals risk-table count.
- Every active symbol has a working `LATEST.md` link and decision ledger.
- Every active symbol has a current immutable snapshot for the report batch and
  the same batch ID/cutoff in its v3 control block.
- Every full-depth lane is terminal; external blockers make the batch `partial`.
- Every completion-required core lane is `complete`; a terminal abstention or
  not-applicable status in a core lane also makes the batch `partial`.
- `RUN.json` and `REPORT.md` reconcile active order, state, and blocker counts.
- `REPORT.md` reconciles every required lane, all four confidence values, and
  the exact margin/liquidation risk summary rather than hiding incomplete work.
- Missing data is explicit and does not remove the symbol from the batch.
- Archived folders remain available but do not appear as active unless restored
  in `SYMBOLS.md`.
