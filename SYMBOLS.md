# Daily Symbol Watchlist

This file is the agent's maintained research universe. Read it at the start of
recurring market, company, portfolio, or trading analysis and update it only
with an explicit as-of timestamp and evidence. Inclusion is not a recommendation
to buy, and `Observe` means that no favorable investment conclusion has been
made.

Last universe review: `2026-07-31T23:30:47+01:00`.

## Status Definitions

- `Observe`: monitor; no completed favorable thesis.
- `Research`: active evidence gathering, fundamental analysis, or valuation.
- `Investment candidate`: evidence supports further consideration at a stated
  price, horizon, and risk level; not personalized advice.
- `Hold/owned`: use only when verified portfolio data confirms ownership and
  the position remains supported.
- `Avoid`: current evidence indicates an unfavorable or unsuitable setup.
- `Archived`: removed from the active universe; retain the reason and date.

## Daily Maintenance Rules

1. On `do symbols research`, use `research-symbol-watchlist` for every active
   row and update root `REPORT.md`; no active symbol may be omitted silently.
2. Verify the exact instrument, venue, currency, price timestamp, and relevant
   corporate actions before analysis.
3. Use `verify-financial-evidence` before relying on current prices, filings,
   releases, news, estimates, or macroeconomic data.
4. Use the relevant company, valuation, macro, news, market-behavior, portfolio,
   suitability, and execution skills before changing a status.
   For commodities or any futures-based index exposure, also use
   `analyze-commodities-and-futures` and preserve the exact contract/product,
   settlement, curve, roll, margin, and delivery terms.
5. Write an immutable batch snapshot under
   `research/symbols/<SYMBOL>/history/`, update `LATEST.md`, and append the
   decision to `DECISIONS.md`. Never delete the folder when a symbol is archived.
6. Record each material decision in the analysis log. Include the horizon,
   confidence, thesis, valuation or entry conditions, risks, invalidation, and
   next review.
7. Use 1 trading day, 2 weeks, 1 month, and 2 months as the standard horizons.
   For each, state a flat band and up/flat/down probabilities totaling 100%, or
   use `insufficient evidence` with no fabricated percentages.
8. Report in USD and keep unlevered risk separate from approximate 5x gross
   linear exposure before financing, spread, slippage, gaps, margin calls, and
   liquidation.
9. Add a symbol only with a research reason. Move removed symbols to the archive
   and change log rather than deleting their history.
10. Platform aliases are not universal tickers. Resolve them to the exact
   security, futures contract, fund, index, cash product, or CFD before using
   market data or planning execution.

## Active Universe

| Symbol | Instrument or issuer | Asset class | What it represents | Status |
| --- | --- | --- | --- | --- |
| `AAPL` | Apple Inc. | Stock | Consumer devices, services, and the Apple hardware/software ecosystem. | Observe |
| `NVDA` | NVIDIA Corporation | Stock | Accelerated computing, AI processors, networking, and related software. | Observe |
| `AMZN` | Amazon.com, Inc. | Stock | E-commerce, Amazon Web Services cloud computing, logistics, and advertising. | Observe |
| `MSFT` | Microsoft Corporation | Stock | Enterprise software, Azure cloud infrastructure, productivity tools, gaming, and AI. | Observe |
| `META` | Meta Platforms, Inc. | Stock | Social platforms and digital advertising, with additional AI and immersive-technology investment. | Observe |
| `GOOG` | Alphabet Inc. Class C | Stock | Google search and advertising, YouTube, cloud computing, Android, and technology investments. | Observe |
| `TSLA` | Tesla, Inc. | Stock | Electric vehicles, energy generation and storage, charging, software, and automation initiatives. | Observe |
| `AMD` | Advanced Micro Devices, Inc. | Stock | CPUs, GPUs, data-center accelerators, embedded processors, and semiconductor design. | Observe |
| `NFLX` | Netflix, Inc. | Stock | Global streaming entertainment, including series, films, games, live programming, and advertising. | Observe |
| `PLTR` | Palantir Technologies Inc. | Stock | Data integration, analytics, and AI software for government and commercial customers. | Observe |
| `AVGO` | Broadcom Inc. | Stock | Semiconductors, networking components, and infrastructure software. | Observe |
| `INTC` | Intel Corporation | Stock | CPUs, data-center products, semiconductor manufacturing, and foundry services. | Observe |
| `MU` | Micron Technology, Inc. | Stock | Memory and storage semiconductors, principally DRAM and NAND. | Observe |
| `SMCI` | Super Micro Computer, Inc. | Stock | Server, storage, and rack-scale computing systems, including AI data-center infrastructure. | Observe |
| `COIN` | Coinbase Global, Inc. | Stock | Cryptocurrency trading, custody, staking, subscriptions, and digital-asset infrastructure. | Observe |
| `MSTR` | Strategy Inc | Stock | Bitcoin-treasury exposure combined with enterprise analytics software and capital-markets activity. | Observe |
| `UBER` | Uber Technologies, Inc. | Stock | Mobility, delivery, freight, and logistics marketplace services. | Observe |
| `SOFI` | SoFi Technologies, Inc. | Stock | Digital lending, banking, brokerage, and financial-technology platform services. | Observe |
| `JPM` | JPMorgan Chase & Co. | Stock | Diversified banking, payments, markets, asset management, and consumer finance. | Observe |
| `BAC` | Bank of America Corporation | Stock | Consumer and commercial banking, wealth management, payments, and capital markets. | Observe |
| `WMT` | Walmart Inc. | Stock | Large-scale retail, grocery, membership clubs, logistics, advertising, and e-commerce. | Observe |
| `XOM` | ExxonMobil Holdings Corp | Stock | NYSE-listed ExxonMobil holding-company exposure to integrated oil, natural gas, refining, chemicals, and lower-carbon investments. | Observe |
| `CVX` | Chevron Corporation | Stock | Integrated oil and gas production, refining, chemicals, and energy projects. | Observe |
| `DIS` | The Walt Disney Company | Stock | Entertainment studios, streaming, television, sports media, parks, resorts, and consumer products. | Observe |
| `BA` | The Boeing Company | Stock | Commercial aircraft, defense, space, and aviation services. | Observe |
| `F` | Ford Motor Company | Stock | Passenger and commercial vehicles, financing, electric vehicles, and automotive services. | Observe |
| `GM` | General Motors Company | Stock | Passenger and commercial vehicles, financing, electric vehicles, software, and mobility initiatives. | Observe |
| `NKE` | NIKE, Inc. | Stock | Athletic footwear, apparel, equipment, brands, and direct-to-consumer retail. | Observe |
| `PFE` | Pfizer Inc. | Stock | Biopharmaceutical research, medicines, vaccines, and related healthcare products. | Observe |
| `ORCL` | Oracle Corporation | Stock | Database software, enterprise applications, and cloud infrastructure and services. | Observe |
| `BABA` | Alibaba Group Holding Limited ADR | Stock/ADR | Chinese and international e-commerce, cloud computing, logistics, and digital services. | Observe |
| `GOLD` | Gold commodity alias | Commodity | Gold exposure driven by real yields, currencies, central-bank and investment demand, and physical supply; not automatically NYSE ticker `GOLD`. | Observe |
| `CRUDOIL` | Crude-oil platform alias | Commodity | Generic crude-oil exposure; resolve whether the intended benchmark is WTI, Brent, a futures contract, fund, or cash/CFD product. | Observe |
| `SILVER` | Silver commodity alias | Commodity | Precious and industrial metal exposure influenced by real yields, currencies, investment demand, mining supply, and industrial use. | Observe |
| `ARABICA` | Arabica coffee platform alias | Commodity | Coffee exposure affected by weather, crop cycles, inventories, producer currencies, logistics, and futures positioning. | Observe |
| `US100` | Nasdaq-100 platform alias | Equity index | Large non-financial companies listed on Nasdaq; resolve the exact index, future, fund, or CFD. | Observe |
| `SP500` | S&P 500 platform alias | Equity index | Broad large-cap U.S. equity exposure; resolve the exact index, future, fund, or CFD. | Observe |
| `DJI30` | Dow Jones Industrial Average platform alias | Equity index | Price-weighted index of 30 large U.S. companies; resolve the exact index, future, fund, or CFD. | Observe |

`NFLX` is the normalized Netflix ticker; the originally supplied `NFXL` was a
transposition. Confirm any future symbol correction against a primary issuer or
exchange source.

## Current Analysis And Decisions

One row per active decision. `High in insufficiency` is confidence in the stop
condition, not confidence about market direction.

| Symbol | Status | As of | Horizon | Confidence | Thesis and valuation/entry conditions | Key risks and invalidation | Next review |
|---|---|---|---|---|---|---|---|
| `AAPL` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and an official public event was reviewed; no validated price, expectation/response series or calibrated valuation supports direction. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `NVDA` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and an official public event was reviewed; no validated price, expectation/response series or calibrated valuation supports direction. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `AMZN` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and an official public event was reviewed; no validated price, expectation/response series or calibrated valuation supports direction. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `MSFT` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and an official public event was reviewed; no validated price, expectation/response series or calibrated valuation supports direction. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `META` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and an official public event was reviewed; no validated price, expectation/response series or calibrated valuation supports direction. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `GOOG` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and official sources were searched; no current operating catalyst or validated price/calibrated directional view was established. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `TSLA` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and an official public event was reviewed; no validated price, expectation/response series or calibrated valuation supports direction. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `AMD` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and an official public event was reviewed; no validated price, expectation/response series or calibrated valuation supports direction. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `NFLX` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and an official public event was reviewed; no validated price, expectation/response series or calibrated valuation supports direction. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `PLTR` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and official sources were searched; no current operating catalyst or validated price/calibrated directional view was established. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `AVGO` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and an official public event was reviewed; no validated price, expectation/response series or calibrated valuation supports direction. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `INTC` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and an official public event was reviewed; no validated price, expectation/response series or calibrated valuation supports direction. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `MU` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and an official public event was reviewed; no validated price, expectation/response series or calibrated valuation supports direction. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `SMCI` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and an official public event was reviewed; no validated price, expectation/response series or calibrated valuation supports direction. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `COIN` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and official event metadata was found, but the decisive document and validated price/response evidence were unavailable. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `MSTR` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and an official public event was reviewed; no validated price, expectation/response series or calibrated valuation supports direction. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `UBER` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and an official public event was reviewed; no validated price, expectation/response series or calibrated valuation supports direction. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `SOFI` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and official event metadata was found, but the decisive document and validated price/response evidence were unavailable. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `JPM` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and an official public event was reviewed; no validated price, expectation/response series or calibrated valuation supports direction. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `BAC` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and an official public event was reviewed; no validated price, expectation/response series or calibrated valuation supports direction. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `WMT` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and an official public event was reviewed; no validated price, expectation/response series or calibrated valuation supports direction. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `XOM` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and an official public event was reviewed; no validated price, expectation/response series or calibrated valuation supports direction. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `CVX` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and official event metadata was found, but the decisive document and validated price/response evidence were unavailable. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `DIS` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and official sources were searched; no current operating catalyst or validated price/calibrated directional view was established. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `BA` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and an official public event was reviewed; no validated price, expectation/response series or calibrated valuation supports direction. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `F` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and official event metadata was found, but the decisive document and validated price/response evidence were unavailable. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `GM` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and an official public event was reviewed; no validated price, expectation/response series or calibrated valuation supports direction. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `NKE` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and an official public event was reviewed; no validated price, expectation/response series or calibrated valuation supports direction. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `PFE` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and an official public event was reviewed; no validated price, expectation/response series or calibrated valuation supports direction. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `ORCL` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and an official public event was reviewed; no validated price, expectation/response series or calibrated valuation supports direction. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `BABA` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity verified and official sources were searched; no current operating catalyst or validated price/calibrated directional view was established. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `GOLD` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity unresolved; official product comparisons confirm that the alias can map to materially different exposures, so no price or direction is attached. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `CRUDOIL` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity unresolved; official product comparisons confirm that the alias can map to materially different exposures, so no price or direction is attached. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `SILVER` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity unresolved; official product comparisons confirm that the alias can map to materially different exposures, so no price or direction is attached. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `ARABICA` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity unresolved; official product comparisons confirm that the alias can map to materially different exposures, so no price or direction is attached. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `US100` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity unresolved; official product comparisons confirm that the alias can map to materially different exposures, so no price or direction is attached. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `SP500` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity unresolved; official product comparisons confirm that the alias can map to materially different exposures, so no price or direction is attached. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |
| `DJI30` | Observe | `2026-08-01T02:36:54Z` | 1 day to 2 months | High in insufficiency | Identity unresolved; official product comparisons confirm that the alias can map to materially different exposures, so no price or direction is attached. | Missing or contradictory price, product, filing, valuation or response evidence could reverse any view. | 2026-08-08 or data resolution |

## Analysis And Status Change Log

Use an ISO 8601 timestamp with timezone. Record additions, removals, ticker
changes, and material status or thesis changes.

| Timestamp | Symbol | Change | Evidence and rationale | Analyst/agent | Next action |
| --- | --- | --- | --- | --- | --- |
| 2026-07-31T23:30:47+01:00 | All | Watchlist initialized | Initial user-specified research universe; every symbol starts as `Observe`. | Agent | Verify and analyze before changing status. |
| 2026-08-01T00:50:51Z | All | Completed evidence-bounded batch `2026-08-01T004949Z` | 38/38 covered; 31 identities verified, 7 aliases unresolved, 0 usable current price/news packets, and 0 published probabilities. | Agent | Resolve exact products and connect authorized evidence before directional analysis. |
| 2026-08-01T00:55:00Z | XOM | Updated issuer identity | Current SEC ticker/exchange file maps XOM to CIK `0002115436`, ExxonMobil Holdings Corp, on NYSE; the immutable batch snapshot preserves the preceding watchlist label and shows the reconciled exact identity. | Agent | Recheck corporate-action and predecessor/successor treatment before financial comparison. |
| 2026-08-01T02:43:26Z | All | Completed official-source batch `2026-08-01T023654Z` | 38/38 covered; 31 registered securities searched, 7 aliases remained unresolved, 0 validated price packets and 0 published probabilities. | Agent plus three read-only evidence lanes | Connect authorized price/news evidence, resolve products and complete valuation/response analysis. |

## Archived Symbols

| Symbol | Instrument | Archived at | Previous status | Reason | Re-entry condition |
| --- | --- | --- | --- | --- | --- |
| — | — | — | — | No archived symbols. | — |
