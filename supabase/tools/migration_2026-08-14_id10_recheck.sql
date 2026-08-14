-- id=10 MEGA CNU GLOBAL 장학금(신입생) 원문(plus.cnu.ac.kr) 재대조 반영
--
-- 발견 1: eligible_region='대전·충남·충북·세종'로 들어가 있었는데, 이건 "현재 거주지"가
--   아니라 "출신 고등학교 소재지" 조건임(원문: "대전·충남·충북·세종 소재 고등학교 졸업자").
--   eligible_region은 현재 거주지 전용 필드라 그대로 두면 오매칭(과소/과다 둘 다 가능) —
--   matching_gaps.md "14번 후속"에 이미 있는 패턴(hometown_school_region_condition 태그)으로
--   옮김.
-- 발견 2: 의예·수의예·약학과 제외 조건이 원문에 있었는데 비어있었음.
-- 발견 3: 학점 유지조건이 "직전학기 1.75 이상 그리고 전체누적 3.00 이상"으로 서로 다른 두
--   기준인데, 우리 스키마(min_gpa 하나)는 이걸 정확히 표현 못함 — 누적 3.0 기준으로 근사
--   처리하고 description에 정확한 원문 조건을 남겨둠(matching_gaps.md에도 새 갭으로 기록).
UPDATE scholarship
SET
    amount_detail = '1학년: 무료 어학교육 + 어학 시험응시료(TOEFL/IELTS) 지원. 2학년: 우수 해외대학 파견 400~800만원.',
    application_method = '자동선발 — 별도 신청 절차 없이 입시 성적 기준으로 선발',
    admission_score_condition = '[성적우수] 수능 영어영역 1등급 이내인 자 중 국어·수학 2개 영역 표준점수 합산 고득점자, 또는 [특성화] 학생부종합전형 Ⅰ·Ⅱ·Ⅲ 합격자 중 합격 차수별 순위가 높은 자',
    excluded_major = '의예과, 수의예과, 약학과',
    min_gpa_basis = 'cumulative',
    eligible_region = NULL,
    required_special_status = array_append(required_special_status, 'hometown_school_region_condition'),
    description = '출신 고등학교가 대전·충남·충북·세종 소재여야 함(현재 거주지 아님, 학생이 직접 확인 필요). 학점 유지조건은 직전학기 평균평점 1.75 이상 그리고 전체 누적 평균평점 3.00 이상을 모두 충족해야 함(시스템 매칭은 누적 3.0 기준으로만 판단).'
WHERE id = 10;
