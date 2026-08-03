-- 2026-08-03 (2차): 특수상황을 리스트(OR)로 바꾸고, 마감일/학과 구조화 컬럼 추가.
-- migration_2026-08-03_optional_fields.sql이 이미 적용되어 있어야 함(그 위에 이어서 적용).
--
-- 실행 방법: python run_sql.py migration_2026-08-03b_or_bundles_deadline_major.sql
-- (성공 확인 후) python run_sql.py reclassify_or_bundles_2026-08-03b.sql

-- required_special_status: 단일값(specialstatus) -> 리스트(TEXT[])로 변경.
-- 배재사랑장학금("장애학생 또는 다문화가정")처럼 여러 조건이 OR로 묶인 장학금을 표현하려면
-- 장학금 쪽도 다중값이어야 함(SavedSpec.special_status와 동일한 방식).
ALTER TABLE scholarship ALTER COLUMN required_special_status DROP DEFAULT;
ALTER TABLE scholarship ALTER COLUMN required_special_status TYPE TEXT[] USING (
  CASE WHEN required_special_status IS NULL THEN '{}'::TEXT[]
       ELSE ARRAY[required_special_status::TEXT]
  END
);
ALTER TABLE scholarship ALTER COLUMN required_special_status SET DEFAULT '{}';
ALTER TABLE scholarship ALTER COLUMN required_special_status SET NOT NULL;

-- 마감일 구조화 (matching_gaps.md 7번). 대부분 기존 데이터는 "매 학기 초 공지"류 상시
-- 프로그램이라 NULL로 남고, 실제 확정 마감일이 있는 공고만 이후 크롤링에서 채움.
ALTER TABLE scholarship ADD COLUMN application_deadline DATE;

-- 학과 (matching_gaps.md 2번) — SavedSpec에도 department 컬럼 추가.
ALTER TABLE savedspec ADD COLUMN department VARCHAR;
