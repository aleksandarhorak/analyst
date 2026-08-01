---
name: manage-portfolio-risk
description: Evaluate portfolio fit, size exposures, and stress concentration, factors, correlation, leverage, liquidity, drawdown, and exit risk. Use for position sizing, portfolio construction, rebalance analysis, hedging, risk budgeting, scenario tests, or assessing whether a good thesis belongs in a mandate.
---

# Manage Portfolio Risk

## Preconditions

Establish objectives, benchmark, horizon, liquidity needs, permissible assets,
risk budget, leverage and concentration limits, tax or currency constraints,
current holdings, reliable positions, and prices. Use `check-broker-suitability`
when the analysis becomes a personalized recommendation. Before real client
positions or constraints are handled, use `govern-client-data` and keep them in
the approved client system rather than this repository or its artifacts.

## Procedure

1. Verify exposures by issuer, security, sector, geography, currency, duration,
   style, liquidity, counterparty, and look-through holdings.
2. Define thesis-failure loss and gap scenarios before sizing expected upside.
3. Measure marginal and total concentration, factor contribution, correlation,
   beta, volatility, drawdown, leverage, financing, and liquidity risk using
   multiple windows and stated assumptions.
4. Stress historical and hypothetical regimes, correlation convergence,
   volatility spikes, funding pressure, market closure, borrow recall, foreign-
   exchange moves, and forced liquidation.
5. Compare proposed exposure with cash and reasonably available alternatives.
6. Estimate turnover, tax, transaction cost, market impact, capacity, and time
   to exit under normal and stressed volume.
7. Recommend a range or constraint-aware alternatives; define rebalance,
   monitoring, and invalidation rules.

Use [the portfolio-risk template](references/portfolio-risk.md).

## Rules

- Do not infer risk capacity from stated risk tolerance.
- Do not rely on one covariance window or one statistical risk number.
- Treat hedges as positions with basis, liquidity, counterparty, carry, and
  path risk.
- Respect hard mandate and liquidity constraints before model optimization.

## Output

Provide objectives and constraints, exposure map, risk contributions,
stress-loss distribution, liquidity and cost assessment, sizing range or
alternatives, safeguards, monitoring triggers, and unresolved data limitations.
