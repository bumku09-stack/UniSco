-- 2026-08-03 (2차): OR로 묶인 복합조건 장학금 4건을 리스트형 required_special_status로 재분류.
-- migration_2026-08-03b_or_bundles_deadline_major.sql을 먼저 실행해서 커밋한 뒤 실행할 것.
--
-- 을지대 "면학장학금"(id 304)은 다자녀가 여러 소득분위 조건 중 하나의 하위조건일 뿐이라
-- (income-tier 안의 세부조건) 여기 포함 안 함 — 그대로 description 텍스트만 유지.

-- 배재사랑장학금: "장애학생 또는 다문화가정 학생 대상" — 장애 조건 자체가 그동안 비어있었어서 채움
UPDATE scholarship
SET requires_disability = TRUE,
    required_special_status = ARRAY['multicultural_family']
WHERE id = 164;

-- 희망복지장학금: "기초생활수급자·차상위계층·한부모가족 학생 대상"
UPDATE scholarship
SET required_special_status = ARRAY['basic_livelihood_recipient', 'near_poor', 'single_parent_family']
WHERE id = 167;

-- 장학사정관장학금(대전대): 다자녀/중증질병/실직가정·재난/긴급가계곤란/다문화가정자녀까지만 구조화.
-- "희망장학금(부모 중 장애등급)"은 학생 본인이 아니라 부모의 장애라 requires_disability로
-- 표현 안 됨, "기타 경제적 어려움 소명자"는 명시적 catch-all이라 구조화 불가 — 둘 다 description
-- 텍스트로만 유지(matching_gaps.md 참고).
UPDATE scholarship
SET required_special_status = ARRAY[
  'multi_child_family', 'severe_illness_or_injury', 'job_loss_or_disaster',
  'financial_emergency', 'multicultural_family'
]
WHERE id = 266;

-- 봉사공로 장학금(대전대): 9개 세부항목 중 "학생회임원봉사"만 구조화 가능(student_council_officer).
-- 나머지(국외봉사/외국인봉사/각종 행사 참여/행사공로/HRC/홍보대사/입시홍보/학군단)는 "특정 활동
-- 참여·수상 이력"이라 성격상 특수상황(신분)이 아니라서 구조화 대상에서 제외 — description
-- 텍스트로만 유지(matching_gaps.md 참고).
UPDATE scholarship
SET required_special_status = ARRAY['student_council_officer']
WHERE id = 288;
