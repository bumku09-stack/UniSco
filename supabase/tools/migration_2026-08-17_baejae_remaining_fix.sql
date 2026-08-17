-- 2026-08-17 배재대 재검증 나머지 정정 (156,157,159,164,166,171,1191,1192,1193,1199,1201,1203,1208,1209,1215)

BEGIN;

UPDATE scholarship
SET name = '특기입학장학금',
    amount_detail = '대상: 1년 등록금 전액, 1위: 최초학기 등록금 전액, 2위: 최초학기 등록금 50%(음악경연대회는 학과기준 적용)',
    min_gpa = 3.7,
    min_credits_last_semester = 15,
    description = '신입생 중 경연대회 입상자 대상(직전학기 평점평균 3.7 이상, 취득학점 15학점 이상 유지 시 지급, 소월문학상은 2018학년도 신입생에 한해 2년 등록금 전액 적용).'
WHERE id = 156;

UPDATE scholarship
SET amount_detail = '입학학기 등록금 전액 지원(재학 중에는 입상실적에 따라 추가 지급)',
    description = '체육특기자 전형 입학생 대상(입학 후 선수로 계속 활동하는 경우에 한함).'
WHERE id = 157;

UPDATE scholarship
SET amount_detail = '전적대학 성적 기준 등급별 차등 지원(교육연계과정 협정대학인 대덕대학·대전과학기술대학·대전보건대학·한국영상대학 연계교육과정전형 입학자는 성적 무관 첫 학기 전액 지급)'
WHERE id = 159;

UPDATE scholarship
SET description = '장애의 정도가 심한 장애인(1~3급, 2015년도 입학생부터) 또는 다문화가정 학생 대상(중복수혜 가능).'
WHERE id = 164;

UPDATE scholarship
SET min_gpa = 1.91,
    foreigner_eligibility = 'korean_only',
    description = 'TOEIC 900점 이상(영어 전공자는 950점 이상) 내국인 재학생 대상(1회에 한함, 지원일 기준 최근 6개월 이내 성적 인정).'
WHERE id = 166;

UPDATE scholarship
SET description = '전국교육회 산하 초·중·고등학교 교사의 자녀 대상.'
WHERE id = 171;

-- 2022학년도 정시모집 합격자(200만원) 항목만 원문으로 확인돼서 추가함 — 2021학년도 정시,
-- 2022학년도 수시 최초합격자의 정확한 금액은 이번엔 확인 못해서 손 안 댐(원문 재확인 필요)
UPDATE scholarship
SET amount_detail = '2022학년도 정시모집 합격자: 등록금(최초학기) 200만원
2022학년도 정시모집 추가모집 합격자: 200만원
2023학년도 수시모집 최초합격(대전·세종·충남·충북 소재 고교 졸업(예정)자): 등록금(최초학기) 150만원
2023학년도 수시모집 최초합격(그 외 지역): 등록금(최초학기) 100만원
2023학년도 정시 및 추가모집 합격자: 등록금(최초학기) 150만원',
    description = '2021~2023학년도 입학자 대상 신입생 장학금(전형·연도별 지급 기준 상이). 2024학년도 이후 입학자 기준은 원문에 없음.'
WHERE id = 1191;

UPDATE scholarship
SET amount_detail = '2025학년도 수시모집 최초합격자: 등록금(최초학기) 100만원
2025학년도 정시모집 합격자: 등록금(최초학기) 100만원
2026학년도 수시모집 최초합격자: 등록금(최초학기) 100만원
2026학년도 정시 및 추가모집 합격자: 등록금(최초학기) 100만원'
WHERE id = 1192;

UPDATE scholarship
SET description = '2025학년도 수시모집 또는 정시모집 합격자, 또는 2026학년도 수시모집 합격자 중 대학 연계 고교 3학년 부장 추천자 대상(중복수혜 가능).'
WHERE id = 1193;

UPDATE scholarship
SET amount_detail = '직전학기 3.0이상에서 1.0 향상 시 수업료 50만원, 2.0이상~3.0미만에서 1.0 향상 시 수업료 30만원, 2.0미만에서 1.0 향상 시 수업료 20만원, 2.0미만에서 2.0 향상 시 수업료 30만원'
WHERE id = 1199;

UPDATE scholarship
SET max_income_bracket = 8
WHERE id = 1201;

UPDATE scholarship
SET amount_detail = '학기 개시일부터 30일 이내 활동 시 미지급, 31~60일 활동 시 장학금액의 1/3, 61~90일 활동 시 1/2, 91일 이후 중단 또는 임기 만료 시 전액 지급'
WHERE id = 1203;

UPDATE scholarship
SET application_method = '별도 신청 절차 없음(재난 등 특별한 사유 발생 시 학교에 문의)'
WHERE id = 1208;

UPDATE scholarship
SET min_gpa = 2.5
WHERE id = 1209;

UPDATE scholarship
SET name = '천사장학금·후원의집장학금·불우학우면학장학금 등(기부금운용장학금)'
WHERE id = 1215;

COMMIT;
