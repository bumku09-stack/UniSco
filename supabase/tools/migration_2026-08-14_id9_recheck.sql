-- id=9 CNU Honor Scholarship 2(신입생) 원문(plus.cnu.ac.kr) 재대조 반영
-- 원문에 "수시 최종합격자" vs "정시 최초합격자"로 구분돼 있었는데 기존 DB는 뭉뚱그려
-- "수시·정시 최초합격자"로 잘못 적혀 있었음 — 정확한 표현으로 수정.
-- min_gpa_basis: 원문에 "(직전학기)"라고 명시된 건 Honor1/Community뿐이고 이 장학금은 그냥
-- "계속지급 평균평점"이라고만 나오는데, 같은 표의 다른 모든 장학금이 직전학기 기준이라
-- 동일 관례로 보고 semester로 판단.
UPDATE scholarship
SET
    amount_detail = '(취업)맞춤형 프로그램 제공 + 등록금 전액(학부) + 기숙사 우선배정·비용지원(최대 2년) + 학기당 100만원 학업장려금',
    application_method = '자동선발 — 별도 신청 절차 없이 입시 성적 기준으로 선발(수시 최종합격자·정시 최초합격자 대상). 선발 여부는 등록금 고지서로 확인',
    admission_score_condition = '학과별(수시 최종합격자 및 정시 최초합격자 중) 수능성적 우수자',
    min_gpa_basis = 'semester',
    description = NULL
WHERE id = 9;
