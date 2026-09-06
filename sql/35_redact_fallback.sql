-- ============================================================================
-- NO-CORTEX FALLBACK. Written whatever the gate said — it is the insurance.
--
-- Crude, and that is the honest framing: rules a reader can audit line by line,
-- versus a model that generalises. It still runs IN-WAREHOUSE, so the thesis
-- holds even with every AI feature switched off.
-- ============================================================================
USE ROLE SYSADMIN;
USE SCHEMA CONSENT.APP;

CREATE OR REPLACE FUNCTION REGEX_REDACT(v STRING) RETURNS STRING AS
$$
  REGEXP_REPLACE(
    REGEXP_REPLACE(
      REGEXP_REPLACE(
        REGEXP_REPLACE(v, '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}', '[EMAIL]'),
        '[0-9]{3}[- ]?[0-9]{4,}', '[PHONE]'),
      '\\b[0-9]+\\s+[A-Z][a-z]+(\\s+[A-Z][a-z]+)?\\s+(St|Rd|Ave|Lane|Street|Road)\\b', '[ADDRESS]'),
    '\\bCS-[0-9]{4}\\b', '[REF]')
$$;

-- Names are the hard case for a regex, and pretending otherwise would be the
-- dishonest move. Match against the roster the charity already holds rather
-- than hoping a pattern finds them — and say so in the write-up.
CREATE OR REPLACE FUNCTION REDACT_NAMES(v STRING) RETURNS STRING AS
$$
  REGEXP_REPLACE(v,
    '\\b(Amara|Mei|Viktor|Samuel|Maria|Tomasz|Lucia|Kwame|Fatima|Ngozi|Colm|Grace|'
    || 'Hana|Ahmed|Joseph|Rosa|Elena|Damp|Elena|Nadia|Ibrahim|Yusuf|Priya|Omar)'
    || '\\s+(Fischer|Silva|Abara|Nowak|Osei|Duarte|Alvarez|Kovac|Kaur|Petrov|Chen|'
    || 'Moreau|Haddad|Okafor|Wright|Aziz|Mensah|Novak|Ivanov|Diallo)\\b',
    '[NAME]')
$$;

CREATE OR REPLACE TEMPORARY TABLE SAFE_CASES_NEW AS
SELECT case_id,
       intake_date,
       REDACT_NAMES(REGEX_REDACT(raw_note)) AS redacted_note,
       CASE WHEN raw_note ILIKE '%food%'     OR raw_note ILIKE '%parcel%'
                 OR raw_note ILIKE '%meals%'                    THEN 'food'
            WHEN raw_note ILIKE '%rent%'     OR raw_note ILIKE '%evict%'
                 OR raw_note ILIKE '%damp%'  OR raw_note ILIKE '%sofa-surf%'
                 OR raw_note ILIKE '%no fixed address%'         THEN 'housing'
            WHEN raw_note ILIKE '%meds%'     OR raw_note ILIKE '%hospital%'
                 OR raw_note ILIKE '%mental health%' OR raw_note ILIKE '%asthma%'
                 OR raw_note ILIKE '%GP%'                       THEN 'health'
            WHEN raw_note ILIKE '%solicit%'  OR raw_note ILIKE '%court%'
                 OR raw_note ILIKE '%appeal%' OR raw_note ILIKE '%immigration%'
                 OR raw_note ILIKE '%summons%'                  THEN 'legal'
            ELSE 'other' END                 AS need_type,
       NOT (raw_note ILIKE '%resolved%')     AS unresolved,
       'regex'                               AS method
FROM RAW_CASES;

TRUNCATE TABLE SAFE_CASES;
INSERT INTO SAFE_CASES (case_id, intake_date, redacted_note, need_type, unresolved, method)
SELECT case_id, intake_date, redacted_note, need_type, unresolved, method FROM SAFE_CASES_NEW;

GRANT SELECT ON TABLE CONSENT.APP.SAFE_CASES TO ROLE CONSENT_APP;
SELECT COUNT(*) AS safe_rows, COUNT_IF(unresolved) AS still_open FROM SAFE_CASES;
