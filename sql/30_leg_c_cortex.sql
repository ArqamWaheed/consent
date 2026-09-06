-- ============================================================================
-- LEG C — the AI depth. Six Cortex AISQL functions.
-- Five of these had ZERO usage across the entire 31-entry challenge field.
-- Run these in gate order and COMMIT AFTER EACH so you can stop anywhere.
-- ============================================================================
USE ROLE SYSADMIN;
USE SCHEMA CONSENT.APP;

-- ── C5: PARSE — the document is read where it lands ─────────────────────────
CREATE OR REPLACE TABLE PARSED AS
SELECT RELATIVE_PATH AS source_file,
       AI_PARSE_DOCUMENT(TO_FILE('@CONSENT.APP.DOCS', RELATIVE_PATH),
                         {'mode':'LAYOUT'}) AS doc
FROM DIRECTORY(@CONSENT.APP.DOCS);

-- ── C4: EXTRACT — structure without a human reading a name ──────────────────
CREATE OR REPLACE TABLE EXTRACTED AS
SELECT source_file,
       AI_EXTRACT(doc:content::STRING,
                  {'intake_date':'the intake date',
                   'note':'the caseworker note'}) AS fields
FROM PARSED;

-- ── C2 + C3: REDACT (the boundary) + triage ─────────────────────────────────
CREATE OR REPLACE TABLE SAFE_CASES AS
SELECT MD5(source_file || fields:intake_date::STRING)          AS case_id,
       fields:intake_date::DATE                                AS intake_date,
       AI_REDACT(fields:note::STRING,
                 ['NAME','PHONE_NUMBER','EMAIL_ADDRESS',
                  'ADDRESS','ID_NUMBER'])                      AS redacted_note,
       AI_CLASSIFY(fields:note::STRING,
                 ['food','housing','health','legal'])          AS need_type,
       AI_FILTER('this describes a need that is still unresolved',
                 fields:note::STRING)                          AS unresolved
FROM EXTRACTED;

-- ── C1: AGG — the safest AI call here. Reasons across EVERY row, ────────────
--        not a sample, and not limited by a context window.
SELECT AI_AGG(redacted_note,
              'In three sentences, describe the pattern of unmet need across these
               cases. Cite counts, never individuals.') AS impact_brief
FROM SAFE_CASES;

-- Private tables stay ungranted. Re-assert after any CREATE OR REPLACE.
GRANT SELECT ON TABLE CONSENT.APP.SAFE_CASES TO ROLE CONSENT_APP;
