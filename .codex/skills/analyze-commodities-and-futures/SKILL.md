---
name: analyze-commodities-and-futures
description: Analyze commodity spot, futures, funds, and broker derivatives through exact product specifications, physical supply/demand, inventories, term structure, basis, seasonality, positioning, margin, settlement, roll, and delivery risk. Use for metals, energy, agriculture, commodity aliases such as GOLD/CRUDOIL/SILVER/ARABICA, or index/financial futures where a generic symbol can hide contract mechanics.
---

# Analyze Commodities And Futures

## Preconditions

Resolve the exposure before analysis: spot reference, deliverable future and
month, continuous series construction, fund, option, swap, or broker CFD; venue,
contract code, multiplier, tick, quote unit/currency, trading/session calendar,
expiry, settlement, delivery, margin, roll, and broker mapping. If any term that
can change P&L or liquidation is unknown, limit the conclusion.

Read [the commodity and contract template](references/commodity-futures-analysis.md).
Use `acquire-point-in-time-financial-data` and `verify-financial-evidence` for
prices, settlements, inventories, macro data, positioning, and specifications.

## Procedure

1. State decision cutoff, horizon, exact product, native unit/currency, exposure
   direction, and whether the series is traded, official settlement, indicative,
   adjusted continuous, or total return.
2. Build the physical balance: production/capacity, consumption, trade flows,
   inventories and location/quality, outages, logistics, substitution, policy,
   and the marginal source of supply and demand. Separate stocks from flows.
3. Map timing and seasonality: crop/maintenance/heating/driving cycles, weather,
   storage constraints, reporting lags, revisions, and calendar effects. Do not
   turn a normal seasonal pattern into a surprise.
4. Analyze curve and basis: spot/nearby/deferred prices, contango/backwardation,
   calendar spreads, carry/storage/financing, convenience yield, location and
   quality basis, roll method, roll yield, and convergence/expiry behavior.
5. Analyze macro and cross-market transmission: real yields, USD and producer
   currencies, rates, growth, inflation, freight, energy inputs, geopolitics,
   substitutes, and relevant equity/credit signals. State competing mechanisms.
6. Use CFTC positioning only with report date, release time, category/reporting
   limits, open-interest denominator, changes in classification, and alternatives.
   Weekly aggregate positions do not reveal current intent or cause price moves.
7. Separate observed attention/flow/volume evidence from stories about trader
   psychology. Use `analyze-market-behavior` for participant-specific claims.
8. Build base/bull/bear paths with physical and financial triggers, curve/roll
   effects, disconfirmers, and exact horizon. Register any directional
   probabilities with `calibrate-financial-forecasts`.
9. Stress gap, limit, halt, liquidity, basis, roll, delivery, margin, financing,
   FX, broker close-out, and daily mark-to-market paths. Use
   `manage-portfolio-risk`; never apply a generic 5x multiplier without the
   broker's exact product and liquidation rules.

## Product-Specific Routing

- `GOLD` and `SILVER`: distinguish physical/spot/forward, COMEX future, fund,
  mining equity, and CFD; verify troy-ounce units and monetary versus physical
  demand.
- `CRUDOIL`: distinguish WTI/Brent, grade/location, cash/future/CFD, month and
  roll; storage and delivery constraints can dominate nearby pricing.
- `ARABICA`: distinguish ICE Coffee C from other coffee grades/products; model
  crop year, origins, deliverability, weather, inventories, freight, and producer
  currencies.
- `US100`, `SP500`, and `DJI30`: if using futures, identify the actual contract,
  multiplier and maturity rather than treating a cash index or CFD as identical.

## Output

Provide identity/specification ledger, physical balance, curve/basis table,
seasonality and catalyst calendar, positioning with lag, scenarios and
probabilities/confidence, roll/total-return bridge, leverage/margin stress,
disconfirmers, invalidation, evidence gaps, and next review.

## Stop Conditions

Stop or abstain for unresolved product/contract, unknown broker specification,
ambiguous unit or settlement, inaccessible decisive physical data, suspected
manipulation or non-public information, or a delivery/margin path the analysis
cannot bound.
