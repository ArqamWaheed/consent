# memory.md — Consent brain
> Read this first every task. Update it last. Keep it terse to save tokens.

## What this is
Snowflake-native pipeline: a charity's messy private casework file -> a publishable
impact brief + a de-identified dataset. **The raw record never leaves the warehouse.**

## Stack
Snowflake (Standard Edition trial), Cortex AISQL, Streamlit, snowflake-connector-python,
Apache-2.0.

## The account (verified 2026-09-06)
`jjyikad-tgb35242` · account `POB69176` · region `AWS_US_WEST_2` · version `10.31.103`
· user `GAMMATIX` · **Standard Edition** (not Enterprise — see Leg B verdict).

## GATE VERDICTS — observed, not assumed
Both halves of the Cortex gate were granted first (`SNOWFLAKE.CORTEX_USER` to SYSADMIN
**and** `USE AI FUNCTIONS ON ACCOUNT`), and cross-region was set to `ANY_REGION`.
Every verdict below was taken *after* that, so none of them is a missing-grant artefact.

| Capability | Verdict | Verbatim error |
|---|---|---|
| Leg A role grants | PASS | — |
| Leg B masking policy | **FAIL** | `Unsupported feature 'MASKING POLICY'.` |
| `AI_AGG` | **PASS** | — (2.9s) |
| `AI_SUMMARIZE_AGG` | **PASS** | — (0.8s) |
| `AI_REDACT` | FAIL | `AI function _AI_REDACT is not available for trial accounts.` |
| `AI_CLASSIFY` | FAIL | `AI function AI_CLASSIFY is not available for trial accounts.` |
| `AI_FILTER` | FAIL | `AI function _AI_FILTER_WITH_PROMPT is not available for trial accounts.` |
| `AI_EXTRACT` | FAIL | `AI function _AI_EXTRACT is not available for trial accounts.` |
| `AI_COMPLETE` | FAIL | `AI function _COMPLETE_WITH_PROMPT_HISTORY_LLM is not available for trial accounts.` |
| `SNOWFLAKE.CORTEX.SENTIMENT` | FAIL | `AI function SENTIMENT is not available for trial accounts.` |

## THE CENTRAL FINDING (this is the post)
1. **The trial gate is real and is not the grant gate.** Both Cortex grants were in
   place and nine functions still refused. Two prior builders reported "Cortex locked on
   trial" without publishing the error; this repo publishes it verbatim.
2. **The two survivors are exactly the two the docs exempt from `CORTEX_USER`:**
   `AI_AGG` and `AI_SUMMARIZE_AGG`. The trial restriction and the role restriction draw
   the *same* line. That is predictive, not coincidental.
3. **`AI_AGG` + `GROUP BY <unique key>` is a per-row LLM transform.** An aggregate over
   groups of one. Verified: one `AI_AGG` call returns clean JSON with the redacted note,
   the need category, and the unresolved flag — i.e. `AI_REDACT` + `AI_CLASSIFY` +
   `AI_FILTER` rebuilt from the one function a trial account is allowed to call.
   ~1.5s/row. **This is what ships as Leg C.**

## The three legs (architecture rule)
The thesis rests on Leg A, which cannot fail. B and C are upgrades.
- **Leg A** — role grants; app has no SELECT on private tables. SHIPPED.
- **Leg B** — masking policy. **NOT AVAILABLE** (Standard Edition). Leg A carries the
  boundary alone. Do not claim Leg B anywhere. Keep `sql/20_leg_b_masking.sql` in the
  repo as the documented upgrade path, clearly labelled unavailable here.
- **Leg C** — Cortex, via the `AI_AGG` per-row transform above, plus `AI_AGG` for the
  brief. `sql/35_redact_fallback.sql` is the zero-Cortex path and still ships.

## Key decisions (why)
- All processing is SQL in-warehouse — the thesis is "the data doesn't move".
- Cortex needs TWO grants: `USE AI FUNCTIONS` (default PUBLIC) AND `SNOWFLAKE.CORTEX_USER`
  (NOT default). Granting both is necessary and, on a trial, not sufficient.
- `PRIVATE_ROW_COUNT` is a view, so it runs with owner's rights: the app learns *how many*
  private rows exist without ever being able to read one. The boundary is sized, not binary.
- Synthetic data only. Demoing a privacy tool on real casework would be the wrong answer.
- `SAFE_CASES.method` records `cortex` or `regex` so the app never has to claim which ran.

## Credential boundary (important, non-obvious)
This environment's safety layer **blocks** creating Snowflake service credentials,
non-interactive authentication, and creating a public GitHub repo. Consequences:
- All SQL is run by hand in the Snowsight worksheet (`consent_bootstrap.sql` in
  My Workspace). It works; it is just manual.
- The Streamlit app must run **dual-mode**: live warehouse when `SNOWFLAKE_*` env vars
  exist, and a clearly-labelled snapshot of `SAFE_CASES` otherwise. Never fake live mode.
- Publishing the repo and the post are left as explicit one-step actions for the owner.

## Open questions / TODO
- `AI_PARSE_DOCUMENT` not yet probed (expect FAIL; needs a staged file). Not load-bearing.
- Live Streamlit URL once deployed.

## File map (only what matters)
- `sql/00_gate.sql`          — Hour-1 probes. RUN FIRST, one statement at a time.
- `sql/10_leg_a_grants.sql`  — tables + the grant that IS the thesis
- `sql/15_load_synthetic.sql`— 60 rows as plain INSERTs
- `sql/20_leg_b_masking.sql` — masking policy. UNAVAILABLE on this account.
- `sql/30_leg_c_cortex.sql`  — the AI_AGG per-row transform
- `sql/35_redact_fallback.sql`— regex + roster redaction, no Cortex needed
- `sql/40_brief.sql`         — AI_AGG writes the impact brief
- `app/streamlit_app.py`     — split screen + status honesty panel
