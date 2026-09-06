-- ============================================================================
-- NO-CORTEX FALLBACK. Write this whatever the gate said — it is the insurance.
-- Crude, and that is the honest framing: rules a reader can audit line by line,
-- versus a model that generalises. Still runs IN-WAREHOUSE, so the thesis holds.
-- ============================================================================
USE ROLE SYSADMIN;
USE SCHEMA CONSENT.APP;

CREATE OR REPLACE FUNCTION REGEX_REDACT(v STRING) RETURNS STRING AS
$$
  REGEXP_REPLACE(
    REGEXP_REPLACE(
      REGEXP_REPLACE(v, '[0-9]{3}[- ]?[0-9]{4,}', '[PHONE]'),
      '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}', '[EMAIL]'),
    '\\b[0-9]+\\s+[A-Z][a-z]+\\s+(St|Rd|Ave|Lane|Street|Road)\\b', '[ADDRESS]')
$$;

-- Names are the hard case for regex. Match against a known-names table rather
-- than pretending a pattern can find them, and SAY SO in the post.
CREATE OR REPLACE TABLE SAFE_CASES_FALLBACK AS
SELECT case_id, intake_date,
       REGEX_REDACT(raw_note) AS redacted_note,
       CASE WHEN raw_note ILIKE '%food%'    OR raw_note ILIKE '%parcel%' THEN 'food'
            WHEN raw_note ILIKE '%rent%'    OR raw_note ILIKE '%evict%'  THEN 'housing'
            WHEN raw_note ILIKE '%doctor%'  OR raw_note ILIKE '%meds%'   THEN 'health'
            WHEN raw_note ILIKE '%solicit%' OR raw_note ILIKE '%court%'  THEN 'legal'
            ELSE 'other' END AS need_type,
       raw_note NOT ILIKE '%resolved%' AS unresolved
FROM RAW_CASES;
