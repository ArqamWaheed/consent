-- ============================================================================
-- HOUR 1 — THE ENTITLEMENT GATE.  Run this FIRST, one statement at a time.
--
-- Do NOT run this file with EXECUTE IMMEDIATE FROM. A probe that fails is a
-- *result*, not an error, and a script would abort on the first one. Run each
-- statement, write the verdict into memory.md, and only then build on it.
--
-- Two builders in the previous edition of this challenge designed around a
-- Cortex function and found mid-build they could not call it. The docs
-- document no trial/edition restriction on Cortex AI Functions — they document
-- a TWO-PART gate that is easy to half-satisfy:
--   https://docs.snowflake.com/en/user-guide/snowflake-cortex/aisql-privileges-and-access
-- ============================================================================

-- ── 0. Where am I, and on what edition? ─────────────────────────────────────
USE ROLE ACCOUNTADMIN;
SELECT CURRENT_REGION()  AS region,
       CURRENT_ACCOUNT() AS account,
       CURRENT_USER()    AS who,
       CURRENT_VERSION() AS version;

SHOW PARAMETERS LIKE 'CORTEX_ENABLED_CROSS_REGION' IN ACCOUNT;

-- ── 1. BOTH halves of the Cortex gate (the step everyone misses) ────────────
-- USE AI FUNCTIONS is granted to PUBLIC by default. CORTEX_USER is granted to
-- nothing by default and only ACCOUNTADMIN can hand it out. Half-satisfying
-- this gate is indistinguishable, from the error message, from "locked on trial".
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE SYSADMIN;
GRANT USE AI FUNCTIONS ON ACCOUNT TO ROLE SYSADMIN;
ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'ANY_REGION';

-- ── 2. LEG B probe — Enterprise-only governance. No Cortex involved. ────────
-- Fails on Standard Edition. That verdict decides Leg B and nothing else.
USE ROLE SYSADMIN;
CREATE DATABASE IF NOT EXISTS CONSENT;
CREATE SCHEMA   IF NOT EXISTS CONSENT.APP;

CREATE OR REPLACE MASKING POLICY CONSENT.APP.probe_mask AS (v STRING)
  RETURNS STRING -> CASE WHEN CURRENT_ROLE() = 'SYSADMIN' THEN v ELSE '***' END;
DROP MASKING POLICY IF EXISTS CONSENT.APP.probe_mask;

-- ── 3. LEG C probes — ascending order of how gated each one is ──────────────
-- AI_AGG is the least gated: the docs say it works with USE AI FUNCTIONS even
-- WITHOUT the CORTEX_USER database role. If this fails, all of Cortex is off.
SELECT AI_AGG(c, 'Summarise the common unmet need in one sentence.') AS agg_ok
  FROM (SELECT 'no food' c UNION ALL SELECT 'rent overdue' UNION ALL SELECT 'no food');

SELECT AI_REDACT('Call Maria Alvarez on 555-0142 about her flat at 12 Bridge St.') AS redact_ok;

SELECT AI_CLASSIFY('needs a food parcel this week',
                   ['food','housing','health','legal']) AS classify_ok;

SELECT AI_FILTER('this describes an unresolved housing problem, not a solved one',
                 'rent overdue two months, landlord threatening eviction') AS filter_ok;

SELECT AI_EXTRACT('Intake 3 Sep, Maria, needs food',
                  {'date':'the date','need':'what they need'}) AS extract_ok;

-- Most region-sensitive. Probe last. Expect it to be the first to fail, and do
-- not let it block anything. Needs a file on @CONSENT.APP.DOCS first.
-- SELECT AI_PARSE_DOCUMENT(TO_FILE('@CONSENT.APP.DOCS','sample_intake.pdf'),
--                          {'mode':'LAYOUT'}) AS parse_ok;
