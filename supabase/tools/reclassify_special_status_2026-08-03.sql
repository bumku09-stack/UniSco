-- 2026-08-03: 기존 장학금 중 description 텍스트로만 있던 새터민/보훈/다문화/아동양육시설/
-- 학생회임원 조건을 required_special_status 컬럼으로 재분류.
-- 여러 조건이 서로 다른 축(장애/소득/기타)과 OR로 묶여 있는 복합 조건 장학금(예: 배재사랑장학금,
-- 희망복지장학금, 장학사정관장학금, 봉사공로 장학금)은 단일 값으로 정확히 표현할 수 없어서
-- 의도적으로 제외함(호성에게 별도 보고 예정, matching_gaps.md 참고).
--
-- 실행 방법: migration_2026-08-03_optional_fields.sql을 먼저 실행해서 커밋한 뒤,
-- python run_sql.py reclassify_special_status_2026-08-03.sql

UPDATE scholarship SET required_special_status = 'north_korean_defector'
WHERE id IN (34, 58, 141, 162, 184, 247, 273, 307, 330);

UPDATE scholarship SET required_special_status = 'national_merit'
WHERE id IN (33, 57, 142, 169, 181, 207, 246, 272, 306, 331);

UPDATE scholarship SET required_special_status = 'multicultural_family'
WHERE id IN (147, 185, 311);

UPDATE scholarship SET required_special_status = 'child_care_facility'
WHERE id IN (139);

UPDATE scholarship SET required_special_status = 'student_council_officer'
WHERE id IN (149, 250, 312, 337, 338, 339);

-- 을지대 "차세대의료인장학금" — 전체누적+직전학기 둘 다 충족해야 하는 AND 조건 (matching_gaps.md 13번 후속)
UPDATE scholarship SET min_gpa_basis = 'both'
WHERE id = 316;
