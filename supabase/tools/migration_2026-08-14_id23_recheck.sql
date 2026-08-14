-- id=23 백마 장학금(복지)(신입생) 원문(plus.cnu.ac.kr) 표 재대조
-- "국가장학금 기준 준용"이라 정확한 소득분위 컷오프가 없음(국가장학금 자체 심사 결과에 연동) —
-- max_income_bracket에 임의 숫자 넣지 않음. 이연자/수업연한초과자 제외는 구조화 필드가 없어서
-- description에 그대로 남겨둠(노란색).
UPDATE scholarship SET
    amount_detail = '등록금 일부 (국가장학금 소득분위 기준에 따라 차등 지급)',
    application_method = '자동선발 — 별도 신청 절차 없이 국가장학금 신청 결과 기준으로 선발',
    admission_score_condition = NULL,
    headcount = '적격자',
    description = '이연자(등록유효복학자), 수업연한초과자는 제외됨'
WHERE id = 23;
