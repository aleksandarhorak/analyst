# Evidence Ledger Template

## Scope

- Decision or claim:
- Entity/instrument and identifier:
- Jurisdiction, market, currency:
- Decision-time cutoff and horizon:

## Ledger

| ID | Claim | Classification | Primary source | Event time | Published/revised | Accessed | As-of/vintage | Units/currency | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Classifications: reported fact, derived fact, estimate, scenario, or opinion.

## Evidence Packets

| Ledger ID | Packet ID | Raw SHA-256 | Adapter/version | Instrument ID | Quality | Source locator |
| --- | --- | --- | --- | --- | --- | --- |

Recompute the packet ID before use. Map every packet observation to one ledger
claim; record but do not merge contradictory observations.

## Reconciliation

- Formula and inputs:
- Period and fiscal-calendar mapping:
- Currency and unit conversion:
- Share count, dilution, and corporate actions:
- Restatement or revision treatment:

## Contradictions And Gaps

| Issue | Sources affected | Decision impact | Resolution or limitation |
| --- | --- | --- | --- |

## Red Flags

- The source post-dates the decision cutoff or lacks a release time.
- A normalized vendor field cannot be traced to its original record.
- An evidence packet hash fails, has `quality.status=fail`, is partial, contains
  a credential, or identifies a different instrument.
- A revised series is substituted for the first release.
- Units, signs, currencies, periods, or identifiers do not match.
- A promotional, anonymous, or synthetic claim lacks corroboration.
- The conclusion depends on unavailable or possibly non-public information.

## Conclusion

- Supported claims:
- Unsupported or disputed claims:
- Confidence:
- What evidence would change the assessment:
