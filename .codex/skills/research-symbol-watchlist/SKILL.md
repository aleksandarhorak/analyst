---
name: research-symbol-watchlist
description: Run a current, online, evidence-led research batch for every active instrument in SYMBOLS.md and preserve per-symbol decision history plus root REPORT.md. Use when the user says "do symbols research" or asks for a complete watchlist market, price, news, behavioral, probability, or leveraged-risk update.
---

# Research Symbol Watchlist

## Trigger And Boundary

The exact request `do symbols research` means research **every active row** in
`SYMBOLS.md`; do not silently sample or omit symbols. This is impersonal
research, not individualized advice or order authority. If a user asks for a
personal recommendation, also use `check-broker-suitability`.

Read [the batch contract](references/batch-contract.md) before a live run. Use
the templates in `assets/` and the synchronization helper in `scripts/`.

## Workflow

1. Read `SYMBOLS.md`, establish the batch cutoff, and run:
   `python3 .codex/skills/research-symbol-watchlist/scripts/sync_symbol_research.py --sync`.
   Then run `migrate_symbol_templates.py --check`. Retain folders for archived
   symbols; never erase decision history.
2. Resolve every alias to an exact security, venue, share class, index, futures
   contract, fund, spot reference, or broker product. For a broker CFD or
   platform alias, require its contract specification. Mark unresolved identity
   as `insufficient evidence`; do not attach another instrument's price.
3. Browse current online sources for every symbol. Use
   `acquire-point-in-time-financial-data` for supported official or authorized
   feeds, then `verify-financial-evidence` to map packet IDs and raw hashes to
   source, price/value, quote currency, session status, and price timestamp. A
   delayed or prior close is not a live quote and must be labeled accurately.
4. Search for current news for every symbol. Use `analyze-news-catalysts` to
   verify material events, publication/event times, novelty, prior expectation,
   observed response, and fundamental transmission. If none is found, record
   sources and the searched window rather than inventing a catalyst.
5. Add relevant company fundamentals and valuation for stocks and the broader
   market regime. For commodities and any futures-based index product, use
   `analyze-commodities-and-futures` for physical drivers, curve/basis, roll,
   positioning lag, contract, settlement, margin, and delivery. Reuse current
   verified research; do not rebuild a full model from headlines.
6. Use `analyze-market-behavior` only with observable, participant- and
   horizon-specific evidence. Record alternatives and a falsifier.
7. Estimate the four required horizons: 1 trading day, 2 weeks, 1 month, and 2
   months. For each, define an unlevered flat-return band and either provide
   up/flat/down probabilities summing exactly to 100% or show `—` with
   `insufficient evidence`. Never invent percentages to fill the table. Before
   publishing populated probabilities, register them with
   `calibrate-financial-forecasts` and record forecast IDs in `LATEST.md`.
8. Use `manage-portfolio-risk` for downside and 5x exposure. Show unlevered loss
   separately from 5x gross linear P&L before financing, spread, slippage, gap,
   margin-call, and liquidation effects. Do not imply that 5x improves the
   forecast.
9. Prepare a complete `latest-v2` draft and decision JSON. Run
   `scripts/symbol_research_history.py snapshot`; it exclusively creates
   `history/<UTC-batch-id>.md`, appends the hash-chained `MANIFEST.jsonl` and
   decision row, then atomically updates `LATEST.md`. Run `verify`. Never write,
   replace, or delete historical artifacts by hand.
10. Replace `REPORT.md` with the complete batch summary. Every active symbol
    must have price status, evidence status, four horizons, confidence, risk,
    and a relative link to its `LATEST.md`. Reconcile coverage before reporting.
11. Run the synchronization helper with `--check`, migration/history
    verification, validate all links and probability sums, and state any
    unavailable data, unresolved aliases, or incomplete analyses.

## Probability Contract

- The start is the verified decision price/value at the batch cutoff.
- `Up` is above the stated flat band; `down` is below it; `flat` is inside it.
- Bands are horizon- and instrument-specific and stated as unlevered returns.
- Probabilities are mutually exclusive and exhaustive and use one calibration
  basis. The three values must total 100% after displayed rounding.
- Show confidence separately from probability. Cite calibration, base rate,
  scenario mapping, and evidence that moved the prior.
- A missing price, unresolved identity, stale decisive news, or irreconcilable
  evidence normally requires `insufficient evidence`, not a confident prior.

## Leverage Contract

All report currency is USD. For reference capital `C`, underlying return `r`,
and 5x linear exposure, show both unlevered `C * r` and approximate gross
leveraged P&L `C * 5 * r`. State that financing, spread, slippage, path,
overnight gaps, broker margin rules, stop execution, and forced liquidation can
make actual loss worse or close the position before the horizon. A 20% adverse
underlying move is approximately 100% of capital before those effects.

## Stop Conditions

Stop or limit a symbol conclusion for unresolved identity, inaccessible decisive
evidence, suspected material non-public information, manipulated sources,
unknown broker contract terms needed for leverage, or contradictory primary
records. Continue the rest of the batch and make the gap visible in `REPORT.md`.
