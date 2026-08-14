-- 2026-08-15: PR #13 코드 리뷰에서 발견 — matching_gaps_resolved.md는 id=1046/526/663의
-- eligibility_alt_groups 적용을 "✅ 해결"로 문서화했지만, 실제로 그 값을 채우는 UPDATE가
-- 해당 PR 어디에도 없었음(컬럼을 추가하는 migration_2026-08-14_eligibility_alt_groups.sql만
-- 존재). 문서가 이미 약속한 내용을 실제 데이터에 반영해서 문서-데이터 불일치를 없앰.
--
-- 세 건 모두 원래 body에 걸려있던 max_income_bracket/required_special_status/
-- requires_disability를 alt_groups로 옮기면서 body 쪽은 비움 — matching.py의 컨벤션
-- (alt_groups를 쓰는 필드는 body에 남겨두지 않음) 그대로 안 지키면, body 조건이
-- alt_groups OR 위에 추가 AND로 걸려서 그룹 중 하나를 통과해도 최종적으로 다시 걸러짐
-- (과소매칭이 그대로 재발). 각 UPDATE는 최종 상태를 명시적으로 지정하므로 현재 값이
-- 무엇이었든 멱등하게 적용됨.

-- id=1046 인천 희망드림장학금: 학자금지원구간 6구간 이하 OR 기초생활수급자·차상위·한부모
-- OR 중증장애인(장애 정도 구분이 시스템에 없어 장애 유무만 봄) — matching_gaps_resolved.md
-- "id=1046 인천 희망드림장학금 등 4건" 항목 참고.
UPDATE scholarship SET
  eligibility_alt_groups = '[
    {"max_income_bracket": 6},
    {"required_special_status": ["basic_livelihood_recipient", "near_poor", "single_parent_family"]},
    {"requires_disability": true}
  ]'::jsonb,
  max_income_bracket = NULL,
  required_special_status = '{}'::TEXT[],
  requires_disability = NULL
WHERE id = 1046;

-- id=526 모범장학생(세종): 학자금지원구간 6구간 이하 OR 기초생활수급자·차상위
UPDATE scholarship SET
  eligibility_alt_groups = '[
    {"max_income_bracket": 6},
    {"required_special_status": ["basic_livelihood_recipient", "near_poor"]}
  ]'::jsonb,
  max_income_bracket = NULL,
  required_special_status = '{}'::TEXT[]
WHERE id = 526;

-- id=663 신한장학재단 법학전문대학원: 학자금지원구간 3구간 이하 OR 기초생활수급자·차상위
UPDATE scholarship SET
  eligibility_alt_groups = '[
    {"max_income_bracket": 3},
    {"required_special_status": ["basic_livelihood_recipient", "near_poor"]}
  ]'::jsonb,
  max_income_bracket = NULL,
  required_special_status = '{}'::TEXT[]
WHERE id = 663;

-- id=999(인재육성장학금, 횡성)는 matching_gaps_resolved.md에 따르면 애초에
-- max_income_bracket이 안 걸려있어서(태그 리스트 자체가 이미 OR) 과소매칭이 아니었음 —
-- 문서와 동일하게 손 대지 않음.
