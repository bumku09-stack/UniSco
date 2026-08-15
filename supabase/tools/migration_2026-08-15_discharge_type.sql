-- 2026-08-15: "병사 전역"/"장교·부사관 전역" 세부 구분 추가 — id=652(제대군인대부지원,
-- "10년 이상 장기복무 제대군인 대상")처럼 군필 중에서도 세부 구분이 갈리는 조건을 표현하기
-- 위함. military_status(gender처럼 필수 단일값)와 별개로, "군필일 때만 의미 있는" 조건이라
-- degree_level(enrollment_status=post_undergrad일 때만 의미)과 같은 패턴으로 분리함.
-- backend/app/models/enums.py의 DischargeType, frontend/src/lib/spec.ts 참고.
CREATE TYPE dischargetype AS ENUM ('enlisted', 'officer_or_nco');

ALTER TABLE scholarship ADD COLUMN IF NOT EXISTS required_discharge_type dischargetype;
ALTER TABLE savedspec ADD COLUMN IF NOT EXISTS discharge_type dischargetype;

-- id=652(제대군인대부지원, "10년 이상 장기복무 제대군인 대상") — 원문상 병사(의무복무,
-- 통상 18~21개월)는 10년 장기복무 자체가 성립 안 하므로 장교/부사관 전역으로 확정.
-- (10년 이상이라는 복무기간까지는 이 필드로 표현 못 함 — description에 원문 그대로
-- 남겨서 노란색 참고용으로 계속 보이게 함, 남은 한계로 기록.)
UPDATE scholarship
SET required_military_status = 'completed', required_discharge_type = 'officer_or_nco'
WHERE id = 652;
