*This is a submission for [Weekend Challenge: Generosity Edition](https://dev.to/challenges/weekend-2026-09-03)*

> **TL;DR** — A charity's proof of impact is made of other people's private lives, so it never gets published. Consent keeps the raw notes inside Snowflake and lets only a redacted dataset and a written brief out. Two things went wrong: the trial account refused nine of the eleven AI functions I designed around, and the boundary I built to protect the data didn't work. Both are in the post, with the error strings.

---

## What I Built

A friend runs a three-person charity. Last year a funder asked them to prove their work mattered. They had the proof, two years of it, in one spreadsheet. They never sent it.

Every row had someone's name, phone number and address in it, given in confidence on the worst week of that person's life.

So the honest answer was "we can't show you that," and the funder heard "they don't have it."

The villain here isn't privacy law and it isn't funders. It's a false choice: **protect the people, or prove the work.**

**So I stopped picking. I moved the boundary instead of the data.**

**Consent** turns a charity's messy private records into two things it can actually hand over: a **publishable impact brief**, and a **de-identified dataset** a funder or a researcher can be given.

The rule that shapes everything: **the raw record never leaves the warehouse.** Redaction, triage and the written summary all happen as SQL inside Snowflake, where the data already lives. Only the redacted side crosses the boundary — including to the app you're looking at.

That isn't a promise in a privacy policy. It's a grant:

```sql
GRANT SELECT ON TABLE CONSENT.APP.SAFE_CASES TO ROLE CONSENT_APP;
-- deliberately NOT granted: RAW_CASES
```

The app literally cannot read the private table. The left panel of the UI shows a row count and nothing else, because a row count is all its role is allowed.

![Split panel: the left half is the RAW_CASES table with case notes blacked out by redaction bars, the right half is SAFE_CASES with the same notes reading NAME, ADDRESS and PHONE placeholders, divided by a vertical line labelled THE WAREHOUSE BOUNDARY](https://dev-to-uploads.s3.us-east-2.amazonaws.com/uploads/articles/wozijt6o0glvzvkpk5xx.jpeg)

*The whole product in one frame. The left half never moves; only the right half is allowed to leave.*

---

## Demo

**Live:** _link goes here once the app is deployed._

A 75-second narrated walkthrough is in the repo at `demo/consent-demo.mp4`.

The **Warehouse status** panel prints the live region, account and role, and probes each Cortex function in front of you. I'd rather show a red light than claim a green one — and on this account, most of them are red.

![Screenshot of the running Consent app: a snapshot-mode banner, a left panel showing 60 private records held and a refused SELECT on RAW_CASES, and a right panel with the AI-written impact brief and a table of redacted notes](https://dev-to-uploads.s3.us-east-2.amazonaws.com/uploads/articles/eya3gi2wk1note9a3wrj.jpeg)

*The refusal is the feature. The app asks for the private note on every page load so you can watch it be told no.*

---

## Code

Repo: **github.com/ArqamWaheed/consent** _(going public with the submission)_

Apache-2.0.

**Interesting files:**

- `sql/10_leg_a_grants.sql` — the six grants the app gets, and the one that was never written.
- `sql/30_leg_c_cortex.sql` — the whole AI pipeline, in one statement.
- `app/warehouse.py` — the entire live-versus-snapshot decision, in one module.
- `data/safe_cases_snapshot.csv` — the published output, committed.

**The data is synthetic.** Sixty fabricated cases in `data/synthetic_cases.csv`. Using real casework to demo a privacy tool would have been its own answer to this challenge, and the wrong one.

---

## How I Built It

The boundary is built in three layers, deliberately in that order, because each one has to stand up if the one above it isn't available. That turned out to matter more than I expected.

**Layer 1 — the app is not allowed to ask.** One grant, quoted above. Works on any Snowflake account, any edition, with every AI feature switched off. This is the whole thesis, and it is one `GRANT` statement away from being true on a free account.

**The count without the contents.** The app still needs to say "60 private records are held here," and it can, because `PRIVATE_ROW_COUNT` is a *view*. A view runs with its owner's rights, so the app learns how many, never who. The boundary is sized, not binary.

```sql
CREATE VIEW PRIVATE_ROW_COUNT AS SELECT COUNT(*) AS private_rows FROM RAW_CASES;
GRANT SELECT ON VIEW PRIVATE_ROW_COUNT TO ROLE CONSENT_APP;
```

**Layer 2 — the engine answers differently depending on who asks.** A masking policy would mean the same `SELECT`, run by a caseworker and by this app, returns two different truths, with no application code in the decision.

**It didn't run.** More on that in a second.

**Layer 3 — Cortex AISQL reads the notes so no human has to.** `AI_REDACT` for the boundary, `AI_CLASSIFY` for triage, `AI_FILTER` as a semantic `WHERE`, `AI_AGG` to write the brief across every row.

That was the plan. Here is what the account actually said.

### The gate

Cortex AI functions need **two** grants, and only one exists by default:

```sql
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE SYSADMIN;  -- not granted by default
GRANT USE AI FUNCTIONS ON ACCOUNT TO ROLE SYSADMIN;          -- default: PUBLIC
```

I granted both, set cross-region inference to `ANY_REGION`, and probed every function before building on it. So nothing below is a missing grant.

| Capability | Verdict | What the account said |
|---|---|---|
| Layer 1 role grants | ✅ | — |
| Layer 2 masking policy | ❌ | `Unsupported feature 'MASKING POLICY'.` |
| `AI_AGG` | ✅ | — |
| `AI_SUMMARIZE_AGG` | ✅ | — |
| `AI_REDACT` | ❌ | `AI function _AI_REDACT is not available for trial accounts.` |
| `AI_CLASSIFY` | ❌ | `AI function AI_CLASSIFY is not available for trial accounts.` |
| `AI_FILTER` | ❌ | `AI function _AI_FILTER_WITH_PROMPT is not available for trial accounts.` |
| `AI_EXTRACT` | ❌ | `AI function _AI_EXTRACT is not available for trial accounts.` |
| `AI_COMPLETE` | ❌ | `AI function _COMPLETE_WITH_PROMPT_HISTORY_LLM is not available for trial accounts.` |
| `SNOWFLAKE.CORTEX.SENTIMENT` | ❌ | `AI function SENTIMENT is not available for trial accounts.` |

Nine of eleven, gone. Including the one the entire design was named after.

![Capability table titled What the account actually allowed, listing AI_AGG and AI_SUMMARIZE_AGG with green checks and AI_REDACT, AI_CLASSIFY, AI_FILTER, AI_EXTRACT, AI_COMPLETE, CORTEX.SENTIMENT and MASKING POLICY with red crosses reading not available for trial accounts](https://dev-to-uploads.s3.us-east-2.amazonaws.com/uploads/articles/syjt2as6a99sz7479cuv.jpeg)

*The grid I did not want to publish. Two of eleven, and the two are not a coincidence.*

**The two survivors are not random.** Snowflake's docs say `AI_AGG` and `AI_SUMMARIZE_AGG` are the two functions that work with `USE AI FUNCTIONS` even *without* the `CORTEX_USER` role. Those are exactly the two that survived the trial gate.

The trial restriction and the role restriction draw the same line. Which makes the docs predictive: if a function is documented as needing `CORTEX_USER`, expect a trial account to refuse it. I have not seen that written down anywhere, and knowing it up front would have changed what I designed.

### Rebuilding three functions out of one

`AI_AGG` is an aggregate. It takes a column and an instruction and reasons across the group.

**So give it groups of one.** `GROUP BY` a unique key and every group holds exactly one row, which turns an aggregate into a per-row LLM transform. And since the instruction is free text, one call can return all three things I lost:

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

`AI_REDACT` plus `AI_CLASSIFY` plus `AI_FILTER`, rebuilt from the one function a trial account is allowed to call, still running inside the warehouse, still never moving a note.

Sixty notes, redacted, classified and triaged in **24 seconds**. All 60 returned parseable JSON. Zero rows held back.

| | |
|---|---|
| Rows in / published | 60 / 60 |
| Cortex time, whole table | 24s |
| Needs found | health 19 · legal 16 · food 13 · housing 12 |
| Still unresolved | 56 of 60 |
| Phone numbers or emails surviving into the published set | 0 |

### The boundary didn't work

Then I ran the test that the entire project rests on. As the app's role, try to read the private table and get refused.

```sql
USE ROLE CONSENT_APP;
SELECT CURRENT_ROLE();                              -- CONSENT_APP
SELECT raw_note FROM CONSENT.APP.RAW_CASES LIMIT 1;
```

It returned the note. In full. Name, address, phone number.

**`USE ROLE` sets your primary role. It drops nothing.** Every other role the user holds stays active as a *secondary* role, and Snowflake authorizes against those too:

```sql
SELECT CURRENT_SECONDARY_ROLES();
-- {"roles":"ACCOUNTADMIN,ORGADMIN","value":"ALL"}
```

My own account was reading through the wall and reporting the correct role while it did it. One statement fixes it:

```sql
USE SECONDARY ROLES NONE;
SELECT raw_note FROM CONSENT.APP.RAW_CASES LIMIT 1;
-- SQL compilation error: Object 'CONSENT.APP.RAW_CASES' does not exist or not authorized.
```

![Two stacked terminal cards labelled BEFORE and AFTER: the first shows the same SELECT returning a case note with a visible name, address and phone, the second shows it refused after USE SECONDARY ROLES NONE](https://dev-to-uploads.s3.us-east-2.amazonaws.com/uploads/articles/ros6w8n3xttp5gvaqet7.jpeg)

*The same query, twice, ten seconds apart. Nothing changed but the session's secondary roles.*

The app now runs `USE SECONDARY ROLES NONE` on connect, and prints `CURRENT_SECONDARY_ROLES()` in the status panel so you can check it instead of trusting me. **A boundary you have not watched refuse something is not a boundary.** It is a diagram.

**Rows that don't parse don't get published.** `TRY_PARSE_JSON` returns null on garbage, and the insert filters those rows out rather than letting a half-redacted note through. A row held back is a row nobody sees. That is the correct failure direction for this tool.

**Why Snowflake specifically, and not an LLM API behind my own server.** If I call an API, the private text leaves the database to be understood, and I have rebuilt the exact problem I set out to solve. Cortex runs the model where the data already is. Remove the warehouse and there is no project.

### What I refused to do

* Do not let the app read the private table "just for the row count." Use a view.
* Do not claim Layer 2 works. It didn't run here, and the file stays in the repo unrun.
* Do not delete the failed functions from the README. A capability grid with no ❌ in it is marketing.
* Do not demo a privacy tool on real casework.
* Do not call this compliant.

**One honest concession**, since this is where a reader should get suspicious: this is a first pass that makes human review tractable, not a compliance guarantee, and I don't claim one. An LLM redactor generalises well and fails silently. The regex fallback in `sql/35_redact_fallback.sql` is cruder and fails loudly. I shipped both and made the app tell you which one produced the rows you're looking at. The point is to turn "nobody can look at this" into "one person can check this in an afternoon."

**A second concession:** the deployed demo runs in snapshot mode unless credentials are configured. The snapshot is not a mock — it is the pipeline's real output, the only part that was ever allowed to leave the warehouse, committed to the repo the same way it would be handed to a funder. The app says which mode it's in, in a banner, every time.

---

## Prize Categories

**Best Use of Snowflake.**

---

## What I Learned

- **The grants were harder than the redaction.** Two of them, one not granted by default, and half-satisfying the pair produces an error indistinguishable from "your account is locked."
- **`USE ROLE` is not a boundary.** It sets the primary role and leaves every other role you hold active. My least-privileged role read the private table while `CURRENT_ROLE()` reported the least-privileged role. The fix is one line. Finding it took running the test instead of assuming it.
- **Publish the error string.** "Cortex is locked on trial accounts" is a rumour. Nine verbatim messages, each naming the internal function that refused, is a finding somebody else can act on. They're in the README.
- **A constraint you can name is a design input.** Losing nine functions didn't cost me the project because the thesis was resting on a `GRANT`, not on a model.
- **`AI_AGG` with `GROUP BY` is a per-row transform.** I have not seen this written anywhere and it quietly un-gates a lot of trial-account work.
- **The line I had to *not* write is the only line that makes the promise true.** And the line I nearly didn't write, `USE SECONDARY ROLES NONE`, is the one that makes it enforceable.

Generosity in this challenge mostly got read as giving. This one is about the gift going the other way: sixty people gave a charity the worst week of their lives, on the understanding that it stayed private. Keeping that promise shouldn't cost them the proof that the help worked.

What would you want redacted before you'd share your own worst spreadsheet?
