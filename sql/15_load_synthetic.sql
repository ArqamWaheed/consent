-- ============================================================================
-- SYNTHETIC CASEWORK. 60 fabricated records. No real casework was used to build
-- or demo this project. Every name, phone, address, email and reference below
-- is invented. Kept as plain INSERTs so the repo is self-contained: no stage
-- upload, no COPY INTO, no external file needed to reproduce the demo.
-- ============================================================================
USE ROLE SYSADMIN;
USE SCHEMA CONSENT.APP;

TRUNCATE TABLE IF EXISTS RAW_CASES;

INSERT INTO RAW_CASES (case_id, intake_date, raw_note, source_file) VALUES
  ('CS-2000', '2026-09-02'::DATE, 'Amara Fischer needs a solicitor for a benefits appeal, court date set. Contact 555-0562.', 'synthetic_cases.csv'),
  ('CS-2001', '2026-09-05'::DATE, 'Mei Silva needs a solicitor for a benefits appeal, court date set. Contact 555-0196.', 'synthetic_cases.csv'),
  ('CS-2002', '2026-09-02'::DATE, 'Doorstep visit to 169 King Street. Mei Abara skipping meals so the children eat. Contact 555-0563.', 'synthetic_cases.csv'),
  ('CS-2003', '2026-09-01'::DATE, 'Doorstep visit to 11 Mill Rd. Viktor Nowak skipping meals so the children eat. Contact 555-0160.', 'synthetic_cases.csv'),
  ('CS-2004', '2026-09-03'::DATE, 'Samuel Fischer (samuel.fischer@example.org) unsure of immigration paperwork deadlines, referred on 2 Sep.', 'synthetic_cases.csv'),
  ('CS-2005', '2026-09-01'::DATE, 'Maria Nowak (maria.nowak@example.org) unsure of immigration paperwork deadlines, referred on 4 Sep.', 'synthetic_cases.csv'),
  ('CS-2006', '2026-09-01'::DATE, 'Samuel Osei (samuel.osei@example.org) waiting on a mental health referral since 1 Sep.', 'synthetic_cases.csv'),
  ('CS-2007', '2026-09-02'::DATE, 'Tomasz Duarte needs a solicitor for a benefits appeal, court date set. Contact 555-0495.', 'synthetic_cases.csv'),
  ('CS-2008', '2026-09-02'::DATE, 'Doorstep visit to 103 Vernon Road. Lucia Abara skipping meals so the children eat. Contact 555-0825.', 'synthetic_cases.csv'),
  ('CS-2009', '2026-09-02'::DATE, 'Samuel Nowak cannot afford meds this month, ref CS-2009. GP at 87 Bridge St. Mobile 555-0418.', 'synthetic_cases.csv'),
  ('CS-2010', '2026-09-05'::DATE, 'Tomasz Alvarez has rent overdue two months, landlord threatening eviction at 121 Elm Rd. Call 555-0161.', 'synthetic_cases.csv'),
  ('CS-2011', '2026-09-04'::DATE, 'Kwame Kovac has rent overdue two months, landlord threatening eviction at 35 Vernon Road. Call 555-0295.', 'synthetic_cases.csv'),
  ('CS-2012', '2026-09-02'::DATE, 'Fatima Alvarez needs a solicitor for a benefits appeal, court date set. Contact 555-0376.', 'synthetic_cases.csv'),
  ('CS-2013', '2026-09-03'::DATE, 'Mei Wright at 12 Mill Rd received a court summons over council tax arrears. Ref CS-2013.', 'synthetic_cases.csv'),
  ('CS-2014', '2026-09-01'::DATE, 'Mei Kaur called, no food in the house since 1 Sep. Two kids. Phone 555-0950. Lives at 77 Vernon Road.', 'synthetic_cases.csv'),
  ('CS-2015', '2026-09-04'::DATE, 'Damp in the flat at 155 Ash Lane making Joseph Osei''s asthma worse. Landlord not responding.', 'synthetic_cases.csv'),
  ('CS-2016', '2026-09-02'::DATE, 'Joseph Moreau has rent overdue two months, landlord threatening eviction at 149 Mill Rd. Call 555-0952.', 'synthetic_cases.csv'),
  ('CS-2017', '2026-09-04'::DATE, 'Colm Chen cannot afford meds this month, ref CS-2017. GP at 50 Mill Rd. Mobile 555-0355.', 'synthetic_cases.csv'),
  ('CS-2018', '2026-09-05'::DATE, 'Mei Nowak needs a solicitor for a benefits appeal, court date set. Contact 555-0531.', 'synthetic_cases.csv'),
  ('CS-2019', '2026-09-03'::DATE, 'Colm Abara missed a hospital appointment, no bus fare. Phone 555-0363. Resolved after travel voucher.', 'synthetic_cases.csv'),
  ('CS-2020', '2026-09-01'::DATE, 'Damp in the flat at 124 Prospect Ave making Grace Haddad''s asthma worse. Landlord not responding.', 'synthetic_cases.csv'),
  ('CS-2021', '2026-09-04'::DATE, 'Fatima Petrov missed a hospital appointment, no bus fare. Phone 555-0866. Resolved after travel voucher.', 'synthetic_cases.csv'),
  ('CS-2022', '2026-09-02'::DATE, 'Damp in the flat at 74 Ash Lane making Ahmed Okafor''s asthma worse. Landlord not responding.', 'synthetic_cases.csv'),
  ('CS-2023', '2026-09-02'::DATE, 'Doorstep visit to 86 King Street. Hana Haddad skipping meals so the children eat. Contact 555-0561.', 'synthetic_cases.csv'),
  ('CS-2024', '2026-09-01'::DATE, 'Doorstep visit to 81 Bridge St. Maria Moreau skipping meals so the children eat. Contact 555-0466.', 'synthetic_cases.csv'),
  ('CS-2025', '2026-09-05'::DATE, 'Grace Duarte at 36 Bridge St received a court summons over council tax arrears. Ref CS-2025.', 'synthetic_cases.csv'),
  ('CS-2026', '2026-09-04'::DATE, 'Ahmed Haddad (ahmed.haddad@example.org) waiting on a mental health referral since 1 Sep.', 'synthetic_cases.csv'),
  ('CS-2027', '2026-09-04'::DATE, 'Doorstep visit to 129 Prospect Ave. Rosa Alvarez skipping meals so the children eat. Contact 555-0984.', 'synthetic_cases.csv'),
  ('CS-2028', '2026-09-01'::DATE, 'Joseph Alvarez (joseph.alvarez@example.org) unsure of immigration paperwork deadlines, referred on 1 Sep.', 'synthetic_cases.csv'),
  ('CS-2029', '2026-09-04'::DATE, 'Rosa Kaur missed a hospital appointment, no bus fare. Phone 555-0497. Resolved after travel voucher.', 'synthetic_cases.csv'),
  ('CS-2030', '2026-09-01'::DATE, 'Viktor Kovac (viktor.kovac@example.org) needs a food parcel this week; benefits delayed again. Ref CS-2030.', 'synthetic_cases.csv'),
  ('CS-2031', '2026-09-01'::DATE, 'Tomasz Moreau sofa-surfing since 4 Sep, no fixed address. Email tomasz.moreau@example.org. Case ref CS-2031.', 'synthetic_cases.csv'),
  ('CS-2032', '2026-09-03'::DATE, 'Elena Haddad cannot afford meds this month, ref CS-2032. GP at 158 Mill Rd. Mobile 555-0794.', 'synthetic_cases.csv'),
  ('CS-2033', '2026-09-04'::DATE, 'Lucia Osei needs a solicitor for a benefits appeal, court date set. Contact 555-0434.', 'synthetic_cases.csv'),
  ('CS-2034', '2026-09-02'::DATE, 'Fatima Abara has rent overdue two months, landlord threatening eviction at 151 Ash Lane. Call 555-0324.', 'synthetic_cases.csv'),
  ('CS-2035', '2026-09-04'::DATE, 'Hana Okafor needs a solicitor for a benefits appeal, court date set. Contact 555-0828.', 'synthetic_cases.csv'),
  ('CS-2036', '2026-09-03'::DATE, 'Ngozi Petrov at 107 Vernon Road received a court summons over council tax arrears. Ref CS-2036.', 'synthetic_cases.csv'),
  ('CS-2037', '2026-09-03'::DATE, 'Samuel Nowak needs a solicitor for a benefits appeal, court date set. Contact 555-0948.', 'synthetic_cases.csv'),
  ('CS-2038', '2026-09-02'::DATE, 'Elena Wright missed a hospital appointment, no bus fare. Phone 555-0119. Resolved after travel voucher.', 'synthetic_cases.csv'),
  ('CS-2039', '2026-09-01'::DATE, 'Doorstep visit to 38 Elm Rd. Ngozi Osei skipping meals so the children eat. Contact 555-0897.', 'synthetic_cases.csv'),
  ('CS-2040', '2026-09-02'::DATE, 'Tomasz Diallo needs a solicitor for a benefits appeal, court date set. Contact 555-0770.', 'synthetic_cases.csv'),
  ('CS-2041', '2026-09-01'::DATE, 'Damp in the flat at 4 Elm Rd making Lucia Mensah''s asthma worse. Landlord not responding.', 'synthetic_cases.csv'),
  ('CS-2042', '2026-09-05'::DATE, 'Damp in the flat at 90 Prospect Ave making Colm Mensah''s asthma worse. Landlord not responding.', 'synthetic_cases.csv'),
  ('CS-2043', '2026-09-04'::DATE, 'Ibrahim Osei has rent overdue two months, landlord threatening eviction at 107 King Street. Call 555-0189.', 'synthetic_cases.csv'),
  ('CS-2044', '2026-09-04'::DATE, 'Fatima Alvarez at 142 Prospect Ave received a court summons over council tax arrears. Ref CS-2044.', 'synthetic_cases.csv'),
  ('CS-2045', '2026-09-02'::DATE, 'Fatima Byrne cannot afford meds this month, ref CS-2045. GP at 166 King Street. Mobile 555-0839.', 'synthetic_cases.csv'),
  ('CS-2046', '2026-09-05'::DATE, 'Grace Duarte at 84 Ash Lane received a court summons over council tax arrears. Ref CS-2046.', 'synthetic_cases.csv'),
  ('CS-2047', '2026-09-01'::DATE, 'Ahmed Fischer (ahmed.fischer@example.org) needs a food parcel this week; benefits delayed again. Ref CS-2047.', 'synthetic_cases.csv'),
  ('CS-2048', '2026-09-02'::DATE, 'Grace Lynch sofa-surfing since 5 Sep, no fixed address. Email grace.lynch@example.org. Case ref CS-2048.', 'synthetic_cases.csv'),
  ('CS-2049', '2026-09-05'::DATE, 'Priya Kovac at 134 Elm Rd received a court summons over council tax arrears. Ref CS-2049.', 'synthetic_cases.csv'),
  ('CS-2050', '2026-09-02'::DATE, 'Doorstep visit to 145 Ash Lane. Colm Fischer skipping meals so the children eat. Contact 555-0639.', 'synthetic_cases.csv'),
  ('CS-2051', '2026-09-05'::DATE, 'Elena Abara cannot afford meds this month, ref CS-2051. GP at 158 Mill Rd. Mobile 555-0965.', 'synthetic_cases.csv'),
  ('CS-2052', '2026-09-01'::DATE, 'Joseph Moreau (joseph.moreau@example.org) waiting on a mental health referral since 1 Sep.', 'synthetic_cases.csv'),
  ('CS-2053', '2026-09-01'::DATE, 'Maria Diallo (maria.diallo@example.org) unsure of immigration paperwork deadlines, referred on 5 Sep.', 'synthetic_cases.csv'),
  ('CS-2054', '2026-09-03'::DATE, 'Grace Silva at 139 Vernon Road received a court summons over council tax arrears. Ref CS-2054.', 'synthetic_cases.csv'),
  ('CS-2055', '2026-09-03'::DATE, 'Damp in the flat at 88 Vernon Road making Lucia Moreau''s asthma worse. Landlord not responding.', 'synthetic_cases.csv'),
  ('CS-2056', '2026-09-01'::DATE, 'Doorstep visit to 9 Ash Lane. Fatima Lynch skipping meals so the children eat. Contact 555-0732.', 'synthetic_cases.csv'),
  ('CS-2057', '2026-09-03'::DATE, 'Fatima Haddad (fatima.haddad@example.org) needs a food parcel this week; benefits delayed again. Ref CS-2057.', 'synthetic_cases.csv'),
  ('CS-2058', '2026-09-05'::DATE, 'Mei Moreau has rent overdue two months, landlord threatening eviction at 129 King Street. Call 555-0207.', 'synthetic_cases.csv'),
  ('CS-2059', '2026-09-04'::DATE, 'Fatima Kovac (fatima.kovac@example.org) waiting on a mental health referral since 4 Sep.', 'synthetic_cases.csv');

SELECT COUNT(*) AS raw_rows_loaded FROM RAW_CASES;
