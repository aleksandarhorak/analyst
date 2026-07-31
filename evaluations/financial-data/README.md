# Financial Data Adapter Fixtures

Synthetic fixtures exercise SEC unit selection, ALFRED revision intervals, CFTC
report/publication separation, and the licensed-provider boundary. They contain
no credentials, licensed payloads, or client facts. The deterministic test is
`python3 scripts/test-financial-data.py`; live endpoint availability is not a
repository gate.
