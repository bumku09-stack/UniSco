-- id=7 CNU Honor Scholarship 1(신입생) 원문(plus.cnu.ac.kr) 재대조 반영
-- 발견: 원문에 "의예·수의예·약학과 제외"가 명시돼 있었는데 excluded_major가 비어있었음.
-- "자연계열 신입생" 한정 조건도 admission_score_condition에 빠져 있었음.
UPDATE scholarship
SET
    amount_detail = '등록금 전액(학부/석·박사) + 학기당 750만원 학업장려금 + 기숙사 우선배정·비용지원 + 글로벌파견프로그램 우선선발. 1학년(2개 학기) 수료 전 자퇴 시 반납.',
    application_method = '자동선발 — 별도 신청 절차 없이 입시 성적 기준으로 선발',
    admission_score_condition = '자연계열 신입생 중 수능 국·영·수·탐구(2개) 모두 3등급 이내, 평균 1.8등급 이내, 수학·영어 모두 1등급인 자 중 수능 합산 표준점수 최우수자',
    excluded_major = '의예과, 수의예과, 약학과',
    min_gpa_basis = 'cumulative'
WHERE id = 7;
