-- ============================================================================
-- LEG A — the boundary as a grant.
-- Works on ANY account, ANY edition, with every AI feature switched off.
-- This is the thesis. Everything else is an upgrade.
-- ============================================================================
USE ROLE SYSADMIN;
USE SCHEMA CONSENT.APP;

CREATE OR REPLACE TABLE RAW_CASES (
  case_id      STRING,
  intake_date  DATE,
  raw_note     STRING,      -- contains PII. The app must never be able to SELECT this.
  source_file  STRING
);

CREATE OR REPLACE TABLE SAFE_CASES (
  case_id       STRING,
  intake_date   DATE,
  redacted_note STRING,
  need_type     STRING,
  unresolved    BOOLEAN
);

CREATE ROLE IF NOT EXISTS CONSENT_APP;
GRANT USAGE  ON DATABASE CONSENT     TO ROLE CONSENT_APP;
GRANT USAGE  ON SCHEMA   CONSENT.APP TO ROLE CONSENT_APP;
GRANT USAGE  ON WAREHOUSE COMPUTE_WH TO ROLE CONSENT_APP;
GRANT SELECT ON TABLE CONSENT.APP.SAFE_CASES TO ROLE CONSENT_APP;

-- deliberately NOT granted: RAW_CASES, PARSED, EXTRACTED
-- This absence is the only line in the project that makes the promise true.

-- Proof, for the post: run as CONSENT_APP and watch it fail.
--   USE ROLE CONSENT_APP;
--   SELECT * FROM CONSENT.APP.RAW_CASES;   -- Object does not exist / not authorized
