-- ============================================================================
-- LEG C — the AI depth. Cortex AISQL, running where the data already lives.
--
-- Nothing here downloads a note to understand it. The model is brought to the
-- record, not the record to the model. That is the whole argument for a
-- warehouse rather than an API call behind my own server.
--
-- Run only after the matching probes in 00_gate.sql passed.
-- ============================================================================
USE ROLE SYSADMIN;
USE SCHEMA CONSENT.APP;

-- ── The boundary crossing, in one statement ─────────────────────────────────
-- AI_REDACT removes PII by category.  AI_CLASSIFY triages without a human
-- reading a name.  AI_FILTER is a semantic WHERE: "is this still unresolved?"
CREATE OR REPLACE TEMPORARY TABLE SAFE_CASES_NEW AS
SELECT case_id,
       intake_date,
       AI_REDACT(raw_note,
                 ['NAME','PHONE_NUMBER','EMAIL_ADDRESS',
                  'ADDRESS','ID_NUMBER'])                  AS redacted_note,
       AI_CLASSIFY(raw_note,
                 ['food','housing','health','legal'])      AS need_type_raw,
       AI_FILTER('this describes a need that is still unresolved, not one that '
                 || 'has already been resolved: ' || raw_note)
                                                           AS unresolved,
       'cortex'                                            AS method
FROM RAW_CASES;

TRUNCATE TABLE SAFE_CASES;
INSERT INTO SAFE_CASES (case_id, intake_date, redacted_note, need_type, unresolved, method)
SELECT case_id,
       intake_date,
       redacted_note,
       COALESCE(need_type_raw:labels[0]::STRING, need_type_raw::STRING) AS need_type,
       unresolved,
       method
FROM SAFE_CASES_NEW;

-- Re-assert after any CREATE OR REPLACE. Grants do not survive a replaced table.
GRANT SELECT ON TABLE CONSENT.APP.SAFE_CASES TO ROLE CONSENT_APP;

SELECT COUNT(*) AS safe_rows, COUNT_IF(unresolved) AS still_open FROM SAFE_CASES;
