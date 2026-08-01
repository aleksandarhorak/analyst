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

## Per-Symbol Evidence Minimum

1. Exact instrument, venue/product, quote currency, and units.
2. Current or most recent valid price/value, timestamp, session, source, and any
   delay. Convert to USD only with a sourced FX rate and retain native value.
3. Verified material news or an explicit no-material-news result with searched
   sources and window.
4. Fundamental/company or macro/supply-demand state appropriate to asset class.
5. Observed market response and a bounded behavioral analysis.
6. Bull, base/flat, and bear drivers; disconfirmers and invalidation.
7. Four probability distributions or `insufficient evidence`.
8. Unlevered and 5x downside with financing, gap, margin, and liquidation caveats.
9. Confidence, next catalysts, monitoring signals, and next review.

## Durable Files

- `research/symbols/<SYMBOL>/LATEST.md`: current decision-time snapshot.
- `research/symbols/<SYMBOL>/DECISIONS.md`: append-only decision index.
- `research/symbols/<SYMBOL>/history/<batch-id>.md`: immutable full snapshot.
- `research/symbols/<SYMBOL>/history/MANIFEST.jsonl`: hash-chained snapshot and
  decision-row manifest.
- `REPORT.md`: complete cross-symbol current summary linking each `LATEST.md`.

On a new run, prepare a complete `latest-v2` draft and decision JSON, then use
`scripts/symbol_research_history.py snapshot`. It exclusively creates the
history file, appends the hash-chained manifest and decision row, and atomically
replaces `LATEST.md`. Never write these four operations by hand. Run `verify`
afterward. If an earlier record was wrong, add a dated correction linked to the
original; never rewrite or delete the prior snapshot or manifest line.

Use `scripts/migrate_symbol_templates.py --apply` only for a versioned,
non-destructive migration. It may insert a marker or a missing section but must
preserve every existing byte of substantive research. Unknown/newer versions
stop the migration.

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
- Missing data is explicit and does not remove the symbol from the batch.
- Archived folders remain available but do not appear as active unless restored
  in `SYMBOLS.md`.
