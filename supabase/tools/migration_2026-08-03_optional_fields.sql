-- 2026-08-03: 어학점수/장애인 세부유형/특수상황 필드 추가 (matching_gaps.md 9·10·12번)
-- + GPA 직전학기·전체누적 동시충족(both) 기준 추가 (13번 후속, 을지대 크롤링 중 발견)
--
-- 실행 방법: python run_sql.py migration_2026-08-03_optional_fields.sql
-- (반드시 이 파일 먼저 실행 -> 성공 확인 후 -> reclassify_special_status_2026-08-03.sql 실행)

CREATE TYPE languagetesttype AS ENUM ('TOEIC', 'TOEFL', 'IELTS', 'TOPIK', '기타');

CREATE TYPE disabilitytype AS ENUM (
    'physical_impairment', 'learning_disability', 'medical_disability', 'mental_impairment',
    'muscular_dystrophy', 'developmental_impairment', 'disabled_parent'
);

CREATE TYPE specialstatus AS ENUM (
    'north_korean_defector', 'multicultural_family', 'child_care_facility',
    'student_council_officer', 'single_parent_family', 'grandparent_family',
    'multi_child_family', 'national_merit'
);

ALTER TYPE gpabasis ADD VALUE 'both';

ALTER TABLE scholarship ADD COLUMN required_disability_type disabilitytype;
ALTER TABLE scholarship ADD COLUMN language_test_type languagetesttype;
ALTER TABLE scholarship ADD COLUMN language_test_min_score FLOAT;
ALTER TABLE scholarship ADD COLUMN required_special_status specialstatus;

ALTER TABLE savedspec ADD COLUMN language_test_type languagetesttype;
ALTER TABLE savedspec ADD COLUMN language_test_score FLOAT;
ALTER TABLE savedspec ADD COLUMN disability_type disabilitytype;
ALTER TABLE savedspec ADD COLUMN special_status TEXT[] NOT NULL DEFAULT '{}';
