# Consent

**Publish your impact without publishing your people.**

A small charity's proof of impact is made of other people's private lives, so the
proof never gets published. Consent turns a messy private casework file into two
things a charity can actually hand over: a **publishable impact brief** and a
**de-identified dataset**.

The rule that shapes everything: **the raw record never leaves the warehouse.**

*Submission for [Weekend Challenge: Generosity Edition](https://dev.to/challenges/weekend-2026-09-03).*

---

## The boundary, in three layers

| Layer | Mechanism | Requires | Status here |
|---|---|---|---|
| **A** | Role grants — the app has no `SELECT` on the private table | nothing | **shipped** |
| **B** | Masking policy — the engine returns different truths per role | Enterprise Edition | **not available** |
| **C** | Cortex AISQL — the model reads the notes so no human has to | Cortex entitlement | **shipped, rebuilt** |

Layer A is the thesis and cannot fail. B and C are upgrades. This account got one of them.

---

## What the account actually allowed

Every verdict below was recorded **after** granting both halves of the Cortex gate
([privileges and model access](https://docs.snowflake.com/en/user-guide/snowflake-cortex/aisql-privileges-and-access)):

```sql
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE SYSADMIN;  -- not granted by default
GRANT USE AI FUNCTIONS ON ACCOUNT TO ROLE SYSADMIN;          -- default: PUBLIC
ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'ANY_REGION';
```

So none of these failures is a missing grant.

| Capability | Verdict | What the account said |
|---|---|---|
| Layer A role grants | ✅ | — |
| Layer B masking policy | ❌ | `Unsupported feature 'MASKING POLICY'.` |
| `AI_AGG` | ✅ | — |
| `AI_SUMMARIZE_AGG` | ✅ | — |
| `AI_REDACT` | ❌ | `AI function _AI_REDACT is not available for trial accounts.` |
| `AI_CLASSIFY` | ❌ | `AI function AI_CLASSIFY is not available for trial accounts.` |
| `AI_FILTER` | ❌ | `AI function _AI_FILTER_WITH_PROMPT is not available for trial accounts.` |
| `AI_EXTRACT` | ❌ | `AI function _AI_EXTRACT is not available for trial accounts.` |
| `AI_COMPLETE` | ❌ | `AI function _COMPLETE_WITH_PROMPT_HISTORY_LLM is not available for trial accounts.` |
| `SNOWFLAKE.CORTEX.SENTIMENT` | ❌ | `AI function SENTIMENT is not available for trial accounts.` |

**The two survivors are exactly the two functions the docs exempt from needing the
`CORTEX_USER` role.** The trial restriction and the role restriction draw the same
line, which makes the docs predictive: if a function is listed as needing
`CORTEX_USER`, expect a trial account to refuse it.

---

## The bug that would have shipped

The boundary test is one query, and the first time it ran for real it **returned the
private note**:

```sql
USE ROLE CONSENT_APP;
SELECT CURRENT_ROLE();                              -- CONSENT_APP
SELECT raw_note FROM CONSENT.APP.RAW_CASES LIMIT 1; -- ...the note. In full.
```

`USE ROLE` sets your *primary* role. It drops nothing. Every other role the user
holds stays active as a **secondary role**, and authorization considers those too:

```sql
SELECT CURRENT_SECONDARY_ROLES();
-- {"roles":"ACCOUNTADMIN,ORGADMIN","value":"ALL"}
```

One statement fixes it, and the same query is then refused:

```sql
USE SECONDARY ROLES NONE;
SELECT raw_note FROM CONSENT.APP.RAW_CASES LIMIT 1;
-- SQL compilation error: Object 'CONSENT.APP.RAW_CASES' does not exist or not authorized.
```

The app issues `USE SECONDARY ROLES NONE` on connect (`app/warehouse.py`) and prints
`CURRENT_SECONDARY_ROLES()` in the status panel, so you can check it rather than
trust it. **Without that line the grant boundary is decorative** — and it looks
completely correct from the outside, because `CURRENT_ROLE()` says exactly what you
expect.

---

## The trick that saved Layer C

`AI_AGG` is an aggregate. Group by a unique key and every group holds one row, which
turns an aggregate into a **per-row LLM transform**. One call then does the work of
three gated functions and returns them together:

```sql
SELECT case_id,
       AI_AGG(raw_note,
              'Return ONLY a JSON object with "redacted" (the note with every name '
           || 'replaced by [NAME], phone by [PHONE], email by [EMAIL], address by '
           || '[ADDRESS], reference by [REF]), "need" (food|housing|health|legal), '
           || '"unresolved" (true|false).') AS payload
FROM RAW_CASES
GROUP BY case_id;
```

`AI_REDACT` + `AI_CLASSIFY` + `AI_FILTER`, rebuilt out of the one function a trial
account is allowed to call, still running inside the warehouse.

`sql/35_redact_fallback.sql` is the zero-Cortex path — regex plus a name roster — and
it ships too. It is cruder, and that is the honest framing: rules a reader can audit
line by line, versus a model that generalises.

---

## Run it

```bash
cp .env.example .env      # optional — without it the app runs in snapshot mode
./scripts/run.sh
```

Then, in a Snowflake worksheet, in order:

```
sql/00_gate.sql           # RUN FIRST, one statement at a time. Probes, not a script.
sql/10_leg_a_grants.sql   # tables, roles, and the grant that IS the thesis
sql/15_load_synthetic.sql # 60 fabricated rows
sql/30_leg_c_cortex.sql   # the AI_AGG per-row transform      (or 35_ for no Cortex)
sql/40_brief.sql          # AI_AGG writes the impact brief    (or 45_ for no Cortex)
sql/20_leg_b_masking.sql  # Enterprise Edition only. Fails here, on purpose, in public.
```

**Two modes.** With `SNOWFLAKE_*` credentials the app queries the warehouse live as
role `CONSENT_APP`. Without them it renders the committed snapshot of `SAFE_CASES` —
the only part of the pipeline that was ever allowed to leave — and says so on screen
in a yellow banner. It never dresses one up as the other.

---

## Interesting files

- `sql/10_leg_a_grants.sql` — the six grants the app gets, the one it does not, and
  the secondary-roles trap written out in full.
- `sql/30_leg_c_cortex.sql` — the `AI_AGG` per-row transform.
- `app/warehouse.py` — the whole live/snapshot decision, in one module.
- `data/safe_cases_snapshot.csv` — the published output, checked in.

---

## Honest scope

- **The data is synthetic.** All 60 cases in `data/synthetic_cases.csv` are fabricated.
  Demoing a privacy tool on real casework would be its own answer to this challenge,
  and the wrong one.
- **This is not a compliance tool.** Redaction here is a first pass that makes human
  review tractable. It is not a GDPR or HIPAA guarantee and no such claim is made.
- **Layer B never ran.** The account is Standard Edition, and edition is fixed at
  signup. The file is kept, unrun, because deleting the thing you could not have is
  how a capability grid becomes a lie.

## Commits after the deadline

<!-- Contest rule: any commit made after 2026-09-07 06:59 UTC must be noted here. -->
None.

## Licence

Apache-2.0. See `LICENSE`.
