-- 외부(재단/공공기관) 장학금 2차 배치 (2026-08-05) — 전국 대상(지역 무관/특정 시군 조건)
--
-- 출처: 공공데이터포털 "한국장학재단_학자금지원정보(대학생)_20260722" CSV
-- (supabase/tools/national_foundations_source_20260722.csv). 1차 배치(대전·충남·세종
-- 지자체)에 이어, 대기업/유명 재단·공공기관 위주로 전국 대상 후보 약 80건을 추려
-- 병렬 조사 에이전트 7개로 각 기관 공식 홈페이지/뉴스와 대조 검증함. 상세 판단 근거는
-- EXTERNAL_SCHOLARSHIPS_PLAN.md 2026-08-05(2차 배치) 항목 참고.
--
-- 시/군 단위 거주 조건이 있는 것들(한국수력원자력 5건·강원랜드 2건·빙그레 1건·포스코 1건)은
-- 2026-08-05에 만든 시/군/구 단위 매칭(matching_gaps.md 14번)을 그대로 활용 — "지역이
-- 대전·충남이 아니라서" 빼지 않고, eligible_region을 정확한 시/군 이름으로 채워서 그 동네
-- 사는 학생(본인 또는 부모)한테만 정확히 매칭되도록 함.
--
-- 원문 모집기간은 대부분 지난 사이클이라(대부분 2025년 또는 이미 지난 2026년 상반기),
-- application_deadline은 전부 NULL로 두고(matching_gaps.md 7번 관례) application_period에
-- "매년 약 N월경(최근 기준: ...)" 형태로 참고용 텍스트만 남김.
--
-- 확실히 제외한 것(9건, 지역/대학 무관하게 우리 서비스와 아예 안 맞음):
--   - 현대자동차그룹 계약학과(산학장학생)/연구장학생: 서울대·연세대·한양대 특정 학과 한정
--   - 고촌재단(종근당) 생활비장학생/무상기숙사장학생: "서울 소재 대학" 한정
--   - 대상문화재단 장학사업(동남아 학생): 서울대 한정
--   - 현대차 정몽구 재단 글로벌 장학생: 서울대 "본교" 한정
--   - 삼성꿈장학재단 희망장학생: 기존 "꿈장학생"만 이어받는 폐쇄형(신규 지원 불가)
--   - DB드림마스터장학생: 기존 특정 프로그램(동하리 등) 수료자만 대상인 폐쇄형
--   - 포스코청암재단 포스코사이언스펠로십: 학생이 아니라 교수(신진교수) 대상
--
-- 조사 결과 추가로 제외/보류한 것:
--   - 삼성꿈장학재단 글로벌희망장학생: 협약대학이 전부 서울/거점국립대급, 우리 대학 미포함
--   - 롯데장학재단 희망장학생: 지정대학 13개 전부 서울/경기권, 우리 대학 미포함
--   - 롯데장학재단 국학우수인재 장학금: 최신(2025~2026) 공고를 못 찾음, 운영 여부 불확실
--   - DB드림서포트장학생: 재단 현재 사업 목록에서 빠짐, 운영 중단 추정
--   - 방일영문화재단 방일영장학생/탈북장학생: 협약대학이 전부 수도권, 우리 대학 미포함 추정
--   - 국가보훈부 보훈장학금(특수교육장학): 대학생이 아니라 초중고 특수교육대상자용
--   - 국가보훈부 독립유공자 후손 장학금(스타벅스코리아): 2026년 스타벅스 논란으로 사업
--     재검토 중, 2026년 사이클 미운영 확인됨
--   - IBK다문화사랑: CSV 설명과 달리 고1 대상 사업일 가능성 있어 재확인 전까지 보류
--   - 국립국제교육원 일본 정부(문부과학성) 장학금: CSV 설명과 정확히 일치하는 공고를
--     재확인 못함(다른 유형 프로그램과 혼동 가능성)
--   - KT그룹희망나눔재단 창의혁신리더장학금: "KT디지털인재 장학생"과 같은 프로그램의
--     구 명칭으로 추정되어 중복 방지차 하나만(KT디지털인재 장학생) 등록
--   - 아산사회복지재단 의생명과학분야대학장학생: "아산재단에서 선정한 대학"의 3·4학년
--     한정이라 애초에 조사 대상에서 제외
--
-- ⚠️참고(등록은 했지만 확정 아닌 것): 아산재단 "북한이탈청소년장학생"은 충남대만 지정대학
-- 포함 여부 잠정 확인(재단 공식 목록 미확인), 관정재단 학부/대학원장학생은 충남대·KAIST만
-- 확인(나머지 대학은 참여 여부 불명이라 제외), 수림재단 신규장학생은 15개 지정대학 중
-- KAIST만 포함. 새울원자력본부는 2026년 "희망미래 장학생"으로 통합 운영되는 것으로 보여
-- 기존 4개 세부 구분(일반/지역/우대/특별) 대신 1건으로 통합 등록함(세부구분 유지 여부
-- 원문 미확인).
--
-- 새로 발견된 자격조건 유형: IBK행복나눔재단 "고립·은둔청년"·"가족돌봄청년"은 지금까지
-- 없던 완전히 새로운 유형 — 매칭 필드가 없어 description 텍스트로만 남김(★엄밀히는
-- "자립준비청년(보호종료아동)" 부분만 기존 child_care_facility로 부분 표현됨). 그 외
-- "군인/소방/경찰공무원 자녀"(아산MIU자녀장학생)는 기존 16번 갭(부모 직업/소속 조건)에
-- 해당하는 이미 알려진 유형, "특정 명문대 화이트리스트"·"총장 추천 필요" 조건들은 기존
-- eligible_university 필드로 이미 표현 가능해서 새 갭이 아님(조사 에이전트가 처음엔
-- "새로운 유형"이라 보고했으나 재검토로 정정함).
--
-- 실행 방법: python run_sql.py ../data_national_foundations_2.sql

INSERT INTO scholarship (name, provider, description, amount, application_url, min_age, max_age, required_gender, eligible_region, required_military_status, max_income_bracket, min_gpa, min_gpa_basis, requires_disability, required_disability_type, foreigner_eligibility, language_test_type, language_test_min_score, required_special_status, application_deadline, grade_level, major, affiliated_institution, min_credits, admission_score_condition, headcount, application_period, eligible_university, eligible_college, required_enrollment_status, min_grade, max_grade, required_degree_level, category_l1, category_l2) VALUES
('아산MIU자녀장학생', '(재단법인)아산사회복지재단', '군인·소방·경찰 공무원 자녀(사회배려대상자) 대상. 전체 학업성적 평점 3.5/4.5 이상인 학생. 국내 대학·전문대학 재학 중 정규학기에 등록한 재학생. 학업격려금 성격으로 국가장학금·교내장학금과 중복수혜 가능. 기관(소속 공무원 부서) 추천 필요. 제적·정학 등 징계자, 군 휴학 제외 휴학/질병 등 학업중단자 제외.', 4000000, 'http://www.asanfoundation.or.kr', NULL, NULL, NULL, NULL, NULL, NULL, 3.5, NULL, NULL, NULL, NULL, NULL, NULL, '{parent_occupation_condition}', NULL, NULL, NULL, NULL, NULL, NULL, '90명(계속 신청자 포함)', '매년 12월경 모집(2026년 기준: 2025-12-01 ~ 2025-12-24)', NULL, NULL, 'undergrad_enrolled', NULL, NULL, NULL, 'school_external', 'private_foundation'),

('의생명과학분야대학원장학생', '(재단법인)아산사회복지재단', '국내대학 석/박사과정·석박사통합과정 입학예정자 또는 재학생 중 의과학·생명과학 등 의생명과학 분야 연구자(소속 전공학과·연령·성별 제한 없음). 대한민국 국적 보유자. 성적 평점 4.0/4.5(4.3만점 3.82) 이상. 연 2000만원(학기당1000만원) 정액지원, 교내장학금·조교장학금(FA/TA/RA) 중복수혜 가능. 지도교수 추천 필요. 해외영주권자·이중국적자, 교내징계, 학업중단자 제외.', 20000000, 'https://www.asanfoundation.or.kr', NULL, NULL, NULL, NULL, NULL, NULL, 4.0, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '매년 10월경 모집(2025년 기준: 2025-10-02 ~ 2025-10-27)', NULL, NULL, NULL, NULL, NULL, 'masters', 'school_external', 'private_foundation'),

('해외의생명과학분야대학원장학생', '(재단법인)아산사회복지재단', '외국대학의 석사·박사·석박사통합과정 입학예정자 또는 재학생 중 의생명과학 분야 연구자(전공학과·유학국가·연령·성별 제한 없음). 대한민국 국적 보유자. 성적 3.82/4.3(4.0만점 3.55) 이상. 연 최대4000만원(학기당2000만원), 학교 위치 국가별 차등 지원. 지도교수 추천서 필요. 해외영주권자·이중국적자 제외.', 40000000, 'https://www.asanfoundation.or.kr', NULL, NULL, NULL, NULL, NULL, NULL, 3.55, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '매년 10월경 모집(2025년 기준: 2025-10-02 ~ 2025-10-27, 2026년 사이클 재확인 권장)', NULL, NULL, NULL, NULL, NULL, 'masters', 'school_external', 'private_foundation'),

('북한이탈청소년장학생', '(재단법인)아산사회복지재단', '정부기관의 보호결정을 받은 북한이탈청소년 중 재단이 지정한 전국 4년제 대학에 재학 중으로 2·3·4학년 진학 예정인 대학생. 전체 학업성적 평점과 직전학기 평점이 모두 3.0 이상. 학기당300만원(연600만원), 재단 지정 오리엔테이션·장학증서 수여식·봉사캠프 등 참여 필수. 지도교수 추천. ⚠️재단 지정 대학 목록 공식 확정은 못했으나 충남대학교가 자체 게시판에 이 공고를 직접 게시하고 있어 포함 가능성 높음(잠정) — eligible_university를 충남대학교로 한정.', 6000000, 'https://www.asanfoundation.or.kr', NULL, NULL, NULL, NULL, NULL, NULL, 3.0, NULL, NULL, NULL, NULL, NULL, NULL, '{north_korean_defector}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '매년 10월경 모집(2025년 기준: 2025-10-02 ~ 2025-10-27)', '충남대학교', NULL, 'undergrad_enrolled', 2, 4, NULL, 'school_external', 'private_foundation'),

('보건의료정책분야대학원장학생', '(재단법인)아산사회복지재단', '국내대학의 석사·박사·석박사통합과정 입학예정자 또는 재학생 중 보건의료정책분야를 연구하는 대학원생. 대한민국 국적 보유자. 성적 4.0/4.5(3.82/4.3) 이상. 연 1000만원(학기당500만원) 정액지원, 교내장학금·조교장학금 중복수혜 가능. 지도교수 추천 필요.', 10000000, 'https://www.asanfoundaton.or.kr', NULL, NULL, NULL, NULL, NULL, NULL, 4.0, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '매년 10월경 모집(2025년 기준: 2025-10-02 ~ 2025-10-27)', NULL, NULL, NULL, NULL, NULL, 'masters', 'school_external', 'private_foundation'),

('관정재단 학부장학생', '관정이종환교육재단', '2026년 1학기 기준 5학기(3학년1학기) 진학 예정, 대한민국 국적으로 대한민국 고등학교 졸업, 만24세 이하. 학부1~3학기 총평균평점 4.0/4.5(3.8/4.3) 이상. 관정성적우수장학금(A형, 학기당600만원)/관정학업장려장학금(B형, 학기당400만원) 중 선택, 최대4학기. 대학 총장 추천 필요(재단이 지원하는 대학만 해당). 편입생 제외. ⚠️충남대학교 참여 확인(학부 5명, 자연이공4/인문사회1 배정) — 나머지 9개 대학 참여 여부는 미확인.', 6000000, 'https://www.ikef.or.kr/', NULL, NULL, NULL, NULL, NULL, NULL, 4.0, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, '5명(자연이공4명/인문사회1명)', '매년 10~11월경 모집(2025년 기준: 2025-10-28 ~ 2025-11-28)', '충남대학교', NULL, 'undergrad_enrolled', 3, 3, NULL, 'school_external', 'private_foundation'),

('관정재단 대학원장학생', '관정이종환교육재단', '대한민국 국적 보유자로서 대한민국 고등학교 졸업, 일반대학원 석사/석박사통합/박사과정 입학예정자·재학생. 前과정 총평균평점 4.0/4.5(3.8/4.3) 이상. 학기당600만원, 최대4학기. 대학 총장 추천 필요. 일반대학원 이외 과정(MBA·전문대학원·특수대학원 등) 제외, 타 민간재단 장학금 중복수혜 불가. ⚠️KAIST 참여 확인(학과별 최대2명) — 나머지 9개 대학 참여 여부는 미확인.', 6000000, 'https://www.ikef.or.kr', NULL, NULL, NULL, NULL, NULL, NULL, 4.0, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, '학과별 최대 2명', '매년 10월~다음해 3월경 모집(2025년 기준: 2025-10-28 ~ 2026-03-06)', 'KAIST', NULL, NULL, NULL, NULL, 'masters', 'school_external', 'private_foundation'),

('인재림 장학', '(재)한국고등교육재단', '대한민국 국적 보유자(복수국적 가능), 전국 4년제 대학 2~3학년(편입생은 이전 학교 성적증명서 제출). 프로그램 교육비 전액 지원+장학금800만원+Design Thinking Project 활동비(팀별200만원, 우수팀200만원 추가). 연중 학부생 자격 유지 필수, 어학연수·교환학생·취업·군복무로 인한 프로그램 중단 불가. 연 1~2회 기수 모집(2025년 5기 10~11월, 6기 4~5월 마감 확인).', 8000000, 'http://www.kfas.or.kr', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, '20명 내외', '연 1~2회 모집(2025년 기준: 5기 2025-10-28~11-24, 6기 2026-04-20~05-11 마감)', NULL, NULL, 'undergrad_enrolled', 2, 3, NULL, 'school_external', 'private_foundation'),

('문우림 장학', '(재)한국고등교육재단', '대한민국 국적 보유자(이중국적/시민권자 가능), 4년제 대학교 학부 2~3학년(2개 학기 이상 이수, 계절학기 불포함). 평균학점 3.5/4.5 이상. 연간800만원 장학금(타 기관과 중복수혜 가능)+2년간 재단 연수 프로그램 교육비 전액 지원. 학과 교수 또는 수업 담당 강사 추천(선택). 2년간 연수 프로그램 참여 가능해야 함(어학연수·교환학생·군복무로 중단 불가).', 8000000, 'https://apply.kfas.or.kr', NULL, NULL, NULL, NULL, NULL, NULL, 3.5, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, '10명 내외', '매년 10~11월경 모집(2025년 기준: 2025-10-01 ~ 2025-11-10)', NULL, NULL, 'undergrad_enrolled', 2, 3, NULL, 'school_external', 'private_foundation'),

('동아시아연구장학생', '(재)한국고등교육재단', '대한민국 국적 소유자, 국내 대학원 석사과정 재학생·수료생(박사 진학 희망자) 또는 박사과정 재학자. 본인의 연구에 한문 자료가 필요한 자. 박사과정 연간1200만원/석사과정 연간1000만원(국내 대학원 등록금 실비 지원, 최대5년). 서류심사+필기고사+면접평가. 지도교수 추천 필요.', 12000000, 'http://www.kfas.or.kr', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '매년 6~7월경 모집(2026년 기준: 2026-06-23 ~ 2026-07-13)', NULL, NULL, NULL, NULL, NULL, 'masters', 'school_external', 'private_foundation'),

('동교인재 장학생', '(재)수림재단', '국내 4년제 이상 대학의 최종 학년 재학생(휴학생 포함)으로서 재학 중 성취한 탁월한 공적으로 타의 모범이 되고 대학의 명예 선양·발전에 크게 기여한 개인. 대상500만원/금상300만원/은상100만원(1회성 포상, 학자금 이중지원 대상 아님). 서류전형+면접, 서류 합격 시 소속 대학 학과장 또는 지도교수 추천서 제출.', 5000000, 'http://www.surim.or.kr/', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, '20명 이내', '매년 9~10월경 모집(2025년 기준: 2025-09-01 ~ 2025-10-17)', NULL, NULL, 'undergrad_enrolled', NULL, NULL, NULL, 'school_external', 'private_foundation'),

('수림재단 신규장학생', '(재)수림재단', '자연과학계열 평가 우수 15개 대학(GIST·KAIST·UNIST·건국대·경희대·고려대·동국대·서강대·서울대·성균관대·연세대·이화여대·중앙대·포스텍·한양대) 2학년 재학생. 5개 자연과학 전공(물리·화학·생물·수학·의예과) 및 관련 공학계열. 대학 1학년 전체 평균 85점 이상(100점 환산), 1학년 24학점 이상 이수, 2026학년도 1학기 12학점 이상 신청. 학자금 지원구간 8구간 이내. 생활지원금 연간480만원(매월40만원). 대학 추천 필요.', 4800000, 'http://www.surim.or.kr/', NULL, NULL, NULL, NULL, NULL, 8, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, '10명', '매년 3~4월경 모집(2026년 기준: 2026-03-01 ~ 2026-04-30)', 'KAIST', NULL, 'undergrad_enrolled', 2, 2, NULL, 'school_external', 'private_foundation'),

('제대군인대부지원(나라사랑대출)', '국가보훈부', '국가보훈부에 등록된 10년 이상 장기복무 제대군인 대상 학자금 대부. 학기당500만원 한도 내 실제소요(입학금·수업료) 금액 지원, 연이율4.0%, 상환기간5년. 전국 국민은행·농협은행 영업지점에서 상시 신청. 한국장학재단 학자금 지원사업과 이중 수혜 시 일시상환 조치됨.', NULL, 'https://www.mpva.go.kr/', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '상시 신청 가능(연중)', NULL, NULL, NULL, NULL, NULL, NULL, 'support_fund', 'youth_living_support'),

('보훈장학금(대학원장학)', '국가보훈부', '국가보훈법령에 따라 교육지원을 받는 국가유공자 본인·배우자·자녀(전몰/순직군경/순직공무원/4·19혁명사망자 등), 고엽제후유의증환자, 5·18민주운동부상자 등. 대학원 석/박사과정 재학, 직전학기 성적 80점 이상. 학기당 최고130만원(실납부 수업료 한도). 대학원 정규 첫 학기 신입생, 수업연한 초과자 제외. 연 2회(1학기 4월, 2학기 9월) 모집.', 1300000, 'https://www.mpva.go.kr', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '연 2회 모집(1학기 4월, 2학기 9월 — 2학기 기준: 2026-09-01 ~ 2026-09-30)', NULL, NULL, NULL, NULL, NULL, 'masters', 'school_external', 'national_scholarship'),

('보훈장학금(대학장학)', '국가보훈부', '6·25 전몰군경자녀의 자녀(손자녀) — 1953-07-27 이전 및 관련 법률 별표 전투기간 중 전사·순직한 국가유공자의 손자녀. 직전학기 성적 70점 이상(신입생 제외). 학기당 최고100만원. 재학 중인 학교 수업연한 초과자, 당해학기 본인납부 수업료 없는 경우 제외. 연 2회(1학기 4월, 2학기 9월) 모집.', 1000000, 'https://www.mpva.go.kr', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '연 2회 모집(1학기 4월, 2학기 9월 — 2학기 기준: 2026-09-01 ~ 2026-09-30)', NULL, NULL, 'undergrad_enrolled', NULL, NULL, NULL, 'school_external', 'national_scholarship'),

('북한이탈주민대학생 교육지원금', '남북하나재단', '국내 고등학교 졸업 또는 동등 이상 학력을 인정받은 북한이탈주민과 자녀. 국·공립대학 등록금100% 면제/사립대학 등록금50% 보조(최초 입학일로부터 6년 범위 내 최대8학기). 전적대학 포함 직전2학기 연속 평균70점(C학점) 미만 시 다음학기 보조 제한. 의무교육 이수 필요. 한국장학재단 국가장학금과 중복 불가. 각 모집대학에 증빙자료 제출.', NULL, 'http://www.koreahana.or.kr', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{north_korean_defector}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '매년 3~5월경 모집(2026년 기준: 2026-03-19 ~ 2026-05-18)', NULL, NULL, 'undergrad_enrolled', NULL, NULL, NULL, 'school_external', 'national_scholarship'),

('통일미래장학생', '남북하나재단', '북한출생 4년제 대학 재학생(만35세 미만). 직전학기 평점 최저점수 이상(3.0/4.5, 2.7/4.3, 2.5/4.0). 700만원(연2회 지급). 서류심사(가구소득/성적 등)+다대다 그룹 면접. 선발 후 성적 최저점수 미달 시 제외, 휴학생·정규학기 초과자 제외.', 7000000, 'http://www.koreahana.or.kr', NULL, NULL, NULL, NULL, NULL, NULL, 3.0, NULL, NULL, NULL, NULL, NULL, NULL, '{north_korean_defector}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '매년 3~4월경 모집(2026년 기준: 2026-03-23 ~ 2026-04-10, 2026년 상반기 이미 선발완료)', NULL, NULL, 'undergrad_enrolled', NULL, NULL, NULL, 'school_external', 'national_scholarship'),

('남북하나재단 일반장학생', '남북하나재단', '모집공고 마감일 현재 국내 대학(일반·전문·산업·교육·기술·기능대학) 및 원격대학(방송통신·사이버대학) 재학생인 북한이탈주민(재단 내 등급 구분상 "일반" 등급 — 일반 국민 전체 대상 아님, 북한이탈주민 지원 전담 프로그램). 200만원. 자격검증+면접심사. 휴학 중이거나 정규학기 초과자, 직전6개월 600만원 초과 장학금 수혜자 제외.', 2000000, 'http://www.koreahana.or.kr', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{north_korean_defector}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '매년 3~4월경 모집(2026년 기준: 2026-03-23 ~ 2026-04-10, 2026년 상반기 이미 선발완료)', NULL, NULL, 'undergrad_enrolled', NULL, NULL, NULL, 'school_external', 'national_scholarship'),

('만학도장학생', '남북하나재단', '대학생 1~4학년 중 1991-01-01 이전 출생(만35세 이상)인 북한이탈주민. 200만원. 자격검증+면접심사. 휴학 중이거나 정규학기 초과자, 직전6개월 600만원 초과 장학금 수혜자 제외.', 2000000, 'http://www.koreahana.or.kr', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{north_korean_defector}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '매년 3~4월경 모집(2026년 기준: 2026-03-23 ~ 2026-04-10)', NULL, NULL, 'undergrad_enrolled', 1, 4, NULL, 'school_external', 'national_scholarship'),

('신격호 롯데 취업준비생 장학사업', '롯데장학재단', '국내 4~6년제 대학 정규학기 2학기 이상 수료자 또는 졸업 후 1년 이내 미취업자. 언론/미디어 분야(PD·기자·아나운서·기획마케팅 등) 취업 희망자. 총(평균)평점 3.0/4.5 이상. 최근학기 한국장학재단 학자금지원구간 통지서 제출 가능자(0~10구간). 100만원(1회 지급, 생활비 명목)+현장직무 체험형 프로그램. 250명(2026년 7기 기준, 기존 500명에서 축소). 단과대 학장·학과장 추천서 제출 시 가산점.', 1000000, 'http://www.lottefoundation.or.kr/', NULL, NULL, NULL, NULL, NULL, NULL, 3.0, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, '250명', '매년 5~6월경 모집(2026년 7기 기준: 마감 2026-06-22)', NULL, NULL, NULL, NULL, NULL, NULL, 'school_external', 'private_foundation'),

('DB드림리더장학금', '재단법인 DB김준기문화재단', '전국 4년제 대학교 학부 5~6학기(3학년)인 자(전공 무관). DB드림리더 활동에 1년간 우선순위를 두고 참여 가능한 학생. 성적 누적평점 B0 이상. 한국장학재단 학자금 지원구간 8구간 이하 우대. 생활비 장학금 학기당300만원. 학과장 또는 지도교수 이상의 추천 필요. 2026년 1학기 휴학 불가, 중복지원 불가.', 3000000, 'https://www.dbfoundation.or.kr', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '매년 12월~다음해 1월경 모집(2026년 기준: 2025-12-17 ~ 2026-01-09)', NULL, NULL, 'undergrad_enrolled', 3, 3, NULL, 'school_external', 'private_foundation'),

('북한배경대학생 어학교육지원', '재단법인 DB김준기문화재단', '북한/제3국 출생 북한이탈주민 대학생 및 대학원생. 2개월간 파고다어학원 정규강의 수강료 전액 지원+학습성취도·출석률에 따른 소정의 장학금+영어시험 비용 지원. 40명 내외.', NULL, 'https://www.dbfoundation.or.kr', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{north_korean_defector}', NULL, NULL, NULL, NULL, NULL, NULL, '40명 내외', '매년 5~6월경 모집(2026년 2차 기준: 2026-05-11 ~ 2026-06-19)', NULL, NULL, NULL, NULL, NULL, NULL, 'school_external', 'private_foundation'),

('신한장학재단 신규장학생', '재단법인 신한장학재단', '2026년도 대학교 입학예정자. 수능성적 4개 영역(국어·수학·영어·탐구) 중 3개 영역 이상 4등급 이내 또는 고교 내신 이수과목 1/2 이상 4등급 이내(탐구는 2과목 평균). 기초생활수급자·차상위계층 또는 기타 생활·학업 여건이 어려운 학생. 연간600만원(전액 학업보조비, 등록금 지원 없음). 학교 담임교사(자립준비청년은 기관 선생님) 추천 필요. 한국장학재단·교내장학금 이외 타 재단 장학금 수령 시 제외.', 6000000, 'http://www.shsf.or.kr', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '매년 12월~다음해 1월경 모집(2026년 기준: 2025-12-22 ~ 2026-01-15)', NULL, NULL, 'undergrad_enrolled', 1, 1, NULL, 'school_external', 'private_foundation'),

('신한장학재단 생활장학금', '재단법인 신한장학재단', '대한민국 법학전문대학원 재학생. 기초생활수급권자·차상위계층 또는 한국장학재단 학자금 지원 3구간 해당자. 400만원(학기당200만원). 1차 서류심사+2차 온라인 면접. 40명. 충남대학교 법학전문대학원 재학생도 대상.', 4000000, 'http://www.shsf.or.kr', NULL, NULL, NULL, NULL, NULL, 3, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, '40명', '매년 3~4월경 모집(2026년 기준: 2026-03-30 ~ 2026-04-09)', '충남대학교', '법학전문대학원', NULL, NULL, NULL, NULL, 'school_external', 'private_foundation'),

('희망나래(자립준비청년 등)', 'IBK행복나눔재단', '19~34세 이하 청년 중 자립준비청년(조기보호종료·보호종료 아동), 고립·은둔청년(구직단념/사회구성원과 갈등 등으로 고립·은둔 상황), 가족돌봄청년(장애·질병 등으로 가족을 돌보는 청년) 중 하나에 해당. 생활비형 장학금300만원+금융경제교육/취업컨설팅. 520명. 사업신청→1차선정자발표→서류제출→최종합격자발표→취업캠프 순. "고립·은둔청년"·"가족돌봄청년"은 지금까지 없던 새로운 유형의 자격조건 — 자립준비청년(보호종료아동)만 기존 child_care_facility 카테고리로 부분 표현 가능, 나머지 2유형은 구조화된 매칭 필드 없음.', 3000000, 'http://www.ibkfoundation.or.kr/', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{child_care_facility}', NULL, NULL, NULL, NULL, NULL, NULL, '520명', '매년 8월경 모집(2025년 기준: 2025-08-01 ~ 2025-08-29)', NULL, NULL, NULL, NULL, NULL, NULL, 'support_fund', 'youth_living_support'),

('IBK장학생', 'IBK행복나눔재단', '연간 근로소득 7천만원 이하의 중소기업 근로자·소상공인 본인 및 미혼의 자녀(외국인근로자·다문화가족 포함). 대학교 재학생. 기업의 기부 참여 여부에 따라 240~300만원 차등 지급. 대기업/공공기관 임원 및 근로자, 중소·중견기업 대표자 및 등기임원, 휴학생, 국외 소재 학교 학생, 대학원생 지원 불가.', 3000000, 'http://www.ibkfoundation.or.kr/', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '매년 3월경 모집(2026년 기준: 2026-03-19 ~ 2026-03-27)', NULL, NULL, 'undergrad_enrolled', NULL, NULL, NULL, 'school_external', 'private_foundation'),

('KT디지털인재 장학생', 'KT그룹희망나눔재단', '국내 대학 재학생 중 AI·빅데이터·컴퓨터공학 등 ICT관련 전공자. 선발일 기준 대한민국 국적 보유자, 학칙에 의한 징계사실 없는 자. 누적학점 평균 4.5만점 3.5이상(4.3만점 3.3이상). 선발시점부터 정규학기 졸업 시까지 잔여학기 등록금 전액 지원. 1차 서류심사+2차 면접(1차 통과 시 교수추천서 필요). 직전학기 12학점 미만 이수자, 수혜기간 중 휴학예정자(군복무 제외) 제외. 전국 대학 대상(특정 협약 대학 한정 아님). ※구 "창의혁신리더장학금"과 같은 프로그램의 개편된 명칭으로 추정 — 중복 방지를 위해 이 명칭으로만 등록.', NULL, 'https://ktgf.or.kr/', NULL, NULL, NULL, NULL, NULL, NULL, 3.5, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '매년 1월경 모집(2026년 기준: 2026-01-14 ~ 2026-01-30)', NULL, NULL, 'undergrad_enrolled', NULL, NULL, NULL, 'school_external', 'private_foundation'),

('대학생 생활비 장학금', '(재)유한재단', '생활이 어려운 결손 및 다문화 가정 학부 재학생, 학자금 지원구간 5구간 이하. 직전학기 평점평균 2.5 이상, 12학점 이상 이수. 연600만원(연2회 각300만원, 생활비성). 결손 또는 다문화가정 입증 서류 제출, 추천 필요.', 6000000, 'http://www.yuhanfoundation.or.kr', NULL, NULL, NULL, NULL, NULL, 5, 2.5, NULL, NULL, NULL, NULL, NULL, NULL, '{multicultural_family}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '매년 3월경 모집(2026년 기준: 2026-03-16 ~ 2026-03-18, 신청기간 짧음)', NULL, NULL, 'undergrad_enrolled', NULL, NULL, NULL, 'school_external', 'private_foundation'),

('유한재단 전액장학생(등록금 장학금)', '(재)유한재단', '2026학년도 1학기 재학 예정인 학부생. 학업 성적이 우수하고 가정형편이 어려워 학비보조가 필요한 학생. 다문화가정·한부모가정·저소득가정 우선순위 선발. 등록금 전액(등록금/수업료/학생회비/졸업비 등). 추천서 필요.', NULL, 'http://www.yuhanfoundation.or.kr', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '매년 12월경 모집(2025년 기준: 2025-12-22 ~ 2025-12-29)', NULL, NULL, 'undergrad_enrolled', NULL, NULL, NULL, 'school_external', 'private_foundation'),

('우리다문화장학재단 학업장학', '우리다문화장학재단', '다문화가족 자녀, 국내 2·3·4년제 대학교 재학생·휴학생. 2026년 기준 중위소득 100% 이하 가구. 현재 학기 포함 졸업까지 3학기 이상 남은 학생. 매월 1회 이상 대학 장학생 서포터즈 "우리누리" 활동 필수 참여. 500만원(2회 분할 지급). 소속대학 총장·학과장/다문화 및 사회복지기관장/지자체·주민센터장 추천 필요. 외국인 및 북한이탈주민 지원불가. 전 학령(초중고대) 통합 연간 1,000명 선발 중 일부(대학생 몫 별도 확인 안 됨).', 5000000, 'http://www.woorifoundation.or.kr', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{multicultural_family}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '매년 3~4월경 모집(2026년 기준: 2026-03-23 ~ 2026-04-17)', NULL, NULL, NULL, NULL, NULL, NULL, 'school_external', 'private_foundation'),

('우리다문화장학재단 특기장학', '우리다문화장학재단', '특기 및 재능 보유 다문화가족 자녀(8~30세). 예체능·어학 특기자/자격·기술보유자/직업진로 특기자 등. 최근3년 이내 전국 규모 이상 대회 입상실적 또는 상응하는 특기·재능 실적자료 제출 가능해야 함. 학교 재학 여부 무관(졸업생·학교밖청소년도 가능). 500만원. 약30명. 소속대학 학교장·총장(지도교수·학과장 포함)/다문화 및 사회복지기관장/지자체·주민센터장/특기재능 관련 전문기관장 추천 필요. 부모 모두 외국국적 가족 및 북한이탈주민 지원불가.', 5000000, 'http://www.woorifoundation.or.kr', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{multicultural_family}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '매년 3~4월경 모집(2026년 기준: 2026-03-23 ~ 2026-04-17)', NULL, NULL, NULL, NULL, NULL, NULL, 'school_external', 'private_foundation'),

('숲과나눔 인재양성 프로그램(석·박사과정)', '재단법인 숲과나눔', '환경·안전·보건 관련 분야 석·박사과정 입학예정자 및 재학생(국내 대학원). 등록금+학습지원비(월20만원). 전공이해도·성장가능성·지속가능성·학업계획·활동경력 등 종합평가. 학자금대출·타기관장학금·교내장학금·BK21 등 등록금 관련 중복수혜 불가.', NULL, 'https://koreashe.org', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '매년 10~11월경 모집(2026년 기준: 2025-10-20 ~ 2025-11-06)', NULL, NULL, NULL, NULL, NULL, 'masters', 'school_external', 'private_foundation'),

('숲과나눔 인재양성 프로그램(글로벌리더십)', '재단법인 숲과나눔', '환경·안전·보건 관련 분야 석·박사과정(대학원), 개발도상국 국적자로 국내 대학 유학예정자 및 유학생. 등록금+항공료+생활지원비(월120만원). 전공이해도 등 종합평가. 교수 추천 필요.', NULL, 'https://koreashe.org', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '매년 10~11월경 모집(2026년 기준: 2025-10-20 ~ 2025-11-06)', NULL, NULL, NULL, NULL, NULL, 'masters', 'school_external', 'private_foundation'),

('숲과나눔 인재양성 프로그램(공익활동가)', '재단법인 숲과나눔', '환경·안전·보건 관련 분야 석·박사과정(대학원), 비영리 공익단체 10년 이상 상근활동가 중 입학예정자 및 재학생. 등록금+학습지원비(월20만원). 단체장 추천 필요.', NULL, 'https://koreashe.org', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '매년 10~11월경 모집(2026년 기준: 2025-10-20 ~ 2025-11-06)', NULL, NULL, NULL, NULL, NULL, 'masters', 'school_external', 'private_foundation'),

('숲과나눔 인재양성 프로그램(생물다양성 분야)', '재단법인 숲과나눔', '생물다양성 분야 전공 대학원(석·박사과정) 입학예정자 및 재학생. 등록금+학습지원비(월20만원).', NULL, 'https://koreashe.org', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '매년 10~11월경 모집(2026년 기준: 2025-10-20 ~ 2025-11-06)', NULL, NULL, NULL, NULL, NULL, 'masters', 'school_external', 'private_foundation'),

('브루나이 정부초청 장학', '국립국제교육원', '2026.7.1 기준 25세 이하(학부)/35세 이하(대학원)의 영어 능통자(GCEO 6학점 또는 IGCSE C등급 또는 IELTS 6.0 또는 TOEFL 550점 이상 중 택1). 학비면제+왕복항공료+생활비+식비+서적구입비. 국립국제교육원 자체 선발.', NULL, 'https://www.niied.go.kr/web/main/nid/niied_board/5522', NULL, 35, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '매년 12월~다음해 2월경 모집(2026년 기준: 2025-12-31 ~ 2026-02-15)', NULL, NULL, NULL, NULL, NULL, NULL, 'school_external', 'association'),

('문화예술인재학부장학금', '현대차 정몽구 재단', '음악·무용 전공 국내 대학교 재학생·휴학생(1~3학년). 가구 중위소득150% 이하. 등록금 전액+학습지원비+국제콩쿠르 장학금+글로벌 우수 장학금+해외 진출 장학생 장학금+마스터클래스 및 연주기회(온드림 앙상블). 1차 서류·영상심사, 2차 온라인 인성검사, 3차 실기검사. 해당 전공자 외 지원불가.', NULL, 'http://www.hyundaicmkfoundation.org/', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, '35명 내외', '매년 3~4월경 모집(2026년 기준: 2026-03-24 ~ 2026-04-15)', NULL, NULL, 'undergrad_enrolled', 1, 3, NULL, 'school_external', 'private_foundation'),

('미래산업 인재 학부 장학생', '현대차 정몽구 재단', '선발일 기준 대한민국 국적 보유자로서 2~3학년 재학생 및 복학 예정자(대학 제한 없음, 최근 개편으로 지정대학 제한 폐지됨 — 전문대 제외). 선발분야: 지능정보기술/바이오헬스/기후기술 및 에너지. 전체 학기 백분위 성적 90점 이상(지원 분야 유관 전공 성적 우수자 우대). 가구 중위소득 150% 이하(한국장학재단 소득구간 7구간 이하). 학습지원비 학기당600만원+국제학술대회 장학금+해외진출 장학생 장학금+온드림 글로벌 우수 장학금. 서류심사+온라인 인적성검사+전공면접+인성면접. 마지막 학기 재학생 지원 불가.', 6000000, 'http://www.cmkfoundationscholarship.org/', NULL, NULL, NULL, NULL, NULL, 7, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '매년 3~4월경 모집(2025년 기준: 2025-03-24 ~ 2025-04-16)', NULL, NULL, 'undergrad_enrolled', 2, 3, NULL, 'school_external', 'private_foundation'),

('미래산업 인재 대학원 장학생', '현대차 정몽구 재단', '일반대학원 석/박사/석박사통합과정 신입생 및 재학생(대학 제한 없음, 최근 개편으로 지정대학 제한 폐지됨). 전일제 미취업 일반대학원생만 지원가능(특수 및 전문대학원 제외). 선발분야: 지능정보기술/바이오헬스/기후기술 및 에너지. 전체학기 백분위성적 90점 이상, 영어성적(TOEIC850 또는 TOEIC Speaking150 또는 OPIc IM3 등). 가구 중위소득150% 이하(소득구간7구간 이하). 학습지원비 학기당700만원+국제학술대회 장학금 등. 지도교수 추천 필요. 마지막 학기 재학생 제외.', 7000000, 'http://www.hyundaicmkfoundation.org/', NULL, NULL, NULL, NULL, NULL, 7, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '매년 3~4월경 모집(2026년 기준: 2026-03-25 ~ 2026-04-15)', NULL, NULL, NULL, NULL, NULL, 'masters', 'school_external', 'private_foundation'),

('고리원자력본부장학(일반장학생)', '한국수력원자력(주)', '국내소재 정규대학에 재학 중인 자. 부산 기장군 장안읍·일광읍에 공고일 포함 최근 만3년 이상 계속 거주(또는 만1년 이상+과거 합산 만15년 이상). 2026학년도 1학기 12학점 이상 이수, 평점평균 2.5/4.5 이상. 100만원(1회성 생활지원금). 한국수력원자력·한국전력·한전KPS 및 발전자회사 직원 및 가족, 사이버대·방송통신대 등 제외. ⚠️2026년부터 일반/특별 구분이 대학생/고등학생/체육특기생(기장군체육회 추천) 구분으로 재편된 것으로 보임 — 세부 변경사항 재확인 권장.', 1000000, 'http://www.khnp.co.kr/kori/main.office', NULL, NULL, NULL, '기장군', NULL, NULL, 2.5, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '매년 7월경 모집(2026년 기준: 2026-07-27 ~ 2026-07-31)', NULL, NULL, 'undergrad_enrolled', NULL, NULL, NULL, 'school_external', 'private_foundation'),

('고리원자력본부장학(특별장학생)', '한국수력원자력(주)', '국내소재 정규대학 재학 중, 부산 기장군 장안읍 전역·일광읍 문동리·문중리·칠암리·신평리·동백리·원리 거주자. 2026학년도 1학기 평균평점 2.5/4.5 이상 및 12학점 이상 이수. 본인 혹은 부모가 기초생활수급자/한부모가정/차상위본인부담경감대상자 중 하나 해당. 300만원(1회성). 한수원·한전·한전KPS 직원 및 가족 제외.', 3000000, 'http://www.khnp.co.kr/kori/main.office', NULL, NULL, NULL, '기장군', NULL, NULL, 2.5, NULL, NULL, NULL, NULL, NULL, NULL, '{single_parent_family,basic_livelihood_recipient,near_poor}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '매년 7월경 모집(2026년 기준: 2026-07-27 ~ 2026-07-31)', NULL, NULL, 'undergrad_enrolled', NULL, NULL, NULL, 'school_external', 'private_foundation'),

('월성원자력본부 주변지역 장학생', '한국수력원자력(주)', '고등교육법 제2조에서 정한 대학의 재학생(외국대학은 국내 전문학사 학위 이상 취득 가능 대학). 경주시 양남면·문무대왕면·감포읍에 만3년 이상(과거부터 접수마감일까지) 연속 주민등록·실거주 중인 주민 또는 그 대학생 자녀. 전체학년 총평균평점 2.0/4.5 이상. 초중고를 주변지역 소재 학교에서 졸업한 정도에 따라 100~140만원 차등(방통대·사이버대는 30만원). 한수원·한전KPS 임직원 및 가족, 대학원 및 초과학기 제외.', 1400000, 'http://www.khnp.co.kr/', NULL, NULL, NULL, '경주시', NULL, NULL, 2.0, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '매년 7월경 모집(2026년 기준: 2026-07-15 ~ 2026-07-29)', NULL, NULL, 'undergrad_enrolled', NULL, NULL, NULL, 'school_external', 'private_foundation'),

('새울원자력본부 희망미래 장학생', '한국수력원자력(주)', '국내소재 정규대학(교) 재학 중, 울주군 서생면·온양읍 지역 거주자(발전소건설 이주민 및 직계비속, 반경1km 이내 거주자, 기초생활수급자 등 세부 요건에 따라 지원금 차등: 100~150만원). 실제 만3년 이상 거주(또는 만1년 이상+과거합산 만15년 이상). 2026학년도 1학기 평균평점 2.0~2.5/4.5 이상(세부기준별 상이). 대학생·고등학생 합산 620명, 총 6억원 규모(2026년 "새울 희망미래 장학생"으로 통합 운영, 기존 일반/지역/우대/특별 4개 세부구분이 유지되는지는 원문 재확인 필요). 한수원·한전·한전KPS 직원 및 가족, 대학원생, 정규학기 초과자 제외.', 1500000, 'http://www.khnp.co.kr/', NULL, NULL, NULL, '울주군', NULL, NULL, 2.0, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, '대학생·고등학생 합산 620명', '매년 7월경 모집(2026년 기준: 2026-07-23 ~ 2026-07-29)', NULL, NULL, 'undergrad_enrolled', NULL, NULL, NULL, 'school_external', 'private_foundation'),

('양양양수발전소주변지역장학금(주민자녀)', '한국수력원자력(주)', '학생 본인 또는 보호자가 강원 양양군 서면 또는 인제군 기린면에 장학생 선발 공고일 기준으로 주민등록을 두고 1년 이상(자료에 따라 2년 이상이라는 정보도 있어 재확인 필요) 실제 거주 중일 것. 12학점 이상 수강, 성적 4.5만점 기준 3.0 이상. 200만원. 거주지/소득수준/성적 순 선발. 휴학생 제외.', 2000000, 'https://www.inje.go.kr', NULL, NULL, NULL, '양양군', NULL, NULL, 3.0, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, '100명', '매년 9월경 모집(2025년 기준: 2025-09-22 ~ 2025-10-24)', NULL, NULL, 'undergrad_enrolled', NULL, NULL, NULL, 'school_external', 'private_foundation'),

('강원랜드 멘토링 장학생(하이샘·하이디)', '강원랜드사회공헌위원회', '전국 석탄산업전환지역(정선·태백·영월·삼척·보령·문경·화순) 소재 고등학교를 졸업한 국내 대학생. 2026년 1·2학기 정규학기 등록 재학생. 나눔장학(기초생활수급자 등 저소득층, 12학점이상+평점3.0/4.5 이상)/키움장학(평점3.5/4.5 이상) 구분. 360만원(연2회 분할)+학업생활 장려금. 석탄산업전환지역 소재 중고등학교 대상 온라인 멘토링 진행(주4시간) 필수. 장학생 활동기간 중 타 장학금 200만원 초과 수혜 시 신청 불가. ⚠️거주지가 아니라 "출신 고등학교 소재지" 조건이라 구조화된 매칭은 안 되고(hometown_school_region_condition), description 텍스트로만 자격 확인 가능.', 3600000, 'http://csr.high1.com', NULL, NULL, NULL, NULL, NULL, NULL, 3.0, NULL, NULL, NULL, NULL, NULL, NULL, '{hometown_school_region_condition}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '매년 4월경 모집(2026년 기준: 2026-04-17 ~ 2026-04-29, 2026년도분 이미 선발완료 522명)', NULL, NULL, 'undergrad_enrolled', NULL, NULL, NULL, 'school_external', 'private_foundation'),

('강원랜드 SOS 장학(구 하이원SOS장학생)', '강원랜드사회공헌위원회', '갑작스러운 가정·경제 위기상황(부모의 사망·질병 등)으로 학업에 심각한 어려움을 겪는 대학 재학생 중, 전국 폐광지역(정선·태백·영월·삼척·보령·문경·화순 등 7개 시/군) 소재 고등학교를 졸업한 자. 100~300만원(사례 경중·위기상황·장학금 사용계획 등 종합평가). 2024년도 강원랜드 멘토링 장학 나눔/키움 장학생 수혜자는 지원 불가, 1가구당 연1회 제한. 상시 접수. ⚠️거주지가 아니라 "출신 고등학교 소재지" 조건(hometown_school_region_condition). 2026년 기준 "강원랜드 SOS 장학"으로 명칭 변경됨.', NULL, 'https://sos.high1scholarship.co.kr', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{hometown_school_region_condition}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '상시 접수(위기상황 발생 시 수시 신청)', NULL, NULL, 'undergrad_enrolled', NULL, NULL, NULL, 'school_external', 'private_foundation'),

('빙그레공익재단 독립유공자 후손 장학생', '재단법인 빙그레공익재단', '독립·국가유공자(소방공무원·의무소방대원 등 제복근무자 포함) 후손으로 생활이 어려운 가정의 대학생(독립유공자 후손: 자손·증손·고손 등, 친가·외가 불문. 국가유공자(소방) 등 후손: 자녀·손자녀). 학업성적 등 학교생활에 모범이 되는 자. 대학생200만원. 2026년 지원규모 확대(독립유공자 후손 45명+국가유공자 제복근무자 후손 신규 포함, 총94명·1.5억원). 생활이 어려운 자(생활지원금·생활조정수당·기초생활수급자·차상위자) > 기준중위소득120%이하 > 고학년 > 성적우수자(직전학기70점) 순 선발. 접수처: 재학 학교 소재지 관할 보훈(지)청 보훈과.', 2000000, 'http://www.mpva.go.kr', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '{national_merit}', NULL, NULL, NULL, NULL, NULL, NULL, '94명(2026년 확대)', '매년 6월경 모집(2026년 기준: 2026-06-08 ~ 2026-06-30)', NULL, NULL, 'undergrad_enrolled', NULL, NULL, NULL, 'school_external', 'private_foundation'),

('포스코비전장학', '포스코청암재단', '경북 포항 또는 전남 광양 지역가정 또는 소재 고등학교 졸업자로서 2026년 대학 신입생. 1학기 성적 3.0/4.5 이상. 소득5분위 이내. 연간500만원(최대7학기, 1학년 2학기부터 지급 — 1학기 신입생은 첫 학기 대상 아님). 재단 홈페이지 온라인 신청 후 서류심사+면접. 다음학기 휴학예정자, 국내 정규 4년제·전문대학 재학생만 가능.', 5000000, 'http://www.postf.org/', NULL, NULL, NULL, '포항시·광양시', NULL, NULL, 3.0, NULL, NULL, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, '40명 내외', '매년 6~7월경 모집(2026년 기준: 2026-06-15 ~ 2026-07-19, 신청 마감 지남)', NULL, NULL, 'undergrad_enrolled', 1, 1, NULL, 'school_external', 'private_foundation'),

('쌍용곰두리장학(성적우수)', '한국장애인개발원', '대한민국 국적의 일반 대학(원)·전문대학에 재학 중인 장애 학생. 직전 학기 성적 평균80점 이상, 최소 12학점(대학)/6학점(대학원) 이상 이수. 학기당100만원(생활보조비 무상보조, 결격사유 없는 한 1년간 지급). 신청서 및 제출서류 구비 후 재학 중인 학교 장학담당 부서를 통해 학교장 명의 전자공문으로 신청. 2026년 2학기 입학생, 원격대(방송통신대·사이버대 등)·평생교육원 제외. 성적우수/예체능특기/정보통신특기 통합 총20명.', 1000000, 'https://www.koddi.or.kr', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, TRUE, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, '직전학기 100점 만점 기준 평균 80점 이상(4.5만점 환산 기준 미명시)', '20명(3개 부문 통합)', '매년 7월경 모집(2026년 기준: 2026-07-20 ~ 2026-07-31)', NULL, NULL, 'undergrad_enrolled', NULL, NULL, NULL, 'school_external', 'private_foundation'),

('쌍용곰두리장학(예체능특기)', '한국장애인개발원', '일반대학(원) 및 전문대학에 재학 중인 장애학생으로 2023년 이후 국내외 예·체능대회에서 입상한 경력이 있는 학생. 학기당100만원(생활보조비 무상보조, 결격사유 없는 한 1년간 지급). 학교장 명의 전자공문으로 신청. 성적우수/예체능특기/정보통신특기 통합 총20명.', 1000000, 'https://www.koddi.or.kr', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, TRUE, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, '20명(3개 부문 통합)', '매년 7월경 모집(2026년 기준: 2026-07-20 ~ 2026-07-31)', NULL, NULL, 'undergrad_enrolled', NULL, NULL, NULL, 'school_external', 'private_foundation'),

('쌍용곰두리장학(정보통신특기)', '한국장애인개발원', '일반대학(원)·전문대학에 재학중인 장애학생으로 2023년 이후 국내외 정보통신대회에서 입상한 경력이 있는 자. 학기당100만원(생활보조비 무상보조, 결격사유 없는 한 1년간 지급). 학교장 명의 전자공문으로 신청. 성적우수/예체능특기/정보통신특기 통합 총20명.', 1000000, 'https://www.koddi.or.kr', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, TRUE, NULL, NULL, NULL, NULL, '{}', NULL, NULL, NULL, NULL, NULL, NULL, '20명(3개 부문 통합)', '매년 7월경 모집(2026년 기준: 2026-07-20 ~ 2026-07-31)', NULL, NULL, 'undergrad_enrolled', NULL, NULL, NULL, 'school_external', 'private_foundation');
