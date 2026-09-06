-- ============================================================================
-- THE BRIEF — AI_AGG reasons across EVERY redacted row, not a sample, and is
-- not bounded by a context window. It is also the least-gated Cortex function
-- in the build: the docs say it works with USE AI FUNCTIONS even without the
-- CORTEX_USER database role.
--
-- It reads SAFE_CASES, never RAW_CASES. The summary is written from material
-- that has already crossed the boundary.
-- ============================================================================
USE ROLE SYSADMIN;
USE SCHEMA CONSENT.APP;

TRUNCATE TABLE IMPACT_BRIEF;
INSERT INTO IMPACT_BRIEF (generated_at, method, brief)
SELECT CURRENT_TIMESTAMP()::TIMESTAMP_NTZ,
       MAX(method),
       AI_AGG(redacted_note,
              'You are writing three sentences for a charity''s funding report. '
           || 'Describe the pattern of unmet need across these cases. '
           || 'Cite counts. Never name or describe an individual.')
FROM SAFE_CASES;

GRANT SELECT ON TABLE CONSENT.APP.IMPACT_BRIEF TO ROLE CONSENT_APP;

SELECT brief FROM IMPACT_BRIEF;
