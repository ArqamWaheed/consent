# memory.md — Consent brain
> Read this first every task. Update it last. Keep it terse to save tokens.

## What this is
Snowflake-native pipeline: a charity's messy private casework file -> a publishable
impact brief + a de-identified dataset. **The raw record never leaves the warehouse.**

## Stack
Snowflake (Enterprise Edition), Cortex AISQL, Streamlit, snowflake-connector-python, Apache-2.0

## Status snapshot
- Phase: Hour 0 complete (scaffold). 
- Last task: repo bootstrapped, SQL legs + app skeleton written, synthetic data generated.
- Next: **HOUR-1 ENTITLEMENT GATE** — run `sql/00_gate.sql`, fill the verdict grid below.

## The three legs (architecture rule)
The thesis rests on Leg A, which cannot fail. B and C are upgrades.
- **Leg A** — role grants; app has no SELECT on private tables. Needs nothing. ALWAYS WORKS.
- **Leg B** — masking policy; engine returns different truths per role. Needs **Enterprise Edition**.
- **Leg C** — Cortex AISQL (6 functions). Needs BOTH Cortex grants + region.

## Gate verdicts  <-- FILL THIS IN HOUR 1, BEFORE WRITING FEATURE CODE
| Capability | Verdict | Fallback if ✗ |
|---|---|---|
| Leg A grants | | — |
| Leg B masking policy | | Standard Edition -> Leg A carries the boundary |
| AI_AGG (least gated) | | if this fails, all Cortex is off |
| AI_REDACT | | `sql/redact_fallback.sql` (regex, still in-warehouse) |
| AI_CLASSIFY / AI_FILTER | | CASE over keywords |
| AI_EXTRACT | | REGEXP_SUBSTR |
| AI_PARSE_DOCUMENT | | parse PDF client-side, land text in VARCHAR |

## Key decisions (why)
- All processing is SQL in-warehouse — the thesis is "the data doesn't move".
- Cortex needs TWO grants: `USE AI FUNCTIONS` (default PUBLIC) AND `SNOWFLAKE.CORTEX_USER`
  (NOT default, needs ACCOUNTADMIN). Half-satisfying this presents as "locked on trial".
- Enterprise Edition + AWS Oregon/N.Virginia chosen at signup — both irreversible.
- Synthetic data only. Demoing a privacy tool on real casework would be the wrong answer.

## Open questions / TODO
- Which legs survived the gate?
- Live Streamlit URL once deployed.

## File map (only what matters)
- `sql/00_gate.sql`        — Hour-1 probes. RUN FIRST.
- `sql/10_leg_a_grants.sql`— tables + the grant that IS the thesis
- `sql/20_leg_b_masking.sql`— masking policy (Enterprise only)
- `sql/30_leg_c_cortex.sql`— the 6 Cortex functions
- `sql/redact_fallback.sql`— regex redaction, no Cortex needed
- `app/streamlit_app.py`   — split screen + /status honesty panel
- `data/synthetic_cases.csv` — 60 fabricated cases
