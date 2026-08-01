# Financial Data Adapter Fixtures

Synthetic fixtures exercise registry-bound SEC issuer identity and unit
selection, ALFRED revision intervals, CFTC report/publication separation, and
the licensed-provider boundary. Provider cases cover complete identity,
freshness, requested currency/session, and explicit adjustment semantics.
Process cases also cover minimal environment inheritance, explicit variable
allowlisting, absolute executables, timeout, hashed stderr, exact response
schemas, validate-before-write, independent cutoff timestamps, and complete
news document/update/correction fields. Malformed-packet, ambiguous cutoff-day,
and secret-leak cases exercise the dependency-free validator. Fixtures contain
no credentials, licensed payloads, or client facts. Run
`python3 scripts/test-financial-data.py`; live endpoint availability is
intentionally not a repository gate. Use `scripts/preflight-provider.py` only
after authorization; a preflight pass is contract evidence, not licensing or
production certification.
