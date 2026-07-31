---
name: plan-trade-execution
description: Design or review a cost-aware trade-execution plan using liquidity, spread, depth, volatility, impact, adverse selection, and transaction-cost analysis. Use for order strategy, venue or timing choices, implementation shortfall, capacity, execution review, or exit planning; never for autonomous order submission.
---

# Plan Trade Execution

## Boundary

This skill analyzes implementation. It does not place, route, cancel, or modify
orders and does not establish trading authority. Keep thesis, portfolio sizing,
and execution as separate decisions.

## Inputs

Require instrument and venue, side, size, currency, urgency, decision price and
time, constraints, participation or completion goal, risk limits, and expected
exit. Mark unknown client, mandate, borrow, or compliance facts.

## Procedure

1. Verify session, tick size, lot size, auction, halt, settlement, short-sale,
   borrow, price-band, and venue constraints from current primary sources.
2. Measure normal and stressed spread, depth, volume curve, volatility,
   resilience, order-flow imbalance, queue or fill risk, and fragmentation.
3. Estimate commissions, spread, impact, delay, fees or rebates, financing or
   borrow, foreign exchange, tax, opportunity cost, and liquidation cost.
4. Choose a decision benchmark and evaluate urgency versus impact and adverse
   selection. Compare simple feasible alternatives.
5. Define order-style logic, participation or pacing limits, pause/cancel
   conditions, auction handling, maximum cost, and contingency paths without
   transmitting an order.
6. Assess capacity and the full exit, not only entry.
7. Specify transaction-cost analysis using decision, arrival, execution, and
   close prices with explainable decomposition.

Use [the execution-plan template](references/execution-plan.md).

## Rules

- Historical average volume is not guaranteed executable liquidity.
- Price impact is state-dependent; show uncertainty and stress cases.
- Fees or rebates never replace a best-execution or client-interest analysis.
- Stop for suspected manipulation, confidential-order misuse, sanctions risk,
  missing authority, or possibly material non-public information.

## Output

Provide assumptions, market-state evidence, alternatives, cost range, chosen
analysis-only plan, safeguards, capacity and exit assessment, and a transaction-
cost review design.
