-- 2026-08-05: "본인 또는 부모 중 1인이 OO에 거주" 조건(matching_gaps.md 19번)을 지원하기
-- 위해 savedspec에 parent_region 컬럼 추가. 선택 입력(NULL 허용) — 안 넣으면 기존처럼
-- 본인 거주지(region)만으로 판단함. backend/app/core/matching.py의 region_matches() 참고.
--
-- 실행 방법: python run_sql.py migration_2026-08-05_parent_region.sql

ALTER TABLE savedspec ADD COLUMN parent_region VARCHAR;
