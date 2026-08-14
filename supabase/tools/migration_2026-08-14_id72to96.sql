-- id=72~96: CNU 학과·외부 개별 장학금. 기존 description이 이미 상당히 상세하게(날짜/전화번호/
-- 조건 등) 조사돼 있어서, 이번 배치는 새로 원문을 재조회하지 않고 기존 텍스트를 금액/신청방식/
-- 자격조건으로 재분류만 함 — 재검증(WebFetch)은 생략했음을 최종 보고에서 사용자에게 알릴 것.

UPDATE scholarship SET amount_detail='1인 200만원(100만원씩 2회 분할 지급), 생활비 지원 장학금', application_method='공고문 확인 후 신청 접수(구체적 신청 경로는 공고 원문 참고)', description='본인 또는 부모 중 1인이 공고일(2026-07-13) 기준 충남에 1년 이상 중도 이탈 없이 계속 거주 중인, 대한민국 소재 대학교 1학년(2차 신청 기준) 대상 — 특정 대학으로 제한하지 않음.' WHERE id=72;
UPDATE scholarship SET amount_detail='시급 18,000원 × 활동시간 지급(연 10시간 이상 조건부)', application_method='한국장학재단 경유 접수(구체적 신청 경로는 공고 원문 참고)' , description=NULL WHERE id=73;
UPDATE scholarship SET amount_detail='100만원', application_method='화성시인재육성재단 홈페이지 온라인 신청', description='화성시 지역화폐 가맹점 자녀 대상, 본인 또는 부모 1인이 화성시에 1년 이상 거주, 소득기준 심사' WHERE id=74;
UPDATE scholarship SET amount_detail='220만원', application_method='정읍시민장학재단 신청(2026년 1학기 성적 기준)', description=NULL WHERE id=75;
UPDATE scholarship SET amount_detail='500만원(생활비성 지원)', application_method='학과별 추천 — 학생 개별 신청 아님(학과 사무실 통해 추천)', description='경제적 이유로 학업지속이 어려운 학생 대상' WHERE id=76;
UPDATE scholarship SET amount_detail='정확한 지원금액은 첨부파일(붙임1)에만 기재돼 있음 — 원문 첨부 재확인 필요', application_method='참여의향서·논문계획서 제출 후 최종논문 제출(문의 043-277-7802)', admission_score_condition='전국 대학(원)생 대상 논문공모(휴학생 제외). 주제: 의암 손병희 생애·사상, 동학농민혁명, 3·1혁명 관련 자유주제', description=NULL WHERE id=77;
UPDATE scholarship SET amount_detail='해당 학기 수업료 전액(2026년 8월 내 지급 원칙, 사정에 따라 9월 지연 가능)', application_method='이메일(kucla@kucla.or.kr)로 신청서 제출', description='휴학생 포함(단 복학 전제, 미복학 시 반납). 기록학 분야 전공자 제외. 한국대학도서관연합회-㈜누리미디어 협약 장학사업.' WHERE id=78;
UPDATE scholarship SET amount_detail='등록금 전액 지원 원칙(1인당 한 학기 최대 500만원, 최대 2개 학기 지급)', application_method='재단 홈페이지(apply.31cf.or.kr) 온라인 신청, 가계곤란 증빙서류는 해당자만 추가 제출', admission_score_condition='박사과정 입학예정자 또는 박사과정 정규학기 2학기 이상 잔여자(석박사통합과정도 준함). 신입생은 석사 전체학기 평균 A학점 이상, 재학생은 직전학기 및 박사과정 전체학기 평균 A학점 이상', description='소득·국적 제한 여부는 원문에 명시돼 있지 않음(확정 필요 시 재단 02-735-3132 문의)' WHERE id=79;
UPDATE scholarship SET amount_detail='일본어학연수 학비 60%(기본)~전액(상위) 지원 + 생활지원금', application_method='홈페이지(angelroute.org)에서 신청, 일본 비자 결격사유만 없으면 지원 가능(사실상 대부분 통과하는 자체 선발 방식)', description='일본 유학·취업·워킹홀리데이 등 해외진출 준비 중인 자 대상. JLPT 등 어학 자격증 불필요.' WHERE id=80;
UPDATE scholarship SET amount_detail='금상 1명 300만원, 은상 1명 200만원(총 500만원)', application_method='자기소개서 제출 후 면접 심사', admission_score_condition='행정학부 학부생 대상 사회공헌·자기소개서·면접 종합평가', description=NULL WHERE id=81;
UPDATE scholarship SET amount_detail='현금 150만원 + 현물 30만원', application_method='협회 홈페이지 통해 신청(구체적 경로는 공고 원문 참고)', description='인슐린 투여 소아청소년 당뇨인 및 췌장장애인 대상 의료·생활비 지원.' WHERE id=82;
UPDATE scholarship SET amount_detail='사업별 금액 상이(예산 초과 시 감액)', application_method='대학원 행정실 통해 신청(공동저자 지원은 2026년부터 폐지)', description='대학원생 우수논문게재·학술대회발표 지원(연구비 성격 장학금)' WHERE id=83;
UPDATE scholarship SET amount_detail='튜터 100만원(선발 시 40만원 + 보고서 제출 시 60만원), 우수팀 튜터 5명 추가 20만원', application_method='대학원생(튜터)-학부생(튜티) 팀 매칭 신청', description='연구 튜터링 프로그램(활동기간 2026-08~2027-02)' WHERE id=84;
UPDATE scholarship SET amount_detail='학자금대출이자·디딤돌 장학 지원(정확한 금액은 대출 조건에 따라 상이)', application_method='이메일 문의 후 신청(jh@sri.re.kr, 044-865-9685)', description='세종시 거주자 대상' WHERE id=85;
UPDATE scholarship SET amount_detail='장학금액은 선발 후 개별통보(정확한 금액 원문에 없음)', application_method='매년 1~2월 홈페이지 공고 후 신청', description='수학과 발전기금 재원' WHERE id=86;
UPDATE scholarship SET amount_detail='매학기 등록금의 50% 지급, 4학년 2학기(8학기) 또는 대학원 수료까지 지속 지급', application_method='매년 1~2월 홈페이지 공고 후 신청', admission_score_condition='품행이 단정하며 향학열이 높은 학생', description='2004년 8월 자연과학대학 내 설립' WHERE id=87;
UPDATE scholarship SET amount_detail='500만원(1회 지급)', application_method='자동선발 — 별도 신청 없음', admission_score_condition='토목공학과 입학자 중 수능 국어·수학·영어 합산 6등급 이내 적격자 전원', description=NULL WHERE id=88;
UPDATE scholarship SET amount_detail='연 500만원, 일정 성적 및 자격 유지 시 4년간 계속 지급', application_method='자동선발 — 별도 신청 없음', admission_score_condition='토목공학과 입학자 중 수능 국어·수학·영어 합산 5등급 이내 적격자 전원', description=NULL WHERE id=89;
UPDATE scholarship SET amount_detail='250만원(생활비 지원 목적)', application_method='자동선발로 추정 — 신청방법 원문에 명시 안 됨', description=NULL WHERE id=90;
UPDATE scholarship SET amount_detail='등록금 전액을 무이자로 대출(생활비 제외)', application_method='한국장학재단 홈페이지(kosaf.go.kr)에서 온라인 신청', admission_score_condition='직전학기 최저이수학점(또는 12학점) 이상 + 성적 70점(100점 만점) 이상 이수(신입생·편입생·재입학생은 성적/학점 기준 적용 제외), 본인이 농어업 종사 기준 충족 시 부모의 농어촌 거주·종사 여부 무관', description=NULL WHERE id=91;
UPDATE scholarship SET amount_detail='등록금 전액 감면', application_method='자동선발로 추정 — 의학전문대학원 M.D.-Ph.D 과정 합격 시 적용(학과 문의 042-580-8113)', description='선발인원은 "총장이 인정하는 인원"으로 규정, 상시(제도적) 장학금' WHERE id=92;
UPDATE scholarship SET amount_detail='월 생활비·정착비·연구비·미국무성 의료보험·왕복항공권·수하물비 지원', application_method='한미교육위원단(풀브라이트) 홈페이지 온라인 신청', admission_score_condition='국내 대학 박사학위 취득자(2022.9 이후), 이중국적자·영주권자 제외, 우수 연구성과 보유자, J-1비자 결격사유 없는 자', description=NULL WHERE id=93;
UPDATE scholarship SET amount_detail='학기당 300만원', application_method='한국장학재단 누리집(kosaf.go.kr)에서 온라인 신청', admission_score_condition='AI 핵심분야 진로 희망자', description=NULL WHERE id=94;
UPDATE scholarship SET amount_detail='학기당 500만원', application_method='한국장학재단 누리집(kosaf.go.kr)에서 온라인 신청', admission_score_condition='인문사회계열 일반대학원 석사과정(전일제)', description=NULL WHERE id=95;
UPDATE scholarship SET amount_detail='등록금 전액 또는 일부', application_method='간호대학 행정실 통해 신청(구체적 경로는 공고 원문 참고)', admission_score_condition='학·석사연계과정 석사 신입생/재학생, 석·박사통합과정 유형1·유형2 신입생 및 재학생(전일제)', description=NULL WHERE id=96;
