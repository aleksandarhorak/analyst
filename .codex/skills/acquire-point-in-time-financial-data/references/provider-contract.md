# Price And News Provider Contract

## Process Interface

Invoke a provider adapter as an executable without a shell. Send one JSON object
on standard input and require one JSON object on standard output. Credentials
stay in the adapter's environment or secret store. Standard error may contain
diagnostics but must not contain credentials, client data, or licensed payloads.

Request:

```json
{
  "schema_version": "provider-request-v1",
  "request_id": "stable-id",
  "kind": "price-or-news",
  "decision_cutoff": "2026-08-01T12:00:00Z",
  "instrument": {
    "id": "provider:venue:security-id",
    "symbol": "AAPL",
    "venue": "XNAS",
    "asset_class": "equity"
  },
  "requirements": {
    "currency": "USD",
    "session": "regular",
    "maximum_age_seconds": 60
  }
}
```

Response:

```json
{
  "schema_version": "provider-response-v1",
  "request_id": "stable-id",
  "provider": "authorized-provider-name",
  "complete": true,
  "instrument": {
    "id": "provider:venue:security-id",
    "symbol": "AAPL",
    "venue": "XNAS",
    "asset_class": "equity"
  },
  "source_url": "https://provider.example/record/opaque-id",
  "rights": "internal analysis; no redistribution",
  "observations": [
    {
      "field": "last_trade",
      "value": 100.25,
      "unit": "USD_per_share",
      "currency": "USD",
      "classification": "reported_fact",
      "event_time": "2026-08-01T11:59:58Z",
      "published_at": "2026-08-01T11:59:58Z",
      "as_of": "2026-08-01T11:59:58Z",
      "session": "regular",
      "latency": "real_time",
      "source_locator": "trade:opaque-id"
    }
  ],
  "errors": []
}
```

## Required Semantics

- `complete=false`, a nonempty `errors` array, request-ID mismatch, or instrument
  mismatch is a hard failure.
- Every observation needs field, value, unit, classification, event time,
  publication time, as-of time, and source locator. Price observations also need
  currency, session, and latency (`real_time`, `delayed`, `prior_close`,
  `settlement`, or `indicative`).
- Corporate-action adjustment state must be explicit for historical prices.
- News needs original publisher, canonical URL, publication/update times,
  headline/document identity, and correction/retraction state. A search snippet
  is not an observation.
- The provider name and rights note are mandatory. Store only what the license
  permits; the evidence packet may retain a hash when payload retention is not
  allowed.
- The caller enforces timeout and output-size limits and never retries a
  non-idempotent request. Acquisition retries use bounded exponential backoff.
