-- min_credits(원문)는 있는데 min_credits_last_semester(구조화 숫자)가 비어서 필터링이 실질
-- 적용 안 되던 잔여 16건 재검토(matching_gaps.md 5번 후속). "직전학기 총 이수학점"과 같은
-- 개념으로 안전하게 숫자 하나로 옮길 수 있는 11건만 반영, 나머지 5건(다른 개념/애매한 시점
-- 조건)은 오판 위험이 있어 원문 텍스트만 유지하고 그대로 둠.

-- 순수 숫자만 있던 경우 (기존 12학점/15학점 등, 예외 조항 없음)
UPDATE scholarship SET min_credits_last_semester = 12 WHERE id = 683;   -- "12학점 이상"
UPDATE scholarship SET min_credits_last_semester = 12 WHERE id = 986;   -- "12학점"
UPDATE scholarship SET min_credits_last_semester = 12 WHERE id = 1067;  -- "12학점"
UPDATE scholarship SET min_credits_last_semester = 12 WHERE id = 1072;  -- "12학점"
UPDATE scholarship SET min_credits_last_semester = 12 WHERE id = 1076;  -- "12학점"
UPDATE scholarship SET min_credits_last_semester = 12 WHERE id = 1087;  -- "12학점"
UPDATE scholarship SET min_credits_last_semester = 12 WHERE id = 1089;  -- "12학점"
UPDATE scholarship SET min_credits_last_semester = 15 WHERE id = 1096;  -- "15학점"

-- 신입생/편입생 첫학기는 면제되는 경우 — 그 학생들은 애초에 "직전학기" 자체가 없어서
-- spec.credits_last_semester가 None으로 남고, credits_matches()의 기존 leniency(모르면
-- 통과)로 자동으로 걸러지지 않으므로 그냥 기본 숫자만 채워도 안전함(id=221/263/268/274
-- 재학생 예외 처리 선례와 같은 원리 — 더 낮은/면제 조건이 자연히 흡수됨).
UPDATE scholarship SET min_credits_last_semester = 12 WHERE id = 1042;  -- "12학점 이상(신입생·편입생·재입학생 첫학기는 면제)"
UPDATE scholarship SET min_credits_last_semester = 12 WHERE id = 1125;  -- "재학생: 12학점 이상(신입생은 학점 조건 없음)"

-- 추가 세부조건이 있지만 주 기준 숫자는 명확한 경우 — id=215 선례(F학점 조건은 구조화 안 하고
-- 원문에만 남김)와 동일하게, P/NP 제외 조건은 min_credits 원문에 그대로 남기고 주 숫자만 채움.
UPDATE scholarship SET min_credits_last_semester = 12 WHERE id = 1100;  -- "12학점 이상(P/NP 제외 평점산정과목 9학점 이상)"

-- 의도적으로 그대로 둠(원문 텍스트만 유지, DB 변경 없음):
-- id=294 — "동일학기 융복합전공 교과목 6학점 이상": 직전학기 총 이수학점과 다른 개념(특정
--   전공 교과목 학점). 2026-08-12에 이미 같은 이유로 제외 확정된 항목(선례 재확인).
-- id=651 — "1학년 24학점 이상 이수(과거 실적) + 해당학기 12학점 이상 신청": 서로 다른 두
--   개념(1학년 누적 실적 + 해당학기 신청 학점)이 합쳐진 복합 조건이라 숫자 하나로 못 줄임.
-- id=679, 680 — "해당학기 12학점 이상": "해당학기"가 완료된 직전학기 이수 학점인지, 그
--   학기에 신청(수강신청)하는 학점인지 원문만으로는 확정 못 함 — 후자면 시점 자체가 달라서
--   min_credits_last_semester(완료 기준)로 옮기면 오히려 잘못된 비교가 됨.
-- id=1116 — "연 30학점 이상(계절학기 제외)": "연"(1년) 단위 기준이라 "직전학기"(한 학기)와
--   다른 개념. 한 학기 30학점은 정상 수강신청 범위를 크게 초과해서, 그대로 옮기면 사실상
--   전원이 걸러지는 오류가 됨.
