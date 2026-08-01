---
name: check-broker-suitability
description: Gate a personalized investment or trading recommendation on jurisdiction, professional capacity, client profile, product understanding, alternatives, costs, conflicts, and series-of-transactions risk. Use before client-specific recommendations or broker-support conclusions; require current primary rules and qualified review.
---

# Check Broker Suitability

## Boundary

This is a conservative analytical gate, not legal advice or proof of compliance.
Determine current rules for the actual jurisdiction, capacity, firm, client,
product, and facts from primary sources. Escalate conclusions to licensed legal
or compliance reviewers.

## Procedure

1. Establish jurisdiction, professional capacity, client type, account, product,
   and applicable current rule set. Record the as-of date.
2. Before receiving or persisting real client facts, use `govern-client-data` to
   establish purpose/authority, minimization, approved secure system, roles,
   provider/region, retention/deletion, correction, and incident controls. Never
   store real client facts in this repository, symbol/forecast memory, fixtures,
   prompts copied to files, logs, or Git history.
3. Gather only the decision-necessary age range, dependants, employment and
   income, assets, debts, tax status,
   objectives, horizon, liquidity needs, experience, knowledge, risk tolerance,
   risk capacity, existing holdings, concentration, and other constraints in the
   approved client system. Reference them by redacted profile ID and verified
   date rather than repeating sensitive values.
4. Never infer missing client facts. If material information is absent, ask or
   restrict the output to impersonal education and research.
5. Understand product mechanics, downside, leverage, liquidity, complexity,
   fees, financing, tax effects, conflicts, exit, and performance across adverse
   scenarios.
6. Compare cash and reasonably available alternatives on risk, reward, cost,
   complexity, liquidity, and client fit.
7. Test the single transaction and the resulting series of transactions for
   concentration, turnover, excessive cost, and inconsistency with objectives.
8. Identify compensation, inventory, banking, research, affiliate, data,
   referral, and personal conflicts. State mitigations; disclosure alone does
   not cure a poor recommendation.
9. Record rationale, rejected alternatives, missing facts, reviewer, and expiry
   or refresh conditions.

Use [the suitability-gate template](references/suitability-gate.md).

## Outcomes

Return one of: proceed to qualified review, revise, insufficient information,
or do not recommend. Never state that an output is suitable, in a client's best
interest, or compliant solely because this checklist was completed.

## Mandatory Stops

Stop for failed client-data governance, missing material profile facts,
inability to understand the product,
unresolved authority, prohibited or manipulative conduct, suspected material
non-public information, sanctions restrictions, or a conflict that cannot be
controlled.
