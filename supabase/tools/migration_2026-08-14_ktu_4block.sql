-- 한국침례신학대학교 45건 4블록(금액/기간/신청방식) 분리 + 내부메모/헤지 문구 제거
-- id=366(지정·미지정 외부장학금)은 판단 보류 대상이라 이 마이그레이션에서 제외함

UPDATE scholarship SET
  amount_detail = '수업료 100%',
  application_period = '신입학 시',
  application_method = '추천 및 서류제출(교회주보·재직증명서·목회자추천서)',
  description = '동일 교회에서 신입생 3명 이상이 동시에 입학할 경우, 담임목사 추천을 받은 1명에게 지급.'
WHERE id = 322;

UPDATE scholarship SET
  amount_detail = '수업료 13% 지원',
  application_period = '매 학기 말 ''보강 및 기말고사'' 기간 중(2026-12-08~12-21)',
  application_method = '신청(제출서류: 재직증명서·가족관계증명서)',
  description = '침례교단 인준 목회자의 배우자(사모) 대상.'
WHERE id = 323;

UPDATE scholarship SET
  amount_detail = '수업료 30% 지원(1개 학위과정에 한해 지급)',
  application_period = '매 학기 말 ''보강 및 기말고사'' 기간 중(2026-12-08~12-21)',
  application_method = '신청',
  description = '침례교단 또는 타 교단 인준 목회자의 자녀(만 33세 미만) 대상.'
WHERE id = 324;

UPDATE scholarship SET
  amount_detail = '수업료 50% 지원',
  application_period = '매 학기 말 ''보강 및 기말고사'' 기간 중(2026-12-08~12-21)',
  application_method = '신청',
  description = '한국침례회 해외선교회 소속 장기선교사(북한 선교사 포함)의 자녀 대상.'
WHERE id = 325;

UPDATE scholarship SET
  amount_detail = '수업료 65%',
  application_period = '매 학기 말 ''보강 및 기말고사'' 기간 중(2026-12-08~12-21)',
  application_method = '신청',
  description = '직계가족 3인 이상이 학부·대학원에 동시 재학 중인 경우 가족이 지정한 1인에게 지급.'
WHERE id = 326;

UPDATE scholarship SET
  amount_detail = '수업료 50%',
  application_period = '매 학기 말 ''보강 및 기말고사'' 기간 중(2026-12-08~12-21)',
  application_method = '신청',
  description = '부부가 동시 재학 중인 경우 지정한 1인에게 지급.'
WHERE id = 327;

UPDATE scholarship SET
  amount_detail = '수업료 100%(1개 학위과정에 한해 지급)',
  application_period = '매 학기 말 ''보강 및 기말고사'' 기간 중(2026-12-08~12-21)',
  application_method = '신청',
  description = '한국침례신학대학교 교직원의 자녀(만 33세 미만) 대상.'
WHERE id = 328;

UPDATE scholarship SET
  amount_detail = '수업료 50%(1개 학위과정에 한해 지급)',
  application_period = '매 학기 말 ''보강 및 기말고사'' 기간 중(2026-12-08~12-21)',
  application_method = '신청',
  description = '한국침례신학대학교 교직원 본인 또는 그 배우자 대상.'
WHERE id = 329;

UPDATE scholarship SET
  amount_detail = '수업료 50% 지원(교내 자체 재원)',
  application_period = '매 학기 말 ''보강 및 기말고사'' 기간 중(2026-12-08~12-21)',
  application_method = '신청',
  description = '북한이탈주민 재학생 대상.'
WHERE id = 330;

UPDATE scholarship SET
  amount_detail = '국가유공자 본인·배우자: 수업료 100%
국가유공자 자녀(직전학기 성적 백분위 70점 이상): 수업료 50%',
  application_period = '매 학기 말 ''보강 및 기말고사'' 기간 중(2026-12-08~12-21)',
  application_method = '신청',
  description = '국가유공자 본인·배우자 또는 그 자녀 대상(교내 자체 재원).'
WHERE id = 331;

UPDATE scholarship SET
  amount_detail = '장학위원회 심의로 결정(정액 미정)',
  application_period = '수시',
  application_method = '장학위원회 심의',
  description = '해외 교환학생으로 선발된 학생 대상.'
WHERE id = 332;

UPDATE scholarship SET
  amount_detail = '수업료 40% 지원, 최대 2개 학위과정까지 지급',
  application_period = '매 학기 말 ''보강 및 기말고사'' 기간 중(2026-12-08~12-21)',
  application_method = '신청(제출서류: 여권·목회자추천서·건강보험 가입증명)',
  description = '외국인 학생 대상(국외 한국인 대상 교육 장학금 미수혜자에 한함).'
WHERE id = 333;

UPDATE scholarship SET
  amount_detail = '수업료 50% 지원(1개 학위과정에 한해 지급)',
  application_period = '매 학기 말 ''보강 및 기말고사'' 기간 중(2026-12-08~12-21)',
  application_method = '신청',
  description = '중증장애 학부 재학생 대상.'
WHERE id = 334;

UPDATE scholarship SET
  amount_detail = '수업료 100% 지원',
  application_period = '매 학기 말 ''보강 및 기말고사'' 기간 중(2026-12-08~12-21)',
  application_method = '신청',
  description = '교회음악과 학생 중 학과 교수 추천을 받은 자 대상.'
WHERE id = 335;

UPDATE scholarship SET
  amount_detail = '수업료 100% 지원',
  application_period = '매 학기 말 ''보강 및 기말고사'' 기간 중(2026-12-08~12-21)',
  application_method = '신청(제출서류: 선발확인서)',
  description = '국방부에서 선발한 군종사관후보생 대상.'
WHERE id = 336;

UPDATE scholarship SET
  amount_detail = '수업료 100% 지원',
  application_period = '매 학기 말 ''보강 및 기말고사'' 기간 중(2026-12-08~12-21)',
  application_method = '신청',
  description = '총학생회장·부회장·총무 등 최상위 학생자치기구 임원 대상.'
WHERE id = 337;

UPDATE scholarship SET
  amount_detail = '수업료 70% 지원',
  application_period = '매 학기 말 ''보강 및 기말고사'' 기간 중(2026-12-08~12-21)',
  application_method = '신청',
  description = '학과 학생회장·동아리연합회장 등 중간급 학생자치기구 임원 대상.'
WHERE id = 338;

UPDATE scholarship SET
  amount_detail = '수업료 30% 지원',
  application_period = '매 학기 말 ''보강 및 기말고사'' 기간 중(2026-12-08~12-21)',
  application_method = '신청',
  description = '학생회 국장·학과 총무 등 실무진 학생자치기구 임원 대상.'
WHERE id = 339;

UPDATE scholarship SET
  amount_detail = '지급액은 프로그램별로 상이',
  application_period = '수시',
  application_method = '추천',
  description = '교수학습지원센터의 추천을 받은 학생 대상(각종 대회 격려 포함).'
WHERE id = 340;

UPDATE scholarship SET
  amount_detail = '지급액은 프로그램별로 상이',
  application_period = '수시',
  application_method = '추천',
  description = '진로·취업지원센터의 추천을 받은 학생 대상(각종 대회 격려 포함).'
WHERE id = 341;

UPDATE scholarship SET
  amount_detail = '지급액은 대회별로 상이',
  application_period = '수시',
  application_method = '추천',
  description = '각종 대회·경연 참가자 중 소속 학과 추천을 받은 학생 대상.'
WHERE id = 342;

UPDATE scholarship SET
  amount_detail = '수업료 40%(1개 학기에 한함)',
  application_period = '매 학기 말 ''보강 및 기말고사'' 기간 중(2026-12-08~12-21)',
  application_method = '신청',
  description = 'TOEFL IBT 90점(120점 만점) 이상, TOEIC 850점(990점 만점) 이상, 또는 TOEIC Speaking 중상급(Intermediate-High) 이상 등 어학 성적 우수자 대상.'
WHERE id = 343;

UPDATE scholarship SET
  amount_detail = '입학성적(전형 환산점수) 상위 5% 신입생 대상 — 과수석: 수업료 100%
성적우수A(수석 포함 상위 3%): 수업료 65%
성적우수B(다음 2%): 수업료 25%',
  application_period = '신입학 시',
  application_method = '자동선발',
  description = '사회복지학과·유아교육과 등 일부 학과는 별도 트랙으로 선발.'
WHERE id = 344;

UPDATE scholarship SET
  amount_detail = '4년간 수업료 100% 지원',
  application_period = '신입학 시',
  application_method = '자동선발',
  description = '대학수학능력시험 국어·수학·영어 전 영역 1등급(예체능계열 제외) 신입생 대상.'
WHERE id = 345;

UPDATE scholarship SET
  amount_detail = '매년 성적 상위 5% 재학생 대상 — 과수석: 수업료 100%
성적우수A(수석 포함 상위 3%): 수업료 65%
성적우수B(다음 2%): 수업료 25%',
  application_period = '매 학기 말 ''보강 및 기말고사'' 기간 중(2026-12-08~12-21)',
  application_method = '신청',
  description = NULL
WHERE id = 346;
-- 참고(내부용, DB엔 안 넣음): 순위 기준 선발이라 min_gpa 단일 수치로 매칭 불가 — matching_gaps 후보

UPDATE scholarship SET
  amount_detail = '수업료 이내에서 지급',
  application_period = '신입학·편입학 시',
  application_method = '자동선발',
  description = '2026학년도 신입학·편입학생 대상 1년간 한정 지원(가정형편 고려).'
WHERE id = 347;

UPDATE scholarship SET
  amount_detail = '수업료 이내에서 심의로 지급',
  application_period = '매 학기 말 ''보강 및 기말고사'' 기간 중(2026-12-08~12-21)',
  application_method = '신청(장학위원회 심의)',
  description = '가정형편이 어려운 재학생 대상.'
WHERE id = 348;

UPDATE scholarship SET
  amount_detail = '수업료 이내',
  application_period = '매 학기 초',
  application_method = '자동선발(국가장학금 신청 여부와 연동해 대응 지급)',
  description = '한국장학재단 국가장학금 수혜자 대상, 장학위원회 심의를 거쳐 교내 재원으로 대응 지원.'
WHERE id = 349;

UPDATE scholarship SET
  amount_detail = '심의로 금액 결정(정액 미정)',
  application_period = '국가재난 발생 시 수시 공지',
  application_method = '장학위원회 심의',
  description = '국가재난 발생 시 지원. 통상 요구되는 GPA·출석 기준이 면제됨.'
WHERE id = 350;

UPDATE scholarship SET
  amount_detail = '100만원 이내 지급(장학사정관 심의)',
  application_period = '수시',
  application_method = '총장·학과장·대학원장 추천 필요',
  description = '목회자 자녀 및 생계가 곤란한 학생 대상.'
WHERE id = 351;

UPDATE scholarship SET
  amount_detail = '100만원 이내 지급',
  application_period = '수시',
  application_method = '장학사정관 심의',
  description = '목회자 부부(모영국·송정선 목사)를 기리는 기금장학금.'
WHERE id = 352;

UPDATE scholarship SET
  amount_detail = '장학사정관 심의로 결정(정액 미정)',
  application_period = '수시',
  application_method = '장학사정관 심의',
  description = '구체적 자격조건이 정해져 있지 않은 재량형 기금장학금.'
WHERE id = 353;

UPDATE scholarship SET
  amount_detail = '등록금 이내 지급',
  application_period = '수시',
  description = '신학대학원생 중 성적이 우수하고 교회 사역 중이며 가정형편이 어려운 학생 대상.'
WHERE id = 354;

UPDATE scholarship SET
  amount_detail = '등록금 이내 지급',
  application_period = '수시',
  description = '신학대학원생 중 성적이 우수하고 가정형편이 어려운 학생 대상.'
WHERE id = 355;

UPDATE scholarship SET
  amount_detail = '등록금 이내 지급',
  application_period = '매 학기 말 ''보강 및 기말고사'' 기간 중(2026-12-08~12-21)',
  application_method = '신청',
  description = '학부생 중 성적이 우수하고 가정형편이 어려운 학생 대상.'
WHERE id = 356;

UPDATE scholarship SET
  amount_detail = '등록금 이내 지급',
  application_period = '수시',
  description = '신학대학원생 중 성적이 우수하고 교회 사역 중이며 가정형편이 어려운 학생 대상.'
WHERE id = 357;

UPDATE scholarship SET
  amount_detail = '등록금 이내 지급',
  application_period = '수시',
  description = '침례교 해외선교회 소속 선교사의 자녀로 신학계열 학부 또는 대학원에 재학 중인 학생 대상.'
WHERE id = 358;

UPDATE scholarship SET
  amount_detail = '등록금 이내 지급',
  application_period = '수시',
  description = '일반대학원 기독교교육전공 재학생 대상.'
WHERE id = 359;

UPDATE scholarship SET
  amount_detail = '등록금 이내 지급',
  application_period = '수시',
  application_method = '장학사정관 심의',
  description = '구체적 자격조건이 정해져 있지 않은 재량형 기금이자장학금.'
WHERE id = 360;

UPDATE scholarship SET
  amount_detail = '등록금 이내 지급',
  application_period = '수시',
  description = '목회자 또는 선교사를 지망하는 학생 대상.'
WHERE id = 361;

UPDATE scholarship SET
  amount_detail = '10만원 지급',
  application_period = '매 학기 말 ''보강 및 기말고사'' 기간 중(2026-12-08~12-21)',
  application_method = '신청',
  description = '대학예배(채플) 출석이 우수한 학생 대상.'
WHERE id = 362;

UPDATE scholarship SET
  amount_detail = '20만원~50만원 차등 지급',
  application_period = '매 학기 말 ''보강 및 기말고사'' 기간 중(2026-12-08~12-21)',
  application_method = '신청',
  description = '직전 학기 대비 성적이 향상된 학생 대상.'
WHERE id = 363;

UPDATE scholarship SET
  amount_detail = '20만원~100만원 차등 지급',
  application_period = '매 학기',
  application_method = '자동선발',
  description = '성경시험(Bible Test Scholarship) 성적 우수자 대상.'
WHERE id = 364;

UPDATE scholarship SET
  amount_detail = '수업료 100% 지원',
  application_period = '수시',
  description = '규정에 따라 선발.'
WHERE id = 365;
