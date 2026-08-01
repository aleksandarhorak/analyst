# Symbol Research Report

<!-- analyst-template: report-v3 -->

> Initialized from `SYMBOLS.md`; no full-depth live batch has been completed.
> `—` means unavailable or a justified abstention, not zero.

## Batch Metadata

- Batch ID / decision cutoff: —
- Access completion time: —
- Batch status: initialized
- Reporting currency: USD
- Research depth contract: full-depth-v1
- Batch checkpoint: —
- Shared macro artifact: —
- Price policy: Not researched
- News window: Not researched
- Leverage: unlevered plus 5x gross linear exposure before financing, spread,
  slippage, path, gaps, margin calls, and liquidation
- Capacity: Impersonal research; no order authority
- Evidence packets / forecast registrations: Not researched

## Machine-Readable Batch State

```json
{{REPORT_STATE_JSON}}
```

## Batch Completion Ledger

| Symbol | Research state | Identity | Price | Fundamentals/product | Valuation/scenarios | News | Macro | Behavior | Thesis | Forecast | Downside/5x | Monitoring |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
{{COMPLETION_ROWS}}

## Shared Macro Regime

Not researched. A live v3 batch must preserve one point-in-time macro artifact
and map its transmission into every applicable symbol.

## Universe And Current Evidence

| Symbol | Instrument | USD price/value | Price as of | News/evidence | Current view | Detail |
|---|---|---:|---|---|---|---|
{{SUMMARY_ROWS}}

## Directional Probabilities

Cells are `up/flat/down`; each populated cell totals 100%. Horizons are 1
trading day, 2 weeks, 1 month, and 2 months. Bands, forecast IDs, calibration,
and abstention reasons are in the linked detail file.

| Symbol | 1 trading day | 2 weeks | 1 month | 2 months | Confidence by horizon |
|---|---:|---:|---:|---:|---|
{{PROBABILITY_ROWS}}

## Downside And 5x Exposure

| Symbol | Reference capital USD | Unlevered downside | Approx. 5x gross downside | Margin/liquidation status |
|---|---:|---:|---:|---|
{{RISK_ROWS}}

## Batch Limitations

This initialized report is not a completed research batch. A live run must
finish every feasible full-depth lane, preserve explicit blockers, create
current immutable snapshots, reconcile the batch state, and publish `complete`
or `partial` accurately.
