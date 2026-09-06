# Consent

**Publish your impact without publishing your people.**

A small charity's proof of impact is made of other people's private lives — so the
proof never gets published. Consent turns a messy private casework file into two
things a charity can actually hand over: a **publishable impact brief** and a
**de-identified dataset**.

The rule that shapes everything: **the raw record never leaves the warehouse.**

*Submission for [Weekend Challenge: Generosity Edition](https://dev.to/challenges/weekend-2026-09-03).*

## The boundary, in three layers

| Layer | Mechanism | Requires |
|---|---|---|
| **A** | Role grants — the app has no `SELECT` on the private tables | nothing |
| **B** | Masking policy — the engine returns different truths per role | Enterprise Edition |
| **C** | Cortex AISQL — 6 functions do the reading so no human has to | Cortex entitlement |

Layer A is the thesis and cannot fail. B and C are upgrades.

## Run it

```bash
cp .env.example .env      # fill in your Snowflake details
./scripts/run.sh
```

Then, in a Snowflake worksheet, in order:

```
sql/00_gate.sql          # RUN FIRST — proves what your account can actually do
sql/10_leg_a_grants.sql  # tables + the grant that IS the thesis
sql/20_leg_b_masking.sql # Enterprise Edition only
sql/30_leg_c_cortex.sql  # the six Cortex functions
sql/redact_fallback.sql  # no-Cortex path; keep it whatever the gate said
```

## Capability grid

<!-- Fill from sql/00_gate.sql. Do not fake a ✅. -->

| Capability | Verdict |
|---|---|
| Layer A grants | |
| Layer B masking policy | |
| `AI_AGG` | |
| `AI_REDACT` | |
| `AI_CLASSIFY` / `AI_FILTER` | |
| `AI_EXTRACT` | |
| `AI_PARSE_DOCUMENT` | |

## Honest scope

- **The data is synthetic.** All 60 cases in `data/synthetic_cases.csv` are fabricated.
  Demoing a privacy tool on real casework would be its own answer to this challenge,
  and the wrong one.
- **This is not a compliance tool.** Redaction here is a first pass that makes human
  review tractable. It is not a GDPR or HIPAA guarantee and no such claim is made.

## Commits after the deadline

<!-- Contest rule: any commit made after 2026-09-07 06:59 UTC must be noted here. -->
None.

## Licence

Apache-2.0. See `LICENSE`.
