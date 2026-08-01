# Reviewed Document Manifest

These are primary operational documents, not an academic-paper survey. Each
listed web document was read in full on 2026-08-01 for the claims recorded
below. No copyrighted full text is redistributed in the repository.

## D1: EDGAR Application Programming Interfaces

- **Author:** U.S. Securities and Exchange Commission
- **Version:** page reviewed/updated 2025-04-08
- **Source:** https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- **Method:** Full official API page review.
- **Finding:** Use submissions/companyfacts JSON with explicit CIK, taxonomy,
  concept, unit, filing, and access metadata; retain raw response hashes.
- **Limitation:** SEC access policy and issuer-specific XBRL contexts still need
  enforcement and reconciliation.
- **Full text reviewed:** yes (HTML page)

## D2: FRED API Real-Time Periods And Vintage Dates

- **Author:** Federal Reserve Bank of St. Louis
- **Version:** current API documentation at cutoff
- **Sources:** https://fred.stlouisfed.org/docs/api/fred/realtime_period.html and
  https://fred.stlouisfed.org/docs/api/fred/series_vintagedates.html
- **Method:** Full official documentation-page review.
- **Finding:** Historical analysis must request an explicit real-time period and
  preserve revision/vintage metadata.
- **Limitation:** A registered key is required and series methodology differs.
- **Full text reviewed:** yes (HTML pages)

## D3: Commitments Of Traders Overview And Explanatory Notes

- **Author:** U.S. Commodity Futures Trading Commission
- **Version:** current pages at cutoff
- **Sources:** https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm
  and https://www.cftc.gov/MarketReports/CommitmentsofTraders/ExplanatoryNotes/index.htm
- **Method:** Full official documentation-page review.
- **Finding:** Preserve both Tuesday report date and Friday publication/access
  time; treat categories, reportability, and options-equivalent data as limited.
- **Limitation:** Weekly aggregated positions cannot establish current trader
  intent or causality.
- **Full text reviewed:** yes (HTML pages)

## D4: Revised Guidance On Model Risk Management

- **Authors:** Federal Reserve, OCC, and FDIC
- **Version:** SR 26-2, 2026-04-17
- **Source:** https://www.federalreserve.gov/frrs/guidance/supervisory-guidance-on-model-risk-management.htm
- **Method:** Full official HTML guidance review, including scope footnotes.
- **Finding:** Adopt risk-based validation, outcome analysis, monitoring,
  documentation, inventory, effective challenge, and vendor oversight.
- **Limitation:** The guidance says generative and agentic AI are outside its
  scope; these are voluntary engineering controls here, not compliance claims.
- **Full text reviewed:** yes (HTML guidance)

## D5: NIST Privacy Framework Landing Guidance

- **Author:** National Institute of Standards and Technology
- **Version:** Privacy Framework 1.0 page, updated 2024-01-22
- **Source:** https://www.nist.gov/privacy-framework/privacy-framework
- **Method:** Full official landing-page review and version-status check.
- **Finding:** Use risk-based privacy governance while requiring the actual
  jurisdiction, purpose, authority, minimization, and lifecycle controls.
- **Limitation:** The landing page and voluntary framework are not legal advice.
- **Full text reviewed:** yes (HTML page; framework PDF not relied on)

## D6: CME Mark-To-Market

- **Author:** CME Group
- **Version:** current education page at cutoff
- **Source:** https://www.cmegroup.com/education/courses/introduction-to-futures/mark-to-market
- **Method:** Full official education-page review.
- **Finding:** Separate traded, close, and official settlement values and model
  daily variation margin and liquidation risk from exact contract terms.
- **Limitation:** Product rulebooks and broker terms control each actual trade.
- **Full text reviewed:** yes (HTML page)
