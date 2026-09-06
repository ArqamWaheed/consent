-- ============================================================================
-- LEG B — the boundary as an engine-enforced policy.  ENTERPRISE EDITION ONLY.
-- With Leg A the app is not allowed to ask. With Leg B the engine answers
-- differently depending on who asks — and no application bug can undo that.
-- ============================================================================
USE ROLE SYSADMIN;
USE SCHEMA CONSENT.APP;

CREATE OR REPLACE MASKING POLICY pii_mask AS (v STRING) RETURNS STRING ->
  CASE WHEN CURRENT_ROLE() IN ('CASEWORKER','SYSADMIN') THEN v
       ELSE '‹withheld by policy›' END;

ALTER TABLE RAW_CASES MODIFY COLUMN raw_note SET MASKING POLICY pii_mask;

-- Demo for the post: the same SELECT, two roles, two different truths.
--   USE ROLE SYSADMIN;    SELECT raw_note FROM RAW_CASES LIMIT 1;  -- full text
--   USE ROLE CONSENT_APP; SELECT raw_note FROM RAW_CASES LIMIT 1;  -- blocked by Leg A anyway
