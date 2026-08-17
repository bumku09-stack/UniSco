-- 한국침례신학대학교 재검증(원문 재대조) 수정
-- 원문(mCode=MN303/MN310)을 다시 읽어보니 "자동선발"과 "매 학기 말 '보강 및 기말고사'
-- 기간 중(2026-12-08~12-21)"이라는 구체적 날짜/방식 문구는 두 페이지 어디에도 없음.
-- 실제 원문 근거: "재학생(2-4학년)들은 학기말 시험기간 내에 신청 할 수 있습니다",
-- "입학 전에 장학금을 신청하는 경우 장학공지에서 확인 후 신청바랍니다",
-- "다른 장학금의 경우 장학공지에서 수시로 신청받습니다" — 전부 "신청" 행위가 필요하다고
-- 나와있고, 자동선발이라는 말은 없음. CNU에서 발견된 것과 같은 유형의 문제.

-- 자동선발로 잘못 표시됐던 신입생 대상 6건 -> 입학 전 신청으로 정정
UPDATE scholarship SET
  application_period = '입학 전',
  application_method = '신청(장학공지 확인 후, 담임목사 추천 및 서류제출 필요)'
WHERE id = 322;

UPDATE scholarship SET
  application_period = '입학 전',
  application_method = '신청(장학공지 확인 후)'
WHERE id IN (344, 345, 347);

UPDATE scholarship SET
  application_period = '수시',
  application_method = '신청(장학공지 확인, 장학위원회 심의)'
WHERE id = 349;

UPDATE scholarship SET
  application_period = '수시',
  application_method = '신청(장학공지 확인 후)'
WHERE id = 364;

-- 근거 없는 특정 날짜(2026-12-08~12-21)/'보강 및 기말고사' 표현 -> 원문 표현인
-- "학기말 시험기간"으로 정정 (신청방식은 이미 맞게 들어가 있어 그대로 둠)
UPDATE scholarship SET
  application_period = '학기말 시험기간'
WHERE id IN (323, 324, 325, 326, 327, 328, 329, 330, 333, 334, 335, 336, 337, 338, 339, 343, 346, 348, 356, 362, 363);
