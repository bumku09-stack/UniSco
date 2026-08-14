-- id=24 영탑 A 장학금(신입생) 원문(plus.cnu.ac.kr) 표 재대조
-- 다른 CNU 신입생 장학금들과 다르게 이건 "자동선발"이 아니라 학생과에 직접 서류 제출이 필요함
-- (application_period에 이미 마감일이 있었던 것도 그 증거).
UPDATE scholarship SET
    amount_detail = '등록금 전액',
    application_method = '직접 신청 필요 — 학생과에 서류 제출(정시 합격자는 별도 기한 적용)',
    headcount = '적격자',
    min_gpa_basis = 'semester',
    description = '장애의 정도가 심한 장애인 대상(장애 정도 구분은 우리 시스템에서 판단 못함 — 장애 등록 여부만 확인)'
WHERE id = 24;
