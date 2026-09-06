-- ============================================================================
-- LEG C — the AI depth, rebuilt from the one function a trial account allows.
--
-- What the gate found (sql/00_gate.sql, verdicts in memory.md): with BOTH Cortex
-- grants in place, AI_REDACT, AI_CLASSIFY, AI_FILTER, AI_EXTRACT, AI_COMPLETE and
-- SNOWFLAKE.CORTEX.SENTIMENT all answer
--     "AI function ... is not available for trial accounts."
-- Exactly two survive: AI_AGG and AI_SUMMARIZE_AGG — which are exactly the two the
-- docs exempt from needing the CORTEX_USER database role. The trial restriction and
-- the role restriction draw the same line.
--   https://docs.snowflake.com/en/user-guide/snowflake-cortex/aisql-privileges-and-access
--
-- So: AI_AGG is an aggregate. GROUP BY a unique key and every group has one row,
-- which makes it a per-row LLM transform. One call then does the work of three —
-- redaction, triage, and the unresolved flag — and returns them as JSON.
--
-- Nothing here downloads a note to understand it. The model is brought to the
-- record, not the record to the model.
-- ============================================================================
USE ROLE SYSADMIN;
USE SCHEMA CONSENT.APP;

-- ── The boundary crossing ───────────────────────────────────────────────────
CREATE OR REPLACE TABLE CORTEX_STAGING AS
SELECT case_id,
       intake_date,
       AI_AGG(raw_note,
              'You are redacting a charity case note. Return ONLY a JSON object with '
           || 'exactly these keys and no markdown fence: "redacted" (the note rewritten '
           || 'with every personal name replaced by [NAME], phone by [PHONE], email by '
           || '[EMAIL], street address by [ADDRESS], case reference by [REF], nothing '
           || 'else changed), "need" (exactly one of food, housing, health, legal), '
           || '"unresolved" (true if the need is still open, false if the note says it '
           || 'was resolved).') AS payload
FROM RAW_CASES
GROUP BY case_id, intake_date;

-- ── Parse the JSON, and refuse to publish anything that did not parse ───────
-- If the model returned something unusable for a row, that row does not silently
-- become a half-redacted note. It is held back and counted.
TRUNCATE TABLE SAFE_CASES;
INSERT INTO SAFE_CASES (case_id, intake_date, redacted_note, need_type, unresolved, method)
SELECT case_id,
       intake_date,
       TRY_PARSE_JSON(payload):redacted::STRING,
       LOWER(TRY_PARSE_JSON(payload):need::STRING),
       TRY_PARSE_JSON(payload):unresolved::BOOLEAN,
       'cortex'
FROM CORTEX_STAGING
WHERE TRY_PARSE_JSON(payload):redacted::STRING IS NOT NULL
  AND LOWER(TRY_PARSE_JSON(payload):need::STRING) IN ('food','housing','health','legal');

-- The staging table holds model output derived from private notes. It is not
-- granted to anything, and it is dropped as soon as SAFE_CASES is built.
DROP TABLE IF EXISTS CORTEX_STAGING;

-- Grants do not survive a replaced table. Re-assert, every time.
GRANT SELECT ON TABLE CONSENT.APP.SAFE_CASES TO ROLE CONSENT_APP;

SELECT (SELECT COUNT(*) FROM RAW_CASES)                AS raw_rows,
       COUNT(*)                                        AS published_rows,
       (SELECT COUNT(*) FROM RAW_CASES) - COUNT(*)     AS held_back,
       COUNT_IF(unresolved)                            AS still_open
FROM SAFE_CASES;
