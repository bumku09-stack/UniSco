-- 2026-08-15: "학군단(ROTC) 후보생만 대상" 장학금(id=63,212)이 기존 3종(군필/면제/미필)
-- 어디로도 안 걸러져서 추가. 군필이면 ROTC 후보생 신분 자체가 성립 안 하므로 기존 값과
-- 의미상 안 겹침(임관 전 학생만 해당). frontend/src/lib/spec.ts,
-- backend/app/models/enums.py의 MilitaryStatus 참고.
ALTER TYPE militarystatus ADD VALUE IF NOT EXISTS 'rotc_candidate';

-- id=63(학군사관후보생 해외연수 장학금), id=212(학군사관후보생장학금, 우송대) — 원문에
-- "학군단(ROTC) 후보생 대상"이라고 명확히 나와있는 2건만 반영. id=149/172는 ROTC가 여러
-- 자격 중 하나일 뿐(학생회 임원 등도 동일하게 해당)이라 required_military_status를 ROTC로
-- 좁히면 다른 자격으로 되는 학생들이 부당하게 걸러져서 손 안 댐.
UPDATE scholarship SET required_military_status = 'rotc_candidate' WHERE id IN (63, 212);
