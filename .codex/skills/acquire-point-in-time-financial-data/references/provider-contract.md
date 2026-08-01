# Price And News Provider Contract

## Process Interface

Invoke a provider adapter as an executable without a shell. Send one JSON object
on standard input and require one JSON object on standard output. Credentials
stay in the adapter's environment or secret store. Standard error may contain
diagnostics but must not contain credentials, client data, or licensed payloads.
The executable path must be absolute. The repository passes only a minimal safe
environment plus names explicitly allowlisted with `--provider-env`; it never
passes the whole parent environment.

Request:

```json
{
  "schema_version": "provider-request-v1",
  "request_id": "stable-id",
  "kind": "price",
  "decision_cutoff": "2026-08-01T12:00:00Z",
  "instrument": {
    "id": "sec:cik:0000320193:AAPL",
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
    "id": "sec:cik:0000320193:AAPL",
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
      "adjustment": "unadjusted",
      "source_locator": "trade:opaque-id"
    }
  ],
  "errors": []
}
```

## Required Semantics

- `complete=false`, a nonempty `errors` array, request-ID mismatch, or any ID,
  symbol, venue, or asset-class mismatch is a hard failure. The response is also
  reconciled to the repository instrument registry.
- Every observation needs field, value, unit, classification, event time,
  publication time, as-of time, and source locator. Price observations also need
  currency, session, latency (`real_time`, `delayed`, `prior_close`,
  `settlement`, or `indicative`), and adjustment state. Currency and session
  must match the request. `as_of` must be no later than the decision cutoff and
  no older than `maximum_age_seconds`.
- Corporate-action adjustment state must be explicit for every price, including
  an explicit `unadjusted` value where applicable.
- A `news` request needs original publisher, HTTPS canonical URL,
  publication/update times, headline, stable document identity, and a correction
  state of `original`, `corrected`, or `retracted`. Publication age must be no
  greater than the request's `maximum_age_seconds`. A search snippet is not an
  observation.
- The provider name and rights note are mandatory. Store only what the license
  permits. The current packet schema retains normalized observations; a provider
  whose license prohibits that storage must not be onboarded until a governed
  external-store or hash-only contract exists.
- Top-level and observation objects use exact schemas; unexpected fields fail.
  The caller independently validates event, publication, update, and as-of times
  against the cutoff, enforces freshness, caps both stdout and stderr while
  reading, and never retries a non-idempotent request. Acquisition retries use
  bounded exponential backoff.
- Production onboarding must reconcile any provider-specific instrument ID
  through the adapter's authorized catalogue to the repository registry. The
  repository does not infer vendor identity from ticker similarity.
