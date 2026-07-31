# Source Ledger

Access date for every online source: 2026-08-01.

| Source | Publication or version | Claim used | Limits | Confidence |
|---|---|---|---|---|
| [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) | Updated 2025-04-08 | `data.sec.gov` exposes unauthenticated submissions and XBRL JSON; units remain explicit; bulk files are nightly while APIs update through the day. | Not a price/news source; automated access policy still applies. | High |
| [FRED real-time periods](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html) | Current API documentation | `realtime_start` and `realtime_end` select what was known during a past period instead of silently using today's revision. | Requires a registered API key and series-specific methodology review. | High |
| [FRED vintage dates](https://fred.stlouisfed.org/docs/api/fred/series_vintagedates.html) | Current API documentation | Vintage dates identify releases or revisions that changed a series. | A vintage date alone does not prove release-time availability to the second. | High |
| [CFTC COT overview and FAQ](https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm) | Current page | COT generally reports Tuesday positions on Friday; history is not backdated after publication; inclusion and classifications have material limits. | Weekly, lagged positioning is not a live signal or trader-intent record. | High |
| [CFTC COT explanatory notes](https://www.cftc.gov/MarketReports/CommitmentsofTraders/ExplanatoryNotes/index.htm) | Current page | Defines reportable positions, futures-equivalent options, spreading, category, concentration, and open-interest construction. | Categories can combine hedging and speculation and may change. | High |
| [Federal Reserve SR 26-2](https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm) | 2026-04-17 | Revised risk-based model-risk guidance supersedes SR 11-7 for its stated banking scope. | Supervisory guidance, not a direct requirement for this repository. | High |
| [Revised model-risk guidance](https://www.federalreserve.gov/frrs/guidance/supervisory-guidance-on-model-risk-management.htm) | 2026-04-17 | Supports fit-for-purpose validation, outcome analysis, recalibration, ongoing monitoring, inventory, documentation, and third-party oversight. | Explicitly excludes generative/agentic AI from scope; principles are adopted here as useful controls, not regulatory compliance. | High |
| [NIST Privacy Framework](https://www.nist.gov/privacy-framework/privacy-framework) | Version 1.0, 2020; page updated 2024-01-22 | Provides a voluntary risk-management framework and current pointer to data-governance work. | Does not establish the governing law or a lawful basis for a real client. | High |
| [CME mark-to-market](https://www.cmegroup.com/education/courses/introduction-to-futures/mark-to-market) | Current education page | Futures have exchange settlement, daily P&L/margin effects, and contract-specific settlement methods. | Exact contract specifications and broker margin terms remain mandatory. | High |

## Contradictions And Unknowns

- No single free official source covers exchange-grade real-time quotes and
  comprehensive licensed news for every instrument in `SYMBOLS.md`.
- COT's public history is useful for point-in-time positioning, but the reported
  date and publication date are different and classifications are imperfect.
- Privacy and brokerage duties vary by jurisdiction and capacity; the general
  governance skill must stop for current primary-rule research and qualified
  review rather than encode one jurisdiction as universal.
