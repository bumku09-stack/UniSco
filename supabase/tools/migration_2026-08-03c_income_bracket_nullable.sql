-- 2026-08-03: 소득분위 "모름" 지원을 위해 savedspec.income_bracket을 선택 입력으로 변경.
-- 자기 소득분위를 모르는 사용자가 많아서, 스펙 입력/마이페이지에서 드롭다운 + "모름" 옵션을
-- 추가하고, "모름"이면 소득분위 조건이 있는 장학금도 안 거르고 전부 보여주도록 처리함
-- (special_status의 "선택 안 함=모름=안 거름" 원칙과 동일, backend/app/core/matching.py의
-- is_eligible() 참고).
--
-- 실행 방법: python run_sql.py migration_2026-08-03c_income_bracket_nullable.sql

ALTER TABLE savedspec ALTER COLUMN income_bracket DROP NOT NULL;
