-- 2026-08-14: OR 조건(서로 다른 종류의 조건 중 하나만 만족해도 통과) 지원을 위한
-- 재사용 가능한 컬럼 추가. 예: "농어촌 거주 6개월 이상" 또는 "본인이 농어업 종사" 또는
-- "농식품계열학과 재학" 중 하나만 만족하면 되는 경우(id=91 등).
-- NULL(기본값)이면 기존 장학금과 완전히 동일하게 동작함(AND 방식 그대로) — 이 기능은
-- 순전히 opt-in이라 기존 1500여 건의 매칭 결과에 영향 없음.
ALTER TABLE scholarship ADD COLUMN IF NOT EXISTS eligibility_alt_groups JSONB;

COMMENT ON COLUMN scholarship.eligibility_alt_groups IS
  '이 중 하나의 그룹만 만족하면 자격 충족(OR). 각 그룹은 {"eligible_region": "...", "major": "...", "required_special_status": [...], ...} 형태 — scholarship 테이블의 같은 이름 필드와 동일한 값 형식을 씀. NULL이면 이 기능 미사용(기존 AND 방식 그대로).';
