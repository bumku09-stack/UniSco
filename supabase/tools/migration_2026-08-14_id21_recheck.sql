-- id=21 진학우수(일반대학원) 원문(plus.cnu.ac.kr) 표 재대조
-- 헤드카운트 "적격자"(기준 충족하면 정원 제한 없이 전원 지급) 표기, 대학원(석사) 과정임을
-- required_degree_level에 반영.
UPDATE scholarship SET
    amount_detail = '등록금 전액. 본교 학부(학사) 졸업 후 1년 이내 본교 일반대학원(석사) 입학 시 지원. 진학포기(자퇴 등) 시 반납.',
    application_method = '자동선발 — 별도 신청 절차 없이 학부 졸업 성적 기준으로 선발',
    headcount = '적격자',
    required_degree_level = 'masters',
    description = NULL
WHERE id = 21;
