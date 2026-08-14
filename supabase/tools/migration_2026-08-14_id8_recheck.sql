-- id=8 CNU Community Scholarship(신입생) 원문(plus.cnu.ac.kr) 재대조 반영
-- Honor Scholarship 1과 같은 표에서 나온 자매 장학금(인문·예체능계열용) — 제외학과는 없음(확인함)
UPDATE scholarship
SET
    amount_detail = '등록금 전액(학부/석·박사) + 학기당 750만원 학업장려금 + 기숙사 우선배정·비용지원 + 글로벌파견프로그램 우선선발. 1학년(2개 학기) 수료 전 자퇴 시 반납.',
    application_method = '자동선발 — 별도 신청 절차 없이 입시 성적 기준으로 선발(수시/정시 합격자 대상). 선발 여부는 등록금 고지서로 확인',
    admission_score_condition = '인문·예체능계열 신입생 중 수능 국·영·수·탐구(2개) 모두 3등급 이내, 평균 1.8등급 이내, 국어·영어 모두 1등급인 자 중 수능 합산 표준점수 최우수자',
    min_gpa_basis = 'cumulative',
    description = NULL
WHERE id = 8;
