-- 2026-08-17 재검증 2차 배치: 배재대 마감일 조작 정정 + 목원대 "2년차부터" 조작 정정
-- 배경: 8/16에 배재대 12건의 application_period를 고치면서 application_deadline은
-- 손대지 않고 남겨둠 — 그 12건 전부 옛날 잘못된 period 문구("2025-09-01~09-25")의
-- 꼬리였던 "2025-09-25"가 그대로 박혀있었음. 원문 어디에도 구체적 일자는 없음.

BEGIN;

-- 배재대 9건: 매 학기 반복 신청이 맞음 — 지어낸 마감일만 제거
UPDATE scholarship
SET application_deadline = NULL
WHERE id IN (161,162,163,164,166,167,169,170,171);

-- 배재대 3건: 실제로는 신입생 입학 시 1회성 장학금인데 "매 학기 신청"으로 잘못 분류돼 있었음
UPDATE scholarship
SET application_deadline = NULL,
    application_period = '입학 시'
WHERE id IN (155,156,160);

-- 목원대 5건: "재학 중 직전학기 평점평균 3.5 이상"이 원문 전체이고 "2년차부터"라는
-- 시점은 원문에 없음(신입생은 1학년 2학기부터 이미 "직전학기"가 생기므로 오히려
-- "2년차부터"라고 하면 학생이 실제보다 늦게 조건이 걸리는 걸로 오해함)
UPDATE scholarship
SET amount_detail = '4년간 등록금 전액+기숙사비 지원(직전학기 평점평균 3.5 이상 유지 조건)'
WHERE id = 189;

UPDATE scholarship
SET amount_detail = '1년 등록금 전액(직전학기 평점평균 3.5 이상 유지 조건)'
WHERE id = 192;

UPDATE scholarship
SET amount_detail = '4년 등록금 전액+학업장려금 연 320만원(직전학기 평점평균 3.5 이상 유지 조건)'
WHERE id = 193;

UPDATE scholarship
SET amount_detail = '4년 등록금 전액+연 120만원(직전학기 평점평균 3.5 이상 유지 조건)'
WHERE id = 194;

UPDATE scholarship
SET amount_detail = '4년 등록금 전액+연 80만원(직전학기 평점평균 3.5 이상 유지 조건)'
WHERE id = 195;

COMMIT;
