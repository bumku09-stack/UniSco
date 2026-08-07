-- 외부(지자체/재단) 장학금 1차 배치 (2026-08-05) — 대전·충남·세종 지역
--
-- 출처: 공공데이터포털 "한국장학재단_학자금지원정보(대학생)_20260722" CSV
-- (supabase/tools/national_foundations_source_20260722.csv, 1,850건 중 대전/충남/세종
-- 34건을 색인으로 뽑아 병렬 조사 에이전트 6개로 각 기관 공식 홈페이지/공고와 대조 검증함.
-- 상세 조사 결과·판단 근거는 EXTERNAL_SCHOLARSHIPS_PLAN.md 2026-08-05 항목 참고.
--
-- 원문 모집기간은 대부분 2025년 사이클(이미 지남) 또는 아직 2026 하반기 공고 전이라,
-- application_deadline은 전부 NULL로 두고(matching_gaps.md 7번 관례 — 상시/반복 프로그램
-- 취급) application_period에 "매년 약 N월경(2025 기준: ...)" 형태로 참고용 텍스트만 남김.
--
-- 제외한 것들(넣지 않음, 이유는 EXTERNAL_SCHOLARSHIPS_PLAN.md 참고):
--   - 대전청년내일재단 "희망장학금": 2026년 선발계획에서 빠짐, 중단 추정
--   - 대전청년내일재단 "거주비지원장학금"/"청년희망장학금": 2026 하반기 공고 아직 미발표, 판단 보류
--   - 대전청년내일재단 "과학 장학생": 이미 마감 확인됨(2026-05-29), 별도 조사 없이 제외
--   - 대전광역시서구인재육성장학재단 7건 전부: 재단 공식 페이지가 2022년 이후 갱신 안 된
--     정황 + 7건 중 5건은 공식 페이지에서 프로그램명 자체를 확인 못함 — 서구청
--     자치행정과(042-288-2783) 전화 확인 후 재시도 필요
--   - 충남평생교육진흥원 "아름드리장학생": 대학생 대상이 **아님** — 공식 페이지
--     (clehrd.or.kr/clehrd/sub02_06_01.do) 직접 확인 결과 "취약계층·아동보육시설·쉼터
--     청소년 등" 대상이며 "대학생은 명시적으로 포함되지 않고 고등학생 이하로 한정"됨.
--     ("시설 소속·추천 필요"라는 조건 자체는 새로운 유형이 아니라 SpecialStatus의
--     child_care_facility로 이미 표현 가능 — 처음에 "새로운 유형이라 매칭 불가"로 잘못
--     적었던 걸 정정함. 진짜 제외 사유는 대상 연령대가 대학생이 아니라는 것뿐.)
--   - 충청남도 예산군청 "대학 학자금 대출이자 지원": 2024년 이후 신규 공고·뉴스 전혀 없어
--     운영 여부 불확실 — 담당부서(041-339-7239) 전화 확인 필요
--   - 충남평생교육진흥원 "재능키움장학생", 세종연구원 "학자금원금상환지원장학"·
--     "대학생학자금대출이자지원": 기존 DB에 이미 있는 항목과 중복 확인되어 제외
--
-- 실행 방법: python run_sql.py ../data_national_foundations.sql (또는 run_sql.py에서 상대경로 맞춰 실행)

INSERT INTO scholarship (name, provider, description, amount, application_url, min_age, max_age, required_gender, eligible_region, required_military_status, max_income_bracket, min_gpa, min_gpa_basis, requires_disability, required_disability_type, foreigner_eligibility, language_test_type, language_test_min_score, required_special_status, application_deadline, grade_level, major, affiliated_institution, min_credits, admission_score_condition, headcount, application_period, eligible_university, eligible_college, required_enrollment_status, min_grade, max_grade, required_degree_level, category_l1, category_l2) VALUES

-- ===== 대전청년내일재단 (dhrdf.or.kr → daejeonyouthportal.kr로 통합됨) =====

('꿈돌이장학금', '재단법인 대전청년내일재단', '리더십을 갖추고 자기주도 프로젝트 계획을 마련한 학생 대상. 자기주도 역량기술서(기존 성취 90%+계획 10%)로 평가. 공고일 기준 본인이 1년 이상 계속 대전광역시에 주소를 둔 학생만 해당(본인 기준, 부모 거주는 인정 안 됨 — 다른 대전청년내일재단 장학금과 다른 점). 징계(정학 이상) 처분자, 타 지역 전학자 제외.', 5000000, 'http://www.dhrdf.or.kr', NULL, NULL, NULL, '대전', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, '5명', '매년 4월경 모집(2026년 기준: 2026-04-08 ~ 2026-04-30, 신청 마감 지남 — 2027년 재모집 예상)', NULL, NULL, NULL, NULL, NULL, NULL, 'school_external', 'local_gov'),

('재능장학금', '재단법인 대전청년내일재단', '실적인정기간 내 인문사회/과학/예체능 등 분야 국제 및 전국대회 3위 이내 입상 + 학교장 추천. 직전학기 12학점 이상 수강. 공고일 기준 6개월 전부터 대전광역시에 주민등록상 주소를 둔 학생. 징계·타도시 전학·허위기재 시 제외, 휴학생/수료생/초과학기/직전학기 1학점 미만 취득자 제외. ※선발인원은 대학생만 5명이라는 CSV 자료와 초중고 전체 35명(2,450만원)이라는 2026년 선발계획 문서 수치가 서로 달라 확인 중 — 대학생 몫으로는 5명이 유력하나 원문 재확인 권장.', 1500000, 'http://www.dhrdf.or.kr', NULL, NULL, NULL, '대전', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, '9학점 이상', '5명(대학생 기준 추정 — 전체 35명 중 일부, 확인 필요)', '매년 4월경 모집(2026년 기준: 2026-04-08 ~ 2026-04-30, 신청 마감 지남)', NULL, NULL, NULL, NULL, NULL, NULL, 'school_external', 'local_gov'),

('성취장학금', '재단법인 대전청년내일재단', '1학년: 고3 2학기 내신 2등급 이상 또는 검정고시 90점 이상 + 대학 1학기 평점 B+ 이상. 2~4학년: 직전학기까지 전체 평균 평점 B+ 이상. 공고일 기준 6개월 전부터 대전광역시에 주민등록상 주소를 둔 학생, 학교장 추천. 휴학생/수료생/초과학기/직전학기 12학점 미만, 정학 이상 징계자, 2025년도 대학교 전액장학금 수혜자 제외.', 1500000, 'http://www.dhrdf.or.kr', NULL, NULL, NULL, '대전', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, 'B+ 이상(구체적 만점 기준 미확인)', '74명(대학생 기준)', '매년 9월경 모집(2025년 기준: 2025-09-10 ~ 2025-10-02)', NULL, NULL, NULL, NULL, NULL, NULL, 'school_external', 'local_gov'),

-- ===== 충남평생교육진흥원 (cninjae.or.kr, 최근 clehrd.or.kr / "충남평생교육인재육성진흥원"으로 개칭) =====

('거주비지원 장학생(천안행복기숙사)', '충남평생교육진흥원', '천안행복기숙사에 2026년 1~6월 기간 내 입사 중이거나 입사 예정인 대학생 대상. 최대 60만원(2025년 거주비 증빙 내역 150만원 이하일 경우 실비 지급, 기숙사 식대 제외). 공고일 기준 본인 또는 부모가 충남에 1년 이상 주민등록(2026년부터 본인만→본인 또는 부모로 대상 확대됨). 장기 입사생/저학년/고령 순 선발. 대학교 졸업/휴학/대학원생은 신청 시 제외.', 600000, 'https://www.clehrd.or.kr', NULL, NULL, NULL, '충남', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, '80명', '매년 3~4월경 모집(2026년 기준: 2026-03-20 ~ 2026-04-07, 신청 마감 지남)', NULL, NULL, 'undergrad_enrolled', NULL, NULL, NULL, 'school_external', 'local_gov'),

('학자금대출이자지원사업(충남)', '충남평생교육진흥원', '2015년 이후 한국장학재단 일반·취업후상환 학자금대출(등록금·생활비)을 받은 청년 대상, 최근 1년간 발생 대출이자 전액 지원(한국장학재단 대출금 상환계좌로 상환, 개인계좌 입금 안 됨). 공고일 기준 본인 또는 부모가 주민등록초본상 충청남도에 1년 이상 계속 주소지. 대출이자 발생액·대출원금·고령 순 선발. 타 기관·지자체 동일사업 중복수혜자 제외.', NULL, 'https://www.clehrd.or.kr', NULL, NULL, NULL, '충남', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, '900명(예정)', '매년 9월경 모집(2025년 기준: 2025-09-01 ~ 2025-09-26, 2025년 실제 공고로 확인됨)', NULL, NULL, NULL, NULL, NULL, NULL, 'school_external', 'local_gov'),

('충남사랑장학생', '충남평생교육진흥원', '공고일 기준 충남 소재 대학 2~4학년 재학생. 한국장학재단 학자금 지원구간 2구간 이하. 경제상황(50%)+학업성적(45%)+봉사활동(5%) 심사. 공고일 기준 본인이 충청남도에 2년 이상 중도 이탈 없이 계속 거주(부모 거주는 인정 안 됨 — 본인만). 2026년도 진흥원 장학사업 중복 신청·선발 대상자, 휴학생·수료상태(졸업유예 포함) 제외. ※2026년엔 대학 1학년 대상 "2차"(7.8~7.22) 라운드가 별도로 추가 운영됨 — 이 항목은 2~4학년 대상 "1차" 기준.', 3600000, 'https://www.clehrd.or.kr', NULL, NULL, NULL, '충남', NULL, 2, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, '100명', '매년 4월경 모집(2026년 기준: 2026-04-15 ~ 2026-04-29, 신청 마감 지남)', NULL, NULL, 'undergrad_enrolled', 2, 4, NULL, 'school_external', 'local_gov'),

-- ===== 세종연구원(sri.re.kr, 구 세종인재육성평생교육진흥원 sjhle.or.kr 통합됨) — "핵심인재육성"·"무지개" 장학사업 =====

('모범장학생(세종)', '재단법인 세종연구원', '한국장학재단 소득분위 6구간 이하 또는 국민기초생활수급자·차상위계층. 공고일 기준 1년 이상 세종시 계속 거주자(부·모 또는 본인). 소득배점 고득점자 선발(동점자: 세종시 관내 학교 재학+거주 동시충족 > 거주기간 긴 순 > 고학년 순). 휴학생·수료생 지원 불가. "디딤돌 장학사업" 브랜드 소속.', 1000000, 'https://www.sri.re.kr', NULL, NULL, NULL, '세종', NULL, 6, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, '43명', '매년 5~7월경 모집(2026년 기준: 2026-05-06 ~ 2026-07-10, 신청 마감 지남)', NULL, NULL, 'undergrad_enrolled', NULL, NULL, NULL, 'school_external', 'local_gov'),

('장애인 면학 장학생(세종)','재단법인 세종연구원','신체·지적·발달 등 장애인으로 등록된 학생. 국민기초생활보장법상 기준 중위소득 150% 이하 가정. 세종시 관내 대학 재학 또는 공고일 기준 1년 이상 세종시 계속 거주(부/모 또는 본인). 소득배점 고득점자 선발(동점자: 장애 정도 심한 순 > 세종시 관내 재학+거주 동시충족 > 거주기간 긴 순). 초/중/고/대학생 통합 선발 31명 중 일부(대학생 몫 별도 확인 안 됨). 휴학생·수료생 지원 불가.',1000000,'https://www.sri.re.kr',NULL,NULL,NULL,'세종',NULL,NULL,NULL,NULL,TRUE,NULL,NULL,NULL,NULL,'{}',NULL,NULL,NULL,NULL,NULL,NULL,'31명(초/중/고/대학생 통합)','매년 5~7월경 모집(2026년 기준: 2026-05-06 ~ 2026-07-10, 신청 마감 지남)',NULL,NULL,'undergrad_enrolled',NULL,NULL,NULL,'school_external','local_gov'),

('다문화가정·북한이탈주민 장학생(세종)','재단법인 세종연구원','다문화가족지원법 제2조·제14조의2 해당 다문화가정, 또는 북한이탈주민의 보호 및 정착지원에 관한 법률 제2조1항 해당 북한이탈주민. 국민기초생활보장법상 기준 중위소득 150% 이하 가정. 세종시 관내 대학 재학 또는 공고일 기준 1년 이상 세종시 계속 거주(부/모 또는 본인). 초/중/고/대학생 통합 선발 31명 중 일부. 휴학생·수료생 지원 불가.',1000000,'https://www.sri.re.kr',NULL,NULL,NULL,'세종',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'{multicultural_family,north_korean_defector}',NULL,NULL,NULL,NULL,NULL,NULL,'31명(초/중/고/대학생 통합)','매년 5~7월경 모집(2026년 기준: 2026-05-06 ~ 2026-07-10, 신청 마감 지남)',NULL,NULL,'undergrad_enrolled',NULL,NULL,NULL,'school_external','local_gov'),

('특기적성장학생(세종)','재단법인 세종연구원','신청시작일로부터 1년 이내 4차산업/체육·무용/음악·미술/문학·발표경연 등 특기분야 전국 규모 이상 대회 3위 이내 입상. 세종시 관내 대학 재학 또는 신청시작일 기준 1년 이상 세종시 계속 거주(부/모 또는 본인). 수상실적 배점(70%)+소득배점(30%) 합산 고득점자 선발. 학과장 또는 학부장 추천 필요. "핵심인재육성장학사업" 소속. 대회 입상 실적은 UserSpec으로 확인 불가한 조건.',1500000,'https://www.sri.re.kr',NULL,NULL,NULL,'세종',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'{}',NULL,NULL,NULL,NULL,NULL,NULL,'35명(초/중/고/대학생 통합)','매년 8~9월경 모집(2026년 기준: 2026-08-10 ~ 2026-09-30, 접수 진행 중일 수 있음)',NULL,NULL,'undergrad_enrolled',NULL,NULL,NULL,'school_external','local_gov'),

('공익발전기여 장학생(세종)','재단법인 세종연구원','국가유공자 등 예우 및 지원에 관한 법률 제4조의 국가유공자 본인 또는 자녀, 또는 의사상자 등 예우 및 지원에 관한 법률 제3조의 의사상자 본인 또는 자녀. 세종시 관내 중/고/대학 재학 또는 공고일 기준 1년 이상 세종시 계속 거주(부·모 또는 본인). 국가유공자 사망자 자녀 > 상이등급 높은 순 > 재학+거주 동시충족 > 거주기간 긴 순으로 선발. 중/고/대 학교급별 1회 수혜 시 제외.',1000000,'https://www.sri.re.kr',NULL,NULL,NULL,'세종',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'{national_merit}',NULL,NULL,NULL,NULL,NULL,NULL,'5명(중/고/대학생 통합)','매년 5~7월경 모집(2026년 기준: 2026-05-06 ~ 2026-07-10, 신청 마감 지남)',NULL,NULL,'undergrad_enrolled',NULL,NULL,NULL,'school_external','local_gov'),

('장애인 특기적성 장학생(세종)','재단법인 세종연구원','신체·지적·발달 등 장애인으로 등록된 학생, 신청시작일 기준 1년 이내 전국 규모 이상 대회 3위 이내 입상. 세종시 관내 대학 재학 또는 신청시작일 기준 1년 이상 세종시 계속 거주(부·모 또는 본인). 수상실적(70%)+소득배점(30%) 고득점자 선발. 학과 또는 학부장 추천 필요. "무지개 장학사업" 소속. 대회 입상 실적은 UserSpec으로 확인 불가한 조건.',1500000,'https://www.sri.re.kr',NULL,NULL,NULL,'세종',NULL,NULL,NULL,NULL,TRUE,NULL,NULL,NULL,NULL,'{}',NULL,NULL,NULL,NULL,NULL,NULL,'8명(초/중/고/대학생 통합)','매년 5~7월경 모집(2026년 기준: 2026-05-06 ~ 2026-07-10, 신청 마감 지남)',NULL,NULL,'undergrad_enrolled',NULL,NULL,NULL,'school_external','local_gov'),

-- ===== 지자체 학자금대출 이자지원 (5개 시/군, 전부 확인 결과 운영 중) =====

('대학생학자금대출이자지원(아산)', '충청남도 아산시청', '2016년 2학기 이후 한국장학재단에서 받은 학자금대출(등록금·생활비, 취업후상환/일반상환)의 최근 반기 발생 이자 지원(한국장학재단 대출금 상환계좌로 상환, 개인계좌 입금 안 됨). 공고일 기준 본인 또는 직계존속이 아산시에 1년 이상 계속 주민등록, 만 30세 미만 재학생·휴학생. 졸업생·대학원생 제외. 매 반기(상반기·하반기)마다 별도 공고.', NULL, 'https://www.asan.go.kr', NULL, 30, NULL, '충남', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, '기관확인필요', '매 반기 모집(2026년 상반기 기준: 2026-03-25 ~ 2026-04-22)', NULL, NULL, NULL, NULL, NULL, NULL, 'school_external', 'local_gov'),

('학자금대출 이자지원(당진)', '충청남도 당진시청', '2016년 2학기 이후 한국장학재단 학자금대출(취업후상환/일반상환) 받은 대학생(휴학생 포함) 대상, 최근 반기 발생 이자(생활비 제외) 지원(대출금 상환계좌로 상환). 공고일 기준 본인 또는 직계존속이 당진시에 1년 이상 주민등록. 소득분위 8분위 이하만 지원 가능하나, **다자녀(3자녀 이상) 가정은 소득분위 무관하게 지원**(CSV 원문엔 없던 조건, 실제 공고에서 확인). 대학교 졸업생/수료생/제적생/자퇴생·대학원생, 대출 전액 상환자 제외.', NULL, 'https://www.dangjin.go.kr', NULL, NULL, NULL, '충남', NULL, 8, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{multi_child_family}', NULL, NULL, NULL, NULL, NULL, NULL, '기관확인필요', '매년 9월경 모집(2025년 기준: 2025-09-01 ~ 2025-09-26)', NULL, NULL, NULL, NULL, NULL, NULL, 'school_external', 'local_gov'),

('학자금대출 이자지원 사업(대전)', '대전광역시청', '한국장학재단에서 대출받은 학자금의 최근 발생 본인부담 이자(또는 이자에 해당하는 원금 상환분) 지원(대출계좌로 상환, 개인 계좌 입금 안 함). 한국장학재단 대출받은 만 18~55세 대학(원)생. 대전지역 대학 재학이면 거주지 무관, 대전 외 대학이면 본인 또는 직계존속이 1년 이상 대전시 주민등록 필요. 대출 완납자, 이자면제 대상, 타 지자체 중복지원자, 대학원 수료자, 졸업유예자 제외. 2026년도 예산 약 1억 6,250만원, 약 1,100명 지원 규모로 확인됨.', NULL, 'http://www.daejeon.go.kr', 18, 55, NULL, '대전', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, '약 1,100명', '매년 2~3월경 모집(2026년 기준: 2026-02-27 ~ 2026-03-27, 신청 마감 지남)', NULL, NULL, NULL, NULL, NULL, NULL, 'school_external', 'local_gov'),

('대학생 학자금대출 이자지원(천안)', '충청남도 천안시청', '학자금 대출 당시 한국장학재단 소득분위 1~8분위인 자. 2017년부터 한국장학재단에서 대출받은 학자금의 최근 반기 발생 이자 전액(대출계좌로 상환, 개인계좌 입금 안 됨). 대학교 재·휴학생 및 졸업 후 2년 내 미취업자. 본인의 현재 주민등록상 주소가 천안이거나 직계존속 1인의 주소가 1년 이상 천안. 대학원생, 대출 전액 상환자, 타 기관 중복지원자 제외.', NULL, 'http://www.cheonan.go.kr', NULL, NULL, NULL, '충남', NULL, 8, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, '기관확인필요', '매년 1월경 모집(2026년 기준: 2026-01-09 ~ 2026-01-26, 신청 마감 지남)', NULL, NULL, NULL, NULL, NULL, NULL, 'school_external', 'local_gov'),

-- ===== 한국교총장학회 (한국교원단체총연합회 산하, 지역별 배정 운영) =====

('한국교총장학생(세종)', '세종특별자치시교원단체총연합회', '고등교육법 제2조에 규정된 학교(대학·전문대·사이버대·대학원 등 포함) 재학 중인 한국교총 회원(순직·사망회원 포함)의 자녀. 전년도 평균 학업성적 80점 또는 B학점 이상(신입생은 고3 또는 검정고시 성적 기준). 사회적 배려계층(기초생활수급자·탈북 새터민 등)은 별도 고려. 세종 배정 2명. 정식 명칭은 "한국교총장학회"(대전교총과 별개 지역 배정).', 1000000, 'https://www.sjfta.or.kr', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, '평균 80점 또는 B학점 이상', '2명', '매년 8월 말경 모집(2025년 기준: 2025-08-25 ~ 2025-09-12, 2026년 공고는 8월 하순 예상)', NULL, NULL, NULL, NULL, NULL, NULL, 'school_external', 'association'),

('한국교총장학생(대전)', '대전광역시교원단체총연합회', '고등교육법 제2조에 규정된 학교(대학·전문대 등) 재학 중인 한국교총 회원(순직·사망회원 포함)의 자녀. 전년도 평균 학업성적 80점 또는 B학점 이상(2~4학년 위주 선발). 사회적 배려계층(기초생활수급자·탈북새터민 등)은 별도 고려. 군복무 휴학 후 복학생은 복무 전 2학기 성적 기준으로 지원 가능. 선발인원 2명, 연 50만원.', 500000, 'http://www.dfta.or.kr', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, '평균 80점 또는 B학점 이상', '2명', '매년 8월경 모집(2025년 기준: 2025-08-18 ~ 2025-09-11, 2026년 공고는 8월경 예상)', NULL, NULL, NULL, NULL, NULL, NULL, 'school_external', 'association');
