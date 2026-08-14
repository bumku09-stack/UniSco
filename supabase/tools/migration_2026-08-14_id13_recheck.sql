-- id=13 글로벌엘리트 C(신입생) 원문(plus.cnu.ac.kr) 재대조 반영
-- A/C는 의예·수의예·약학과 제외, B만 포함 — 원문에서 재확인함.
UPDATE scholarship
SET
    amount_detail = '등록금 전액 + 학기당 180만원 학업장려금 + 본교 일반대학원(석사) 진학 시 등록금 전액(4개 학기 지원) — 해외프로그램 혜택 없음(A/B와 차이점)',
    application_method = '자동선발(기본 혜택) — 별도 신청 절차 없이 입시 성적 기준으로 선발. 단, 대학원 진학 혜택은 본인이 직접 신청해야 함',
    admission_score_condition = '모집시기별(수시/정시), 계열별(인문계/자연계) 수능성적 우수자',
    excluded_major = '의예과, 수의예과, 약학과',
    min_gpa_basis = 'semester',
    description = NULL
WHERE id = 13;
