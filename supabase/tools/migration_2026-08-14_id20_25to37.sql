-- id=20, 25~37 CNU 신입생 표 나머지 항목 원문(plus.cnu.ac.kr, 이미 다운받은 표 텍스트/이미지로 재대조) 반영

UPDATE scholarship SET
    amount_detail = '입학금 및 등록금 일부(C급)',
    application_method = '자동선발 — 별도 신청 절차 없이 입시 성적 기준으로 선발',
    admission_score_condition = '입학성적우수자(성적우수·격려와 동일 기준, 구체적 커트라인은 원문에 없음)',
    headcount = '총장이 정하는 인원',
    description = NULL
WHERE id = 20;

UPDATE scholarship SET
    amount_detail = '등록금 일부(A급)',
    application_method = '직접 신청 필요 — 학생과에 서류 제출(정시 합격자는 별도 기한 적용)',
    headcount = '적격자',
    min_gpa_basis = 'semester',
    description = '장애의 정도가 심하지 않은 장애인 대상(장애 정도 구분은 우리 시스템에서 판단 못함 — 장애 등록 여부만 확인)'
WHERE id = 25;

UPDATE scholarship SET
    amount_detail = '등록금 전액',
    application_method = '자동선발 — 별도 신청 절차 없이 체육진흥원 추천 기준으로 선발',
    admission_score_condition = '체육진흥원 추천자',
    headcount = '적격자',
    min_gpa_basis = 'semester',
    description = NULL
WHERE id = 26;

UPDATE scholarship SET
    amount_detail = '등록금 전액',
    application_method = '자동선발 — 국제교류본부 추천 기준으로 선발',
    admission_score_condition = '6.25 유엔참전용사 후손(직계비속)임이 확인된 외국인 유학생(국제교류본부 추천자)',
    headcount = '적격자',
    description = NULL
WHERE id = 27;

UPDATE scholarship SET
    amount_detail = '등록금 일부(C급)',
    application_method = '자동선발 — 별도 신청 절차 없이 선발',
    admission_score_condition = '외국인 유학생',
    description = NULL
WHERE id = 28;

UPDATE scholarship SET
    amount_detail = '등록금 전액',
    application_method = '자동선발 — 별도 신청 절차 없이 선발',
    admission_score_condition = '한국어능력시험(TOPIK) 5급 이상 소지자',
    headcount = '적격자',
    language_test_type = 'TOPIK',
    language_test_min_score = 5,
    description = NULL
WHERE id = 29;

UPDATE scholarship SET
    amount_detail = '등록금 일부(B급)',
    application_method = '자동선발 — 별도 신청 절차 없이 선발',
    admission_score_condition = '한국어능력시험(TOPIK) 4급 소지자',
    headcount = '적격자',
    language_test_type = 'TOPIK',
    language_test_min_score = 4,
    description = NULL
WHERE id = 30;

-- id=31/32: TOPIK 또는 TOEFL/IELTS/TEPS/TOEIC 중 하나만 충족하면 되는 OR 조건인데
-- 우리 스키마(language_test_type 하나)는 이걸 표현 못함 — 구조화 필드는 비워두고
-- 원문 그대로 description에 남김(과소매칭 방지, matching_gaps.md에 기록 예정)
UPDATE scholarship SET
    amount_detail = '등록금 전액',
    application_method = '자동선발 — 별도 신청 절차 없이 선발',
    admission_score_condition = NULL,
    headcount = '적격자',
    description = '한국어능력시험(TOPIK) 5급 이상 또는 영어능력시험(TOEFL iBT 95점, IELTS 6.5, New TEPS 386점, TOEIC 800점 중 하나) 이상 소지자만 해당(여러 시험 중 하나만 충족하면 되는 조건이라 시스템에서 자동으로는 못 걸러냄)'
WHERE id = 31;

UPDATE scholarship SET
    amount_detail = '등록금 일부(B급)',
    application_method = '자동선발 — 별도 신청 절차 없이 선발',
    admission_score_condition = NULL,
    headcount = '적격자',
    description = '한국어능력시험(TOPIK) 4급 또는 영어능력시험(TOEFL iBT 71점, IELTS 5.5, New TEPS 327점, TOEIC 700점 중 하나) 이상 소지자만 해당(여러 시험 중 하나만 충족하면 되는 조건이라 시스템에서 자동으로는 못 걸러냄)'
WHERE id = 32;

UPDATE scholarship SET
    amount_detail = '등록금 전액(정규학기). 본인은 성적·지급학기 제한 없음.',
    application_method = '직접 신청 필요 — 학생과에 서류 제출(정시 합격자는 별도 기한 적용)',
    admission_score_condition = '국가유공자 본인 및 자녀',
    headcount = '적격자',
    min_gpa_basis = 'semester',
    description = NULL
WHERE id = 33;

UPDATE scholarship SET
    amount_detail = '등록금 전액(정규학기)',
    application_method = '직접 신청 필요 — 학생과에 서류 제출(정시 합격자는 별도 기한 적용)',
    admission_score_condition = '북한이탈주민',
    headcount = '적격자',
    min_gpa_basis = 'semester',
    description = NULL
WHERE id = 34;

UPDATE scholarship SET
    amount_detail = '등록금 전액 또는 일부',
    application_method = '학생 신청 대상 아님 — 학생자치기구 임원 등 특정 직위자를 학교가 직권으로 선발',
    admission_score_condition = '학생자치기구 임원 등',
    min_gpa_basis = 'semester',
    description = NULL
WHERE id = 35;

UPDATE scholarship SET
    amount_detail = '등록금 전액 또는 일부. 장학금 수혜학기에 최소 1학점 이상 수강해야 하며, 과정포기(자퇴 등) 시 전액 반납.',
    application_method = '자동선발 — 별도 신청 절차 없이 선발',
    admission_score_condition = '학·석사연계과정 석사과정 전일제 신입생',
    headcount = '총장이 정하는 인원',
    required_degree_level = 'masters',
    description = NULL
WHERE id = 36;

UPDATE scholarship SET
    amount_detail = '등록금 전액 또는 일부. 장학금 수혜학기에 최소 1학점 이상 수강해야 하며, 과정포기(자퇴 등) 시 전액 반납.',
    application_method = '자동선발 — 별도 신청 절차 없이 선발',
    admission_score_condition = '석·박사통합과정 전일제 신입생',
    headcount = '총장이 정하는 인원',
    required_degree_level = 'integrated_ms_phd',
    description = NULL
WHERE id = 37;
