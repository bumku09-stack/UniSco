-- id=6 "대전 인재육성 장학사업"이 실제론 성격이 다른 4개 장학금(꿈돌이/과학/성취/외국인유학생)을
-- 한 행에 뭉쳐놓은 것이라 금액/선발인원/자격조건 구조화가 불가능했음 — 원문(daejeonyouthportal
-- CT_000000000501) 재확인 후 4개 행으로 분리. 2026년 세부 신청자격은 아직 공고 전(4월/9월
-- 공지 예정)이라 소득분위 등 커트라인은 여전히 빈칸으로 남김(원문에 없어서, 추측 금지).

-- 1) 기존 id=6 → 꿈돌이 장학금으로 좁힘
UPDATE scholarship
SET
    name = '꿈돌이 장학금(대전 인재육성)',
    amount = 5000000,
    amount_detail = '1인당 500만원',
    headcount = '5명',
    application_period = '선발일정 : 매년 4월 공지 예정 (2026년 기준)',
    application_method = '별도 공고 시 신청방법 안내 예정',
    description = '지역발전에 기여하고 모범이 되는 대학생 대상. 세부 자격조건(소득분위 등 커트라인)은 매년 4월 공고 시 확정 발표.'
WHERE id = 6;

-- 2) 과학 장학금 (자연과학·공과계열 신입생 전용)
INSERT INTO scholarship (
    name, provider, description, amount, amount_detail, headcount,
    application_url, application_period, application_method,
    eligible_region, category_l1, category_l2, major, min_grade, max_grade,
    grade_level, affiliated_institution
) VALUES (
    '과학 장학금(대전 인재육성)', '대전광역시',
    '학업성적 우수 등 사회의 모범이 되는 자연과학·공과계열 신입생 대상. 세부 자격조건(소득분위 등 커트라인)은 매년 4월 공고 시 확정 발표.',
    2000000, '1인당 200만원', '65명',
    'https://www.daejeonyouthportal.kr/content/CT_000000000501/cntPage.do',
    '선발일정 : 매년 4월 공지 예정 (2026년 기준)', '별도 공고 시 신청방법 안내 예정',
    '대전', 'school_external', 'local_gov', '자연과학계열, 공과계열', 1, 1,
    '확인 필요', '확인 필요'
);

-- 3) 성취 장학금 (대학생 몫만 — 고등학생은 우리 서비스 대상 아님, 558명은 고등학생+대학생 합산이라 대학생만의 정확한 인원은 원문에 없음)
INSERT INTO scholarship (
    name, provider, description, amount, amount_detail, headcount,
    application_url, application_period, application_method,
    eligible_region, category_l1, category_l2,
    grade_level, affiliated_institution
) VALUES (
    '성취 장학금(대전 인재육성, 대학생)', '대전광역시',
    '학업성적 우수 등 사회의 모범이 되는 대학생 대상(고등학생도 별도 지원 가능하나 대학생과 합산 정원이라 선발인원은 원문에 대학생만 따로 안 나와 있음, 전체 고등학생+대학생 합산 558명). 세부 자격조건(소득분위 등 커트라인)은 매년 9월 공고 시 확정 발표.',
    1500000, '1인당 150만원 (고등학생은 70만원, 대학생과 별도 트랙)', NULL,
    'https://www.daejeonyouthportal.kr/content/CT_000000000501/cntPage.do',
    '선발일정 : 매년 9월 공지 예정 (2026년 기준)', '별도 공고 시 신청방법 안내 예정',
    '대전', 'school_external', 'local_gov',
    '확인 필요', '확인 필요'
);

-- 4) 외국인 유학생 장학금
INSERT INTO scholarship (
    name, provider, description, amount, amount_detail, headcount,
    application_url, application_period, application_method,
    eligible_region, category_l1, category_l2, foreigner_eligibility,
    grade_level, affiliated_institution
) VALUES (
    '외국인 유학생 장학금(대전 인재육성)', '대전광역시',
    '학업성적 우수 등 사회의 모범이 되는 외국인 유학생 대상. 세부 자격조건(소득분위 등 커트라인)은 매년 9월 공고 시 확정 발표.',
    1500000, '1인당 150만원', '32명',
    'https://www.daejeonyouthportal.kr/content/CT_000000000501/cntPage.do',
    '선발일정 : 매년 9월 공지 예정 (2026년 기준)', '별도 공고 시 신청방법 안내 예정',
    '대전', 'school_external', 'local_gov', 'foreigner_only',
    '확인 필요', '확인 필요'
);
