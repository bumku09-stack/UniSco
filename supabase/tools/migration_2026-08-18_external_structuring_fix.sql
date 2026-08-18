-- 2026-08-18 외부(재단/지자체) 장학금 295건 구조화 점검 후 발견한 실제 누락분 반영
-- (소득분위 숫자/중위소득% 미변환, 이수학점 조건 미구조화, 백분위 성적 조건 신설)

BEGIN;

-- 백분위 성적(100점 만점) 조건 — min_score_percentile 신설 필드로 구조화
UPDATE scholarship SET min_score_percentile = 90 WHERE id = 173;  -- 서울인재대학장학금
UPDATE scholarship SET min_score_percentile = 80 WHERE id = 536;  -- 한국교총장학생(세종)
UPDATE scholarship SET min_score_percentile = 80 WHERE id = 537;  -- 한국교총장학생(대전)
UPDATE scholarship SET min_score_percentile = 80 WHERE id = 688;  -- 쌍용곰두리장학(성적우수)
UPDATE scholarship SET min_score_percentile = 60, min_credits_last_semester = 12 WHERE id = 1126;  -- 안산 반값등록금
UPDATE scholarship SET min_score_percentile = 90, min_credits_last_semester = 12 WHERE id = 1128;  -- 안산꿈키움 우수장학생
UPDATE scholarship SET min_score_percentile = 60, min_credits_last_semester = 12 WHERE id = 1130;  -- 산단노동자자녀장학금
UPDATE scholarship SET min_score_percentile = 60, min_credits_last_semester = 12 WHERE id = 1131;  -- 특별장학생(안산상공회의소)

-- 서울인재대학장학금 description에 내부 시스템 한계 설명 문구가 그대로 노출되고 있던 것 정리
UPDATE scholarship
SET description = '서울 소재 대학 재학 또는 서울시민의 자녀로 비서울 소재 대학 재학 중인 2학년 이상 학생 대상. 기초생활수급자/차상위/학자금지원 4구간 이하, 전체학기 평점 백분위 90점 이상. 연 200만원 1회 지급.'
WHERE id = 173;

-- 소득분위/중위소득% 미변환분 — 526·687은 원문에 분위 숫자가 그대로 있었음,
-- 686·999·663·1046은 "중위소득 N%"를 기존 확정 변환표(matching_gaps_resolved.md
-- 2026-08-07: 1구간≤30%,2≤50%,3≤70%,4≤90%,5≤100%,6≤130%,7≤150%,8≤200%,9≤300%)로 환산
UPDATE scholarship SET max_income_bracket = 6 WHERE id = 526;   -- 모범장학생(세종) — 6구간 이하(명시)
UPDATE scholarship SET max_income_bracket = 5 WHERE id = 687;   -- 포스코비전장학 — 소득5분위 이내(명시)
UPDATE scholarship SET max_income_bracket = 5 WHERE id = 686;   -- 빙그레 — 중위소득120%→보수적으로 5구간(100%)까지만 인정
UPDATE scholarship SET max_income_bracket = 3 WHERE id = 999;   -- 횡성 희망-성적우수 — 중위소득70%→3구간(id=1000과 동일조건, 이미 3구간으로 반영된 전례 따름)
UPDATE scholarship SET max_income_bracket = 3 WHERE id = 663;   -- 신한장학재단 로스쿨 — 학자금지원 3구간 해당자
UPDATE scholarship SET max_income_bracket = 6 WHERE id = 1046;  -- 희망드림장학금(인천) — 6구간 이하(명시)

-- 이수학점 조건이 원문에 숫자로 명시돼 있었는데 구조화 안 된 것
UPDATE scholarship SET min_credits_last_semester = 12 WHERE id = 521;   -- 재능장학금(대전청년내일재단)
UPDATE scholarship SET min_credits_last_semester = 12 WHERE id = 977;   -- 특기장학생(청송군)
UPDATE scholarship SET min_credits_last_semester = 24 WHERE id = 1000;  -- 인재육성장학금(희망-예능특기, 횡성)
UPDATE scholarship SET min_credits_last_semester = 24 WHERE id = 1005;  -- 향토인재육성장학금(이장자녀, 횡성)
UPDATE scholarship SET min_credits_last_semester = 12 WHERE id = 1101;  -- 특기장학금(충북인재평생교육진흥원)

-- 이미 원문 텍스트 안에 4.5만점 환산까지 해뒀는데 필드에는 안 옮겨져 있던 것
UPDATE scholarship SET min_gpa = 3.5 WHERE id = 1165;  -- 정읍시민장학재단 우수인재 장학금

COMMIT;
