-- ============================================================================
-- LEG B — the boundary as an engine-enforced policy.  ENTERPRISE EDITION ONLY.
--
-- With Leg A the app is not allowed to ask.
-- With Leg B the engine answers differently depending on who is asking — and no
-- application code decides that, which means no application bug can undo it.
-- ============================================================================
USE ROLE SYSADMIN;
USE SCHEMA CONSENT.APP;

CREATE OR REPLACE MASKING POLICY pii_mask AS (v STRING) RETURNS STRING ->
  CASE WHEN CURRENT_ROLE() IN ('CASEWORKER','SYSADMIN','ACCOUNTADMIN') THEN v
       ELSE '<withheld by policy>' END;

ALTER TABLE RAW_CASES MODIFY COLUMN raw_note SET MASKING POLICY pii_mask;

-- The same SELECT, two roles, two different truths:
--   USE ROLE CASEWORKER;   SELECT raw_note FROM CONSENT.APP.RAW_CASES LIMIT 1;
--     -> the full note, because a caseworker is supposed to see it
--   USE ROLE CONSENT_APP;  SELECT raw_note FROM CONSENT.APP.RAW_CASES LIMIT 1;
--     -> denied by Leg A before the policy is even consulted
--
-- Two independent locks on the same door. Leg B is the one that still holds if
-- somebody, some day, grants the app more than they meant to.
