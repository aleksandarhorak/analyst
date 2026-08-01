---
name: govern-client-data
description: Gate the collection, use, storage, transmission, retention, correction, and deletion of real client identity, financial profile, portfolio, account, tax, suitability, or communications data. Use before personalized broker-support work handles client facts, before connecting a client system or provider, or when creating fixtures, logs, research memory, reports, or exports that could expose personal or confidential information.
---

# Govern Client Data

## Repository Prohibition

Never store real client data in this repository, Git history, `MEMORY.md`,
`TODO.md`, symbol research, forecast/evaluation fixtures, prompts copied into
files, logs, screenshots, test failures, commits, or generated artifacts. Do not
repeat identifiers in analysis when a redacted profile ID or aggregate fact is
enough. Use synthetic data for all repository tests.

This skill is risk-management guidance, not a universal legal basis or privacy
compliance determination. Research current primary rules for the actual
jurisdiction, capacity, data subjects, purpose, and transfers; require qualified
privacy, legal, security, and compliance review.

Read [the client-data gate](references/client-data-gate.md) before collection or
integration.

## Procedure

1. Identify controller/processor roles, jurisdiction, regulated capacity, data
   subjects, purpose, decision, current rule source, and qualified owner.
2. Establish and document an authorized basis before collection. Consent is not
   assumed, universal, irrevocable, or always the correct basis.
3. Minimize fields and precision to what the suitability or service purpose
   actually needs. Separate required, optional, derived, disputed, and missing
   facts. Do not collect credentials, account access tokens, or full identity
   documents through this repository workflow.
4. Classify sensitivity and source; show the client how to correct relevant
   inaccuracies. Do not infer protected traits or missing financial capacity.
5. Use only an approved access-controlled system with encryption in transit and
   at rest, least privilege, authentication, audit logging, backup policy, and
   segregated development/test environments. Store a redacted reference ID in
   analytical output, not the raw record.
6. Define purpose-limited recipients, providers, regions/transfers,
   redistribution restrictions, retention/expiry, deletion, correction,
   portability, legal hold, and incident response before transmission.
7. Filter prompts, tool calls, exports, logs, evaluations, and citations for
   unnecessary client data. Confirm external model/data-provider terms and
   approved deployment boundaries before sending any client fact.
8. At expiry or withdrawal where applicable, execute the approved deletion or
   restriction process and retain only the authorized audit evidence.

## Integration Rules

- Before `check-broker-suitability` collects real facts, pass this gate and use
  the approved client system. The suitability output references verified facts
  by redacted ID/source date and contains only decision-necessary detail.
- `research-symbol-watchlist`, symbol history, forecast ledgers, and general
  investment research remain client-free and impersonal.
- Evaluation fixtures use invented entities labeled synthetic. Never transform
  a real case by changing only the name; combinations of facts can re-identify.
- If the user supplies client data in chat, do not copy it into repository
  artifacts. Minimize repetition and explain the secure channel/system needed
  for any persistent workflow.

## Stop Conditions

Stop collection, storage, or transmission for unknown authority or purpose,
missing secure system, excessive fields, unclear provider/region, unresolved
retention/deletion, suspected breach, unauthorized access, client request that
cannot be honored, or any request to commit real client facts to this repository.

## Output

Return pass/revise/stop, redacted data inventory, purpose and authority, field
minimization, approved system/roles, recipients/transfers, retention/deletion,
client rights/correction path, incident escalation, reviewer, expiry, and
unresolved risks. Do not output the underlying sensitive values.
