# {{SYMBOL}} — Latest Research

<!-- analyst-template: latest-v3 -->

> Initialized from `SYMBOLS.md`; no full-depth research batch has been
> completed. A finalized draft must replace every `not_started` lane.

## Instrument And Batch

- Watchlist instrument: {{INSTRUMENT}}
- Asset class: {{ASSET_CLASS}}
- Watchlist description: {{DESCRIPTION}}
- Exact venue/product: Unresolved
- Reporting currency: USD
- Batch ID / decision cutoff: —
- Research depth contract: full-depth-v1
- Batch checkpoint: —

## Machine-Readable Research State

```json
{
  "schema_version": "symbol-research-state-v1",
  "symbol": "{{SYMBOL}}",
  "asset_class": "{{ASSET_CLASS}}",
  "batch_id": null,
  "decision_cutoff": null,
  "access_completed_at": null,
  "reporting_currency": "USD",
  "identity_status": "unresolved",
  "research_status": "not_started",
  "exact_instrument": null,
  "batch_checkpoint": null,
  "lanes": {
    "identity_evidence": {"status": "not_started", "evidence_ids": [], "summary": null, "reason_code": null, "next_action": null},
    "price_market": {"status": "not_started", "evidence_ids": [], "summary": null, "reason_code": null, "next_action": null},
    "fundamentals_product": {"status": "not_started", "evidence_ids": [], "summary": null, "reason_code": null, "next_action": null},
    "valuation_scenarios": {"status": "not_started", "evidence_ids": [], "summary": null, "reason_code": null, "next_action": null},
    "news_catalysts": {"status": "not_started", "evidence_ids": [], "summary": null, "reason_code": null, "next_action": null},
    "macro_transmission": {"status": "not_started", "evidence_ids": [], "summary": null, "reason_code": null, "next_action": null},
    "market_behavior": {"status": "not_started", "evidence_ids": [], "summary": null, "reason_code": null, "next_action": null},
    "investment_thesis": {"status": "not_started", "evidence_ids": [], "summary": null, "reason_code": null, "next_action": null},
    "directional_forecast": {"status": "not_started", "evidence_ids": [], "summary": null, "reason_code": null, "next_action": null},
    "downside_leverage": {"status": "not_started", "evidence_ids": [], "summary": null, "reason_code": null, "next_action": null},
    "monitoring": {"status": "not_started", "evidence_ids": [], "summary": null, "reason_code": null, "next_action": null}
  },
  "evidence": [],
  "price_observation": {
    "status": "not_started",
    "native_value": null,
    "native_currency": null,
    "units": null,
    "observed_at": null,
    "market_session": null,
    "price_policy": null,
    "usd_value": null,
    "price_evidence_id": null,
    "fx_evidence_id": null,
    "fx_rate_usd_per_native_unit": null,
    "fx_observed_at": null,
    "reason_code": null
  },
  "analysis_depth": {
    "fundamentals_product": {
      "analysis_type": null,
      "equity": null,
      "commodity_future": null,
      "other_product": null
    },
    "valuation_scenarios": {
      "methods": [],
      "scenarios": {"base": null, "bull": null, "bear": null},
      "enterprise_to_equity": null,
      "sensitivities": []
    },
    "news_catalysts": {"window_start": null, "window_end": null, "expectation_basis": null},
    "macro_transmission": {"shared_evidence_ids": [], "channels": [], "instrument_effect": null},
    "market_behavior": {"observations": [], "alternatives": [], "falsifier": null},
    "investment_thesis": {"decision_status": null, "variant_view": null, "market_implied_view": null, "catalysts": [], "contrary_case": null, "disconfirmers": [], "invalidation": null},
    "monitoring": {"signals": [], "next_review": null}
  },
  "forecasts": [],
  "risk": {"status": "not_started", "reference_capital_usd": null, "underlying_downside_return": null, "unlevered_pnl_usd": null, "gross_5x_pnl_usd": null, "liquidity_status": null, "costs_summary": null, "margin_liquidation_summary": null, "reason_code": null},
  "unblockers": []
}
```

## Research Depth Ledger

| Lane | Status | Evidence/work completed | Blocker or next action |
|---|---|---|---|
| Identity and point-in-time evidence | Not started | — | Resolve exact instrument and sources. |
| Price and market data | Not started | — | Acquire a cutoff-eligible value. |
| Fundamentals or product analysis | Not started | — | Complete the asset-specific analysis. |
| Valuation and scenarios | Not started | — | Build economically linked cases. |
| News and catalysts | Not started | — | Search and verify the selected window. |
| Macro transmission | Not started | — | Map the shared regime to this instrument. |
| Market behavior | Not started | — | Test observable participant evidence. |
| Investment thesis | Not started | — | Synthesize the complete impersonal view. |
| Directional forecast | Not started | — | Register or justify each abstention. |
| Downside and 5x risk | Not started | — | Quantify or document the exact blocker. |
| Monitoring | Not started | — | Define disconfirmers and next review. |

## Price And Evidence

| Item | Value | Timestamp | Source/status |
|---|---:|---|---|
| Native price/value | — | — | Not researched |
| USD price/value | — | — | Not researched |
| Market session / delay | — | — | Not researched |

### Evidence Ledger

Not researched. Final v3 evidence entries must identify source, URL or packet,
scope, event/publication/access times, cutoff eligibility, and supported claim.

## Fundamentals Or Product Analysis

Not researched. Reconcile company statements and economic drivers, or complete
the exact asset-specific product, physical, curve, settlement, and roll work.

## Valuation And Scenarios

Not researched. Use economically linked base/bull/bear cases and suitable
valuation lenses or an asset-appropriate scenario sensitivity.

## News And Catalysts

Not researched. Record the search window, verified chronology, prior
expectation, novelty, materiality, transmission, and observed response.

## Macro Transmission

Not researched. Link the shared regime evidence to instrument-specific cash
flows, demand, discount rate, financing, currency, or physical balance.

## Market Behavior

Not researched. Use observable participant- and horizon-specific evidence,
alternatives, and a falsifier; do not infer psychology from price alone.

## Investment Thesis

- Decision status: Observe / not researched
- Variant and market-implied views: —
- Base, bull, and bear outcomes: —
- Catalysts and strongest contrary case: —
- Disconfirmers and invalidation: —

## Directional Probabilities

`—` means a justified abstention, not 0%. Populated `up/flat/down` rows total
100% and require registered forecast IDs.

| Horizon | Start | Flat band | Up | Flat | Down | Calibration / forecast ID | Confidence |
|---|---:|---:|---:|---:|---:|---|---|
| 1 trading day | — | — | — | — | — | Insufficient evidence | Insufficient |
| 2 weeks | — | — | — | — | — | Insufficient evidence | Insufficient |
| 1 month | — | — | — | — | — | Insufficient evidence | Insufficient |
| 2 months | — | — | — | — | — | Insufficient evidence | Insufficient |

## Downside And 5x Exposure

- Reference capital: — USD
- Unlevered downside: —
- Approximate 5x gross linear downside before costs: —
- Liquidity, financing, spread, slippage, path, gap, margin-call, and forced-
  liquidation effects: Not researched; 5x does not improve forecast quality.

## Monitoring

- Confirmation and disconfirmation signals: —
- Catalysts and outcome dates: —
- Next review: —

## Decision

- Status: Observe / not researched
- Thesis and strongest contrary case: —
- Invalidation and next review: —
- Immutable snapshot: —

## Data Lineage

- Evidence packet IDs: —
- Registered forecast IDs: —
- Research depth contract: full-depth-v1
- Batch checkpoint: —
- Template version: 3
