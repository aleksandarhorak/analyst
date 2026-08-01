---
name: research-symbol-watchlist
description: Run the potentially hours-long, resumable, full-depth research workflow for every active instrument in SYMBOLS.md, using applicable specialist analysis, bounded parallel lanes, immutable per-symbol history, and root REPORT.md. Use whenever the user says "do symbols research" or requests a complete watchlist research batch.
---

# Research Symbol Watchlist

## Trigger And Boundary

The exact request `do symbols research` means the complete applicable analytical
pipeline for **every active row** in `SYMBOLS.md`; do not silently sample or omit
symbols. It is not a quick quote/news scan or a menu of optional follow-ups. A
batch may take hours and must be resumable. This is impersonal research, not
individualized advice or order authority.

Read both [the full-depth contract](references/full-depth-contract.md) and
[the batch contract](references/batch-contract.md) before a live run. Use the
templates in `assets/` and helpers in `scripts/`.

## Workflow

1. Read `SYMBOLS.md`, establish one batch ID and decision cutoff, and run
   `sync_symbol_research.py --sync` followed by
   `migrate_symbol_templates.py --check`. Initialize the resumable checkpoint
   with `python3 .codex/skills/research-symbol-watchlist/scripts/symbol_research_batch.py init`.
   This creates governed batch-local drafts, calculations, evidence ledgers,
   shared work files, and a correction ledger. Retain archived folders and
   never erase decision history. Treat the ordered symbol, instrument, asset
   class, and description frozen in `RUN.json` as authoritative for schema
   selection; reject a draft that changes its class.
2. Plan bounded, non-overlapping parallel lanes when useful. Share the exact
   identity registry, cutoff, units, source hierarchy, and output contract.
   Keep shared files, snapshots, Git integration, regulated judgments, and final
   synthesis with the lead. Checkpoint completed waves in `RUN.json` with their
   batch-local artifact paths and evidence or attempt IDs.
3. Resolve every alias to an exact security, venue, share class, index, futures
   contract, fund, spot reference, or broker product. Require a broker contract
   specification for a platform alias. Never attach another product's data to an
   unresolved alias.
4. Acquire current online evidence for every symbol. Use
   `acquire-point-in-time-financial-data` for official or authorized feeds and
   `verify-financial-evidence` for source, price/value, units, currency, session,
   timestamp, cutoff eligibility, packet ID, and raw hash. Label delayed or
   prior-close values accurately. For non-USD observations, preserve a sourced
   USD-per-native FX rate and observation time and reconcile native value times
   the rate to the reported USD value.
5. Use `analyze-news-catalysts` for verified event chronology, prior
   expectation, novelty, materiality, observed response, and transmission. A
   no-material-news result requires its search window and sources.
6. Run one current shared regime analysis with `analyze-macroeconomy`, then map
   transmission to every symbol. For each resolved equity use
   `analyze-company-fundamentals`, `value-company-and-forecast`, and
   `build-investment-thesis`. Require reconciled fundamentals, economically
   linked scenarios, suitable valuation lenses, and a complete impersonal
   thesis. Equity records require numeric statement, cash-flow, net-debt, and
   share-count bridges; valuation records require at least two numeric methods,
   linked evidence-bearing inputs, ordered base/bull/bear values, an
   enterprise-to-equity/share bridge when applicable, and sensitivities. For
   commodities and futures-based products use
   `analyze-commodities-and-futures` for exact product, physical drivers,
   numeric curve/basis reconciliation, roll, positioning lag, settlement,
   margin, and delivery. Other products expose underlying/payoff mechanics,
   units, liquidity, limitations, and evidence.
7. Use `analyze-market-behavior` only with observable participant- and
   horizon-specific evidence. Record alternatives and a falsifier; abstain from
   psychology when those observations are unavailable.
8. Assess 1 trading day, 2 weeks, 1 month, and 2 months. Define an unlevered
   flat band and either supply up/flat/down probabilities totaling 100% or a
   horizon-specific justified abstention. Register populated distributions with
   `calibrate-financial-forecasts` before publication and record forecast ID,
   base rate, calibration basis, scenario mapping, confidence, future outcome
   time, and resolution definition for each horizon.
9. Analyze instrument-level downside and 5x exposure. Separate unlevered loss
   from approximate 5x gross linear P&L and include financing, spread, slippage,
   path, gap, margin-call, and liquidation effects. Use
   `manage-portfolio-risk` only when an actual portfolio or mandate is supplied.
10. Continue every independent lane when another dependency fails. Each lane
    ends `complete`, `abstained`, `blocked`, or `not_applicable`, with evidence,
    an exact reason, and a next action where required. Missing price does not
    excuse skipped filing, business/product, news, macro, behavior, or thesis
    work. `Insufficient evidence` is a conclusion, not proof of effort.
    Every abstention preserves the evidence and attempts that justify it.
    Identity, price, fundamentals/product, valuation/scenarios, news, macro
    transmission, thesis, downside/5x, and monitoring are completion-required
    core lanes: any non-complete terminal state among them makes the symbol and
    batch `partial`. Behavior and directional-forecast abstentions may coexist
    with `complete` only when every core lane is complete.
11. Complete central reconciliation, then prepare the governed batch-local
    `latest-v3` draft and decision JSON. Run
    `symbol_research_history.py snapshot`; it exclusively creates the immutable
    snapshot, appends the hash-chained manifest and decision row, and atomically
    updates `LATEST.md`. Never edit history artifacts by hand.
12. Finalize and verify `RUN.json`, then replace `REPORT.md` with `report-v3`.
    Retain Universe And Current Evidence, Directional Probabilities, and
    Downside And 5x Exposure and add batch/depth reconciliation. A run with
    blockers is `partial`, not `complete`.
13. Run synchronization, migration, batch, history, symbol-contract,
    probability, and full quality verification. Do not call the batch complete
    while any required lane is nonterminal or skipped.

Use `correct-lane` or `correct-shared` with a substantive reason before
snapshot when central review finds an error in terminal checkpoint state. The
helper prepares a durable hash-chained correction record before atomically
advancing target state and the chain head. If interruption leaves one prepared
record, `verify` fails closed; run `recover-correction` only after its previous
head and previous value have been checked. After a snapshot exists, preserve it
and start a new corrective batch instead of rewriting history.

## Probability Contract

- The start is the verified decision price/value at the batch cutoff.
- `up` is above the stated band, `down` below it, and `flat` inside it.
- Each populated distribution is exhaustive, uses one calibration basis, totals
  100% after displayed rounding, and has a registered forecast ID.
- Show confidence separately from probability. Cite the base rate, scenario
  mapping, and evidence that moved the prior.
- Missing identity, start value, decisive evidence, or calibration basis
  requires a horizon-specific abstention, not invented percentages. Independent
  research lanes still continue.

## Leverage Contract

Report in USD. For reference capital `C`, underlying return `r`, and 5x linear
exposure, show unlevered `C * r` and approximate gross leveraged `C * 5 * r`.
Financing, spread, slippage, path, overnight gaps, broker margin rules, stop
execution, and forced liquidation can make the realized path worse or close the
position before the horizon. A 20% adverse underlying move is approximately
100% of capital before those effects. Leverage never improves forecast quality.

## Stop Conditions

Stop or limit only the affected conclusion for unresolved identity,
inaccessible decisive evidence, suspected material non-public information,
manipulated sources, unknown required contract terms, or contradictory primary
records. Continue independent lanes and the rest of the batch, preserve the
blocker in `RUN.json`, and expose it in `REPORT.md`.
