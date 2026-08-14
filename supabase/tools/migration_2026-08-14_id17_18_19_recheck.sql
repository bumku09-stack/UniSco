-- id=17/18/19 (성적우수/학업증진/격려, 신입생) 원문(plus.cnu.ac.kr) 표 이미지로 직접 재대조.
-- 결론: 신입생 표에 실제로 존재하는 항목 맞음(재학생 표에도 동명이 따로 있지만 별개 장학금).
-- "계속지급 평균평점(직전학기)" 칸이 이 세 항목은 전부 빈칸(로스쿨학업증진/장려, 우수(대학원)도
-- 마찬가지) — 학점 유지조건 자체가 없는 것으로 확인(단순 데이터 누락이 아니라 원문이 빈칸).
UPDATE scholarship SET
    amount_detail = '등록금 전액',
    application_method = '자동선발 — 별도 신청 절차 없이 입시 성적 기준으로 선발',
    admission_score_condition = '입학성적우수자(구체적 커트라인은 원문에 없음)',
    headcount = '총장이 정하는 인원',
    description = NULL
WHERE id = 17;

UPDATE scholarship SET
    amount_detail = '등록금 일부(A급)',
    application_method = '자동선발 — 별도 신청 절차 없이 입시 성적 기준으로 선발',
    admission_score_condition = '입학성적우수자(성적우수와 동일 기준, 구체적 커트라인은 원문에 없음)',
    headcount = '총장이 정하는 인원',
    description = NULL
WHERE id = 18;

UPDATE scholarship SET
    amount_detail = '등록금 일부(C급)',
    application_method = '자동선발 — 별도 신청 절차 없이 입시 성적 기준으로 선발',
    admission_score_condition = '입학성적우수자(구체적 커트라인은 원문에 없음)',
    description = NULL
WHERE id = 19;
