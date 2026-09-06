-- ============================================================================
-- LEG B — the boundary as an engine-enforced policy.
--
-- ⚠️  NOT AVAILABLE ON THE ACCOUNT THIS WAS BUILT ON. Verbatim:
--        Unsupported feature 'MASKING POLICY'.
--     Dynamic Data Masking requires Enterprise Edition or higher. The trial used
--     here is Standard Edition, and edition is fixed at signup.
--
-- This file is kept, unrun, because it is the documented upgrade path and because
-- deleting the thing you could not have is how a capability grid becomes a lie.
-- On Enterprise it is four lines, and it is the strongest part of the design:
-- Leg A means the app is not ALLOWED to ask; Leg B means the engine ANSWERS
-- DIFFERENTLY depending on who asks, with no application code in the decision.
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
