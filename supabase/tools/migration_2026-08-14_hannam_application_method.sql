-- 한남대 37건: application_period에 들어있던 "자동선발" 등 신청방식 정보를
-- application_method로 분리 (금액/기간/신청방식/자격조건 4블록 완성)

UPDATE scholarship SET application_method = '자동선발', application_period = NULL
WHERE id IN (216,217,218,219,220,222,225,226,227,228,229,230,231,232,233,234,235,236,237,240,242,243,244,245,246,247,248,249,250,251,252);

UPDATE scholarship SET application_method = '자동선발', application_period = '매 학기 초'
WHERE id = 221;

UPDATE scholarship SET application_method = '모집 공고 후 신청', application_period = '매년 6~7월'
WHERE id = 223;

UPDATE scholarship SET application_method = '봉사시간 인증 후 선발', application_period = '매 학기 말'
WHERE id = 224;

UPDATE scholarship SET application_method = '신청', application_period = '매년 1학기 초 공고'
WHERE id = 238;

UPDATE scholarship SET application_method = '신청', application_period = '매년 1학기 초 공고(2019~2026학년도 매년 반복 확인됨)'
WHERE id = 239;

UPDATE scholarship SET application_method = '신청', application_period = '매년 1학기 초 공고(2021~2026학년도 매년 반복 확인됨)',
  min_grade = 1, max_grade = 1, foreigner_eligibility = 'korean_only'
WHERE id = 241;
