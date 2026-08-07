-- 2026-08-05: 시/군/구 단위 지자체 장학금 매칭(matching_gaps.md 14번, 예: "정읍시 거주자만")을
-- 지원하기 위해 savedspec에 district/parent_district 컬럼 추가. 둘 다 선택 입력(NULL 허용).
-- backend/app/core/matching.py의 region_matches() 참고.
--
-- 실행 방법: python run_sql.py migration_2026-08-05b_district.sql

ALTER TABLE savedspec ADD COLUMN district VARCHAR;
ALTER TABLE savedspec ADD COLUMN parent_district VARCHAR;
