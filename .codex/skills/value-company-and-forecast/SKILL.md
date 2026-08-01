---
name: value-company-and-forecast
description: Build economically linked company forecasts, base/bull/bear scenarios, sensitivities, and defensible valuation ranges. Use for discounted cash flow, reverse valuation, comparables, sum-of-parts, target-range, or forecast work after the evidence and fundamental drivers are understood.
---

# Value Company And Forecast

## Preconditions

Confirm security, share class, currency, fiscal calendar, as-of price and time,
horizon, capital structure, and fundamental drivers. Use point-in-time inputs
and distinguish company guidance, consensus, analyst estimates, and scenarios.

## Procedure

1. Select forecast drivers tied to volumes, prices, unit economics, margins,
   working capital, reinvestment, taxes, and financing.
2. Select the appropriate branch in [sector models](references/sector-models.md)
   for banks/lenders, insurers, semiconductors/hardware, SaaS/software,
   energy/resources, or cyclicals. Use several branches for a sum of parts.
3. Reconcile the opening historical period and forecast statements. Explain
   every material normalization.
4. Build base, bull, and bear cases with coherent paths, explicit triggers, and
   probabilities only when defensible.
5. Choose valuation methods suited to the business and capital structure. Use
   at least two informative lenses when possible.
6. For discounted cash flow, expose cash-flow definition, discount rate,
   terminal method, and terminal-value share. For comparables, normalize peer,
   accounting, growth, and cycle differences.
7. Bridge enterprise to equity value with net debt, leases, pensions,
   minorities, associates, options, convertibles, dilution, and non-operating
   assets as applicable.
8. Run sensitivities and reverse-engineer what the current price implies.
9. Compare value with price after risk, time, dilution, tax, liquidity, and
   execution costs; define invalidation and monitoring.
10. When publishing directional probabilities, preregister the exact cutoff,
    band, horizon, method version, and evidence packet IDs with
    `calibrate-financial-forecasts` before the outcome.

Use [the valuation template](references/valuation-model.md).

## Rules

- Report a conditional range, not a guaranteed target.
- Avoid false precision and circular assumptions.
- Do not use a discount rate, multiple, or terminal growth rate without a
  stated basis and sensitivity.
- Separate model error from business uncertainty and market-price uncertainty.

## Output

Provide the driver forecast, scenario table, method-specific values, valuation
range, implied expectations, sensitivities, key risks, disconfirmers,
invalidation conditions, confidence, and unresolved data gaps.
