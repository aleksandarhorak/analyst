# Financial Data Provider Setup

This repository supports official SEC, FRED/ALFRED, and CFTC acquisition plus a
strict executable boundary for a separately licensed price/news provider. It
does not include vendor credentials, entitlements, a licensed feed, or a broker
product catalogue.

## Source Configuration

| Source | Runtime configuration | Notes |
| --- | --- | --- |
| SEC EDGAR | `FINANCIAL_DATA_USER_AGENT` | Descriptive organization/contact; not a secret |
| FRED/ALFRED | `FRED_API_KEY` | Secret; keep in an approved runtime store |
| CFTC public reporting | None currently | Still subject to source availability and usage terms |
| Licensed price/news | Adapter-defined names | Pass only explicitly approved names with `--provider-env` |

Never put credentials in Git, repository `.env` files, command arguments,
packets, fixtures, prompts, screenshots, or logs. The licensed adapter owns its
provider-specific secret-store integration. The repository deliberately defines
no generic vendor key name.

## Provider Trust Boundary

The adapter must implement the
[`provider-request-v1` / `provider-response-v1` contract](../.codex/skills/acquire-point-in-time-financial-data/references/provider-contract.md).
It is invoked directly without a shell. The first command element must be an
absolute executable path.

The repository sends one JSON request on standard input and accepts one JSON
response on standard output. It passes a minimal environment plus only variable
names explicitly listed with `--provider-env`. Stdout and stderr are capped
while reading; nonzero stderr is represented by a hash rather than copied into
the error.

The response must match the registry identity, request ID, currency, session,
freshness, adjustment, cutoff, exact schema, provenance, and rights contract.
Price, news, issuer, index, fund, future, share class, and broker products are
never equated by ticker similarity.

## Authorization Checklist

Before running a live preflight, establish:

- organization and user entitlement for every requested field and market;
- internal-analysis, storage, derived-data, and redistribution rights;
- permitted retention location and lifetime;
- stable provider instrument identifiers and an approved mapping to the
  repository registry;
- real-time versus delayed status, exchange entitlements, session semantics,
  corporate-action adjustment, and correction/retraction behavior;
- an approved executable path and owner;
- runtime secret injection, rotation, access control, audit logging, and
  deletion outside the repository;
- a provider timeout and incident/escalation contact.

If the license forbids storage of normalized observations, stop. The current
`evidence-packet-v1` stores normalized observations; a separately governed
external-store or hash-only contract must be implemented before onboarding that
provider.

## Offline Regression

Run the complete synthetic adapter suite first:

```bash
python3 scripts/test-financial-data.py
```

This exercises official-source fixtures, exact identity, units, revisions,
provider process input/output, environment isolation, timeout, stderr secrecy,
schema rejection, price freshness, news identity/timing, future timestamps, and
failed-write behavior. Passing fixtures are not evidence that a live vendor is
licensed, reachable, or correct.

## Live Adapter Preflight

Set vendor secrets only through an approved runtime mechanism. The following
names and executable are placeholders; do not copy them literally:

```bash
export APPROVED_VENDOR_TOKEN='supplied-by-approved-secret-store'

python3 scripts/preflight-provider.py \
  --registry-key AAPL \
  --provider-env APPROVED_VENDOR_TOKEN \
  --command /absolute/approved/path/provider-adapter
```

`--command` must be last because all remaining arguments belong to the adapter.
Do not use `sh -c`, `bash -c`, `eval`, a relative executable, or a command
string. Use additional `--provider-env NAME` entries only for variables the
adapter genuinely needs.

By default, preflight requests both price and news for one resolved instrument,
validates the resulting packets, prints only safe packet metadata, and removes
its temporary directory. It does not save the licensed observations in the
repository. Use `--kind price` or `--kind news` for an adapter with narrower
authorized scope.

Preflight proves contract compatibility at one instant. It does not prove
coverage completeness, market entitlement, historical correctness, latency
service levels, or production fitness.

## Manual Single-Packet Check

Only after authorization and preflight, acquire into an approved restrictive
directory outside Git. Replace every placeholder from verified registry and
cutoff facts:

```bash
python3 .codex/skills/acquire-point-in-time-financial-data/scripts/acquire_financial_data.py \
  provider \
  --registry-key AAPL \
  --instrument-id sec:cik:0000320193:AAPL \
  --symbol AAPL \
  --asset-class equity \
  --venue XNAS \
  --decision-cutoff 2026-08-01T12:00:00Z \
  --request-id approved-price-aapl-20260801T120000Z \
  --kind price \
  --currency USD \
  --session regular \
  --maximum-age-seconds 60 \
  --output /approved/restrictive/non-git-directory/aapl-price.json \
  --provider-env APPROVED_VENDOR_TOKEN \
  --command /absolute/approved/path/provider-adapter
```

Validate independently:

```bash
python3 .codex/skills/acquire-point-in-time-financial-data/scripts/acquire_financial_data.py \
  validate /approved/restrictive/non-git-directory/aapl-price.json \
  --registry-key AAPL
```

Inspect identity, quality, timestamps, latency, adjustment, currency, session,
rights, and observation count. Do not print the payload into chat or logs. Retain
or delete it according to the verified license and evidence policy.

## Failure Diagnosis

| Failure | Meaning and action |
| --- | --- |
| Absolute executable required | Replace a shell, relative path, or PATH lookup with an approved absolute executable |
| Allowed environment variable unset | Inject it through the approved runtime store or remove the unnecessary allowlist entry |
| Process timeout/output limit | Treat the adapter as unavailable; investigate without exposing payload or secrets |
| Stderr hash on nonzero exit | Use the provider's protected operational logs; do not request raw stderr in repository output |
| Identity mismatch | Repair the provider catalogue mapping; never override by ticker similarity |
| Partial/errors/nonempty error list | Mark the evidence unavailable; do not use partial observations |
| Wrong currency/session/latency/adjustment | Request the exact product semantics or abstain |
| Stale/future timestamp | Correct the request or provider clock/data mapping; do not move the cutoff |
| News document/update/correction failure | Acquire a canonical document record, not a snippet |
| Unsupported field | Update and review the versioned contract before accepting a schema change |
| Rights incomplete or storage prohibited | Stop onboarding and obtain qualified licensing/data-governance review |
| Failed output missing | Expected: rejected packets are validated before writing and leave no usable output |

## Production Acceptance

A qualified owner should sign off only after:

- fixture tests and price/news preflight pass;
- provider-specific stable IDs reconcile through an authorized catalogue;
- entitlement, license, retention, and redistribution controls are documented;
- secrets are proven absent from child environments except explicit allowlist,
  packets, errors, and repository scans;
- stale, future, partial, malformed, corrected, and retracted cases fail safely;
- operational monitoring covers timeouts, schema drift, coverage, latency, and
  provider incidents;
- sample packets reconcile independently to provider/exchange records;
- the downstream workflow continues with `insufficient evidence` during outage.

No provider is currently certified merely because this runbook and preflight
exist.
