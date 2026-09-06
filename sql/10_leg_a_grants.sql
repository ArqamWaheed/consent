-- ============================================================================
-- LEG A — the boundary as a grant.
-- Works on ANY account, ANY edition, with every AI feature switched off.
-- This is the thesis. Everything after it is an upgrade.
-- Safe to run with:  EXECUTE IMMEDIATE FROM @CONSENT.APP.REPO/branches/main/sql/10_leg_a_grants.sql;
-- ============================================================================
USE ROLE SYSADMIN;

CREATE DATABASE IF NOT EXISTS CONSENT;
CREATE SCHEMA   IF NOT EXISTS CONSENT.APP;
USE SCHEMA CONSENT.APP;

CREATE STAGE IF NOT EXISTS CONSENT.APP.DOCS
  DIRECTORY = (ENABLE = TRUE) ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');

-- ── The private side ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS RAW_CASES (
  case_id      STRING,
  intake_date  DATE,
  raw_note     STRING,   -- carries PII. The app must never be able to SELECT this.
  source_file  STRING
);

-- ── The publishable side ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS SAFE_CASES (
  case_id       STRING,
  intake_date   DATE,
  redacted_note STRING,
  need_type     STRING,
  unresolved    BOOLEAN,
  method        STRING    -- 'cortex' or 'regex'. The app tells you which shipped.
);

CREATE TABLE IF NOT EXISTS IMPACT_BRIEF (
  generated_at  TIMESTAMP_NTZ,
  method        STRING,
  brief         STRING
);

-- ── The count, without the contents ─────────────────────────────────────────
-- A view runs with its owner's rights. So the app can be told HOW MANY private
-- records exist without ever being able to see one. The boundary is not
-- all-or-nothing; it is exactly as wide as it needs to be.
CREATE OR REPLACE VIEW PRIVATE_ROW_COUNT AS
  SELECT COUNT(*) AS private_rows FROM CONSENT.APP.RAW_CASES;

-- ── Roles ───────────────────────────────────────────────────────────────────
USE ROLE ACCOUNTADMIN;
CREATE ROLE IF NOT EXISTS CONSENT_APP;   -- what the published app runs as
CREATE ROLE IF NOT EXISTS CASEWORKER;    -- what a person inside the charity runs as
GRANT ROLE CONSENT_APP TO ROLE SYSADMIN;
GRANT ROLE CASEWORKER  TO ROLE SYSADMIN;

GRANT USAGE ON DATABASE  CONSENT     TO ROLE CONSENT_APP;
GRANT USAGE ON SCHEMA    CONSENT.APP TO ROLE CONSENT_APP;
GRANT USAGE ON WAREHOUSE COMPUTE_WH  TO ROLE CONSENT_APP;

GRANT USAGE ON DATABASE  CONSENT     TO ROLE CASEWORKER;
GRANT USAGE ON SCHEMA    CONSENT.APP TO ROLE CASEWORKER;
GRANT USAGE ON WAREHOUSE COMPUTE_WH  TO ROLE CASEWORKER;
GRANT SELECT ON TABLE CONSENT.APP.RAW_CASES TO ROLE CASEWORKER;

-- ── The three grants the app gets, and the ones it does not ─────────────────
GRANT SELECT ON TABLE CONSENT.APP.SAFE_CASES        TO ROLE CONSENT_APP;
GRANT SELECT ON TABLE CONSENT.APP.IMPACT_BRIEF      TO ROLE CONSENT_APP;
GRANT SELECT ON VIEW  CONSENT.APP.PRIVATE_ROW_COUNT TO ROLE CONSENT_APP;

-- deliberately NOT granted to CONSENT_APP: RAW_CASES, PARSED, EXTRACTED.
-- This absence is the only line in the project that makes the promise true.

-- Proof, for the post — run these two and watch the second one fail:
--   USE ROLE CONSENT_APP; SELECT * FROM CONSENT.APP.PRIVATE_ROW_COUNT;  -- 60
--   USE ROLE CONSENT_APP; SELECT * FROM CONSENT.APP.RAW_CASES;          -- denied
