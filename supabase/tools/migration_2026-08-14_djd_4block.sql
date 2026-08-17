-- 대전대학교 40건 4블록(금액/기간/신청방식) 분리 + 말미 중복 태그/내부메모 제거

UPDATE scholarship SET
  amount_detail = '등록금 전액, 이후 매학기 직전학기 15학점 이상 취득·평점평균 3.5 이상 유지 시 4년간 지급(수시/정시 공통)',
  application_period = '입학 시',
  application_method = '자동선발',
  description = '한의예과·군사학과 제외. 공통기준: 수능 영어영역 2등급 이내, 탐구영역(직업탐구 제외) 2과목 평균 반영. 일반학과(부)는 국어·수학·탐구영역 중 2개 영역 백분위 합 160점 이상, 간호학과·물리치료학과는 국어·수학·탐구영역 백분위 합 240점 이상.'
WHERE id = 257;

UPDATE scholarship SET
  amount_detail = '수능 국어·수학·영어 평균 2등급 이내: 등록금 전액(이후 직전학기 15학점+평점평균 4.0 이상 유지 시 4년)
평균 3등급 이내: 수업료 일부(직전학기 15학점+평점평균 3.5 이상 유지)(수시/정시 공통)',
  application_period = '입학 시',
  application_method = '자동선발',
  description = '군사학과 여자 신입생 대상.'
WHERE id = 258;

UPDATE scholarship SET
  amount_detail = '각 전형별 모집단위(학과)·단과대학별 수석·차석에게 수업료 일부 지급(한의예과는 인문/자연 통합 1명). 이후 직전학기 15학점 이상 취득·평점평균 3.5 이상 유지 시 1년간 지급.',
  application_period = '입학 시',
  application_method = '자동선발',
  description = '교과면접전형·교과중점전형·지역인재Ⅰ·Ⅱ전형(통합선발)·혜화인재전형·고른기회전형·농어촌학생전형·특성화고교졸업자전형·기회균형전형·군사학과전형 등 전형별 수석·차석 대상. 실기위주전형(커뮤니케이션디자인학과·영상애니메이션학과·공연예술콘텐츠학과·생활체육학과·건강운동관리학과)도 모집단위별 수석 별도 선발.'
WHERE id = 259;

UPDATE scholarship SET
  amount_detail = '등록금 전액, 1년 지급',
  application_period = '입학 시',
  application_method = '자동선발',
  description = '검도·펜싱·정구·복싱 특기자 대상(수시 모집).'
WHERE id = 260;

UPDATE scholarship SET
  application_period = '입학 시',
  application_method = '자동선발'
WHERE id = 261;

UPDATE scholarship SET
  amount_detail = '등록금 전액, 이후 직전학기 15학점 이상 취득·평점평균 3.5 이상 유지 시 일반학과 3년/한의예과 4년간 지급',
  application_period = '입학 시',
  application_method = '자동선발',
  description = '정시 단과대학별 수석 합격자 대상.'
WHERE id = 262;

UPDATE scholarship SET
  amount_detail = '학과·학년별 재학인원 대비 성적순 5단계 차등 지급
최우수성적: 등록금 100%
성적우수A: 70%
성적우수B: 50%
성적우수C: 30%
성적우수D: 15%
(공통 최소기준: 직전학기 15학점 이상 취득(최종학년 10학점)·평점평균 3.0 이상, F·N·미이수 과목 있으면 제외)',
  application_period = '매 학기',
  application_method = '자동선발',
  description = NULL
WHERE id = 263;

UPDATE scholarship SET
  amount_detail = '소득분위별 차등 지급',
  application_period = '매 학기',
  application_method = '자동선발',
  description = '국가장학금 1~8분위 대상자 중 직전학기 12학점 이상 취득·백분위점수 80점 이상인 자.'
WHERE id = 264;

UPDATE scholarship SET
  amount_detail = '등록금의 20%',
  application_period = '매 학기',
  application_method = '자동선발',
  description = '국가장학금 0분위(기초생활수급자) 대상자 중 직전학기 12학점 이상 취득·백분위점수 80점 이상인 자.'
WHERE id = 265;

UPDATE scholarship SET
  amount_detail = '등록금 일부, 매학기(장학사정관 심사로 차등 지급)',
  application_method = '신청(장학사정관 심사)',
  description = '대상: 다자녀(3자녀 이상), 중증질병 및 상해(1년 이상 연속 의료비 정산서), 실직가정·재난 및 재해(주민센터 확인서), 긴급가계곤란자(부도·파산 관계서류), 희망장학금(부모 중 장애등급 1~3급), 다문화가정자녀(부모 중 한 사람이 외국인, 귀화자·결혼이민자 포함), 기타 경제적 어려움 소명자.'
WHERE id = 266;

UPDATE scholarship SET
  amount_detail = '등록금 일부',
  application_period = '매 학기',
  application_method = '자동선발',
  description = '당해학기 국가장학금 신청자 중 성적기준 미달로 수혜받지 못한 자(직전학기 백분위점수 80점 미만).'
WHERE id = 267;

UPDATE scholarship SET
  amount_detail = '등록금의 50%',
  application_period = '매 학기',
  application_method = '자동선발',
  description = '전임교원·정규직원의 직계자녀 대상. 직전학기 15학점 이상 취득(최종학년 10학점)·평점평균 3.0 이상(유급제도 시행학과는 2.5 이상) 필요.'
WHERE id = 268;

UPDATE scholarship SET
  amount_detail = '등록금의 50%',
  application_period = '매 학기',
  application_method = '자동선발',
  description = '법인 임직원, 부속병원 및 혜화병원 정규직원, 학교설립유공자의 직계자녀 대상.'
WHERE id = 269;

UPDATE scholarship SET
  amount_detail = '중증장애 100만원 / 경증장애 30만원',
  application_period = '매 학기',
  application_method = '자동선발',
  description = '장애지원센터에 등록된 장애학생 대상(직전학기 실점평균 70점 이상).'
WHERE id = 270;

UPDATE scholarship SET
  amount_detail = '학기당 30만원',
  application_method = '신청',
  description = '본교 재학생 중 부모 1인이 본교 졸업생인 경우.'
WHERE id = 271;

UPDATE scholarship SET
  amount_detail = '등록금 전액',
  application_method = '신청',
  description = '보훈청의 대학수업료 등 면제대상증명서를 발급받은 국가유공자 본인 및 그 자녀 대상(본인은 성적 제한 없음, 자녀는 직전학기 백분위점수 70점 이상). 국가보훈처/한국장학재단을 통한 교외 나라사랑장학금과는 별개의 대전대학교 자체 교내 장학금.'
WHERE id = 272;

UPDATE scholarship SET
  amount_detail = '등록금 전액',
  application_period = '매 학기',
  application_method = '자동선발',
  description = '국내 고등학교 졸업 또는 고졸 이상 학력 인정일로부터 5년 이내에 입학·편입학한 북한이탈주민 본인 및 그 자녀 대상(본인은 2회 연속 70점 미만이면 제한, 자녀는 직전학기 백분위점수 70점 이상).'
WHERE id = 273;

UPDATE scholarship SET
  amount_detail = '1차합격자: 등록금의 50%
2차합격자·최종합격자: 등록금 전액',
  application_period = '수시',
  application_method = '신청(합격 발표 후)',
  description = '국가고시(5급 이상) 및 이에 준하는 고시 1차·2차·최종 합격자 대상.'
WHERE id = 274;

UPDATE scholarship SET
  amount_detail = '학기당 50만원(각자 지급)',
  application_method = '신청',
  description = '직계가족 2인 이상이 본교 재학 중인 경우, 직전학기 성적 백분위점수 70점 이상인 재학생 각자 대상.'
WHERE id = 275;

UPDATE scholarship SET
  amount_detail = '성적별 차등 지급(등록금 일부)',
  application_period = '매 학기',
  application_method = '자동선발',
  description = '토플·IELTS·토픽(TOPIK)이 일정 성적 이상인 외국인 재학생 대상.'
WHERE id = 276;

UPDATE scholarship SET
  amount_detail = '수업료 전액',
  application_period = '매 학기',
  application_method = '자동선발',
  description = '현장실습교과목, 유연학기제에 따른 집중이수제, DJU나노디그리 교과목, 공유대학 교과목, 산업체요구형 캡스톤디자인 이수자 대상.'
WHERE id = 277;

UPDATE scholarship SET
  amount_detail = '본교 졸업자: 수업료의 70%
그 외 편입학 등록자: 수업료의 50%',
  application_period = '첫 학기 등록 시',
  application_method = '자동선발',
  description = '편입학 등록자 전원 대상.'
WHERE id = 278;

UPDATE scholarship SET
  amount_detail = '등록금 일부',
  application_period = '매 학기',
  application_method = '자동선발',
  description = '자기주도적 특별한 경험을 통해 1년간 비전을 설계·실행하는 자로서 5학기 이상 등록한 자(직전학기 교내외 장학금 수혜내역 없거나 일정금액 미만, 재학중 1회 수혜).'
WHERE id = 279;

UPDATE scholarship SET
  amount_detail = '등록금 일부(제한 없음)',
  application_method = '총장 재량 심사',
  description = '대외적으로 대전대학교의 위상을 드높인 자 또는 장학금 지급이 필요하다고 총장이 인정·승인한 자 대상(구체적 자격조건 없음, 총장 재량 심사).'
WHERE id = 280;

UPDATE scholarship SET
  amount_detail = '등록금 전액',
  application_period = '매 학기',
  application_method = '자동선발',
  description = '각종 대회에서 우수한 성적을 거둔 체육특기자 대상. 같은 계열로 전지훈련 참가자에게 등록금 일부를 수시 지급하는 "전지훈련장학금"도 있음.'
WHERE id = 281;

UPDATE scholarship SET
  amount_detail = '등록금 일부',
  application_period = '수시',
  description = '체육특기자 중 전지훈련에 참가하는 자 대상.'
WHERE id = 282;

UPDATE scholarship SET
  amount_detail = '등록금 일부',
  application_period = '수시',
  description = '전체 학과 대상. 교내·외 공모전 입상자나 학과 홍보 및 전공 특성화에 기여한 자.'
WHERE id = 283;

UPDATE scholarship SET
  amount_detail = '등록금 일부',
  application_period = '수시',
  description = '군사학과 재학생 대상: 여학생 생활관지원비, 잠재역량(텝스·졸업인증), 학과특성화, 해외연수 참여자.'
WHERE id = 284;

UPDATE scholarship SET
  amount_detail = '등록금의 15%',
  application_period = '매 학기',
  application_method = '자동선발',
  description = '계약학과 재학생 대상.'
WHERE id = 285;

UPDATE scholarship SET
  amount_detail = '등록금 일부',
  application_period = '수시',
  description = '외국어 관련 3개 세부 프로그램 이수/성적 우수자 대상: 정기토익(본교 개최 정기토익 2회 이상 응시, 500점 이상 취득자), 토익캠프(토익캠프 수료자), 외국어역량강화(어학 관련 프로그램 이수자).'
WHERE id = 286;

UPDATE scholarship SET
  amount_detail = '등록금 일부',
  application_period = '수시',
  description = '취업 관련 5개 세부 프로그램 참여/수료자 대상: 재학생직무체험(직무연수 수료자), 글로벌인재육성(4학년2학기 재학중 해외취업알선사업 참가자 또는 해외취업 근로계약 체결자), 취업동아리(엘리트코칭·취창업지원팀 주관 취업동아리 참가자), 취업리포터즈(취업리포터즈 선발·활동자), 취업역량제고(관련 교육과정 수료자).'
WHERE id = 287;

UPDATE scholarship SET
  amount_detail = '등록금 일부(대부분 수시 지급, 학생회임원봉사는 매학기)',
  description = '봉사·공로 관련 9개 세부 항목 대상: 학생회임원봉사(총학생회·단과대학학생회 임원, 동아리연합회 임원, 전학대 의장, 학회장), 국외봉사(국외봉사 참가자 중 모범자), 외국인봉사(통역의전요원·유학생봉사요원·유학생임원·버디), 봉사(각종 행사 및 교내외 부서 업무 참여자), 행사공로(대동제·비전위크·길거리·벚꽃나들이 등 행사 참여자), HRC(HRC 튜터·프로그램 참여자), 푸른별홍보대사, 입시홍보(학교투어·고교초청행사 지원, 출신고교 대상 입시홍보자), 학군단(모범후보생·학군여학우집체장학금·입영훈련우수자·문화탐방참여자·리더십·자치근무자).'
WHERE id = 288;

UPDATE scholarship SET
  amount_detail = '등록금 일부(등록금 고지서 감면 방식)',
  application_period = '2026-2학기: 2026-07-13~2026-07-16 18:00',
  application_method = '신청',
  description = '최근 2개 학기 성적을 비교해 큰 폭으로 향상된 학생 대상(평점평균이 1.1~2.0 이상 향상한 경우).'
WHERE id = 289;

UPDATE scholarship SET
  amount_detail = '등록금 일부',
  application_period = '매 학기',
  application_method = '자동선발',
  description = '파견희망국 공인어학능력 성적 소지자 중 교환학생으로 선발된 2~3학년 재학생 대상.'
WHERE id = 290;

UPDATE scholarship SET
  amount_detail = '등록금 일부',
  application_period = '매 학기',
  application_method = '자동선발',
  description = '하계·동계 단기해외연수 프로그램 이수자, 단기해외연수 결과보고대회 발표우수팀 대상.'
WHERE id = 291;

UPDATE scholarship SET
  amount_detail = '등록금 일부(누적 마일리지 500점 이상 시 전환, 한 학기 지급)',
  application_method = '신청',
  description = '6개 영역(학업/봉사/취업 등) 마일리지 누적점수 500점 이상인 재학생 대상.'
WHERE id = 292;

UPDATE scholarship SET
  amount_detail = '등록금 일부(대부분 수시/매학기 지급)',
  description = '역량강화 관련 6개 세부 항목 대상: 아너스장학금(프로그램 참가 적극성 및 교육성과 우수자, 평가 후 차등지급), 공모전및경시대회(교내 각종 공모전·경시대회 우수자), 도서관마일리지(도서포인트70%+좌석이용포인트30% 누적자), 독서인증(도서관 추천도서 읽고 시험 패스한 자), 학생역량강화장학금(비전탐색·비전설계·DUIMS·블로그기자단·ASEAN포럼·스포츠건강체력·학생홍보단·현장실습 등 프로그램 참여자, 한학기), 기금인출장학(발전기금·장학기금으로 적립된 장학금, 해당부서 요청에 의해 지급).'
WHERE id = 293;

UPDATE scholarship SET
  amount_detail = '6학점 이상: 10만원
9학점 이상: 20만원
(총 70명 이내)',
  application_period = '매 학기',
  application_method = '자동선발',
  description = '융·복합 전공교육과정 이수학생 대상. 동일학기 융복합전공 교과목(제1전공 포함) 6학점 이상 이수자 중 성적순 선발.'
WHERE id = 294;

UPDATE scholarship SET
  amount_detail = '등록금 일부, 연 1회 지급',
  application_period = '연 1회',
  application_method = '자동선발',
  description = '비교과 프로그램 참가 누적 포인트가 있는 자 대상.'
WHERE id = 295;

UPDATE scholarship SET
  amount_detail = '매년 약 2천만원 규모를 마일리지 취득 학생들에게 지급(연례 프로그램)',
  application_method = '신청(제출서류: 창업 마일리지 신청서·창업활동 수기·외부 프로그램 참여 증빙자료(상장·수료증)·롤모델 창업특강 수료증)',
  description = '창업교과/비교과 마일리지를 취득한 재학생 대상.'
WHERE id = 296;
