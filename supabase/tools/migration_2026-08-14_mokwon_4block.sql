-- 목원대학교 25건 4블록(금액/기간/신청방식) 분리

UPDATE scholarship SET
  amount_detail = '등록금 100% 감면',
  application_period = NULL,
  application_method = '자동선발',
  description = '각 학부(과)별 직전학기 평점평균 최고 성적자 대상.'
WHERE id = 175;

UPDATE scholarship SET
  amount_detail = '등록금 80% 감면',
  application_period = NULL,
  application_method = '자동선발',
  description = '학과 내 학년별 최우수 성적자 대상.'
WHERE id = 176;

UPDATE scholarship SET
  amount_detail = '등록금 50%/35%/20% 감면(등급별 차등)',
  application_period = NULL,
  application_method = '자동선발',
  description = '학과/학년별 우수 성적자 대상.'
WHERE id = 177;

UPDATE scholarship SET
  amount_detail = '등록금 범위 내 지급',
  application_period = NULL,
  application_method = '자동선발',
  description = '복수전공·융복합전공을 이수 중인 학생 대상.'
WHERE id = 178;

UPDATE scholarship SET
  application_period = NULL,
  application_method = '자동선발',
  description = '한국장학재단 소득분위 0~8분위 국가장학금 신청자 대상.'
WHERE id = 179;

UPDATE scholarship SET
  application_period = NULL,
  application_method = '학부(과)장 추천',
  description = '학부(과)장 추천 학생 대상.'
WHERE id = 180;

UPDATE scholarship SET
  amount_detail = '입학금 및 등록금 전액 감면',
  application_period = '상시',
  application_method = '서류제출(교육지원대상자증명서)',
  description = '국가유공자 본인·배우자·직계자녀 대상.'
WHERE id = 181;

UPDATE scholarship SET
  amount_detail = 'A급 100만원, B급 70만원(등급별 차등)',
  application_period = NULL,
  application_method = '자동선발',
  description = '장애인 등록 학생 대상.'
WHERE id = 182;

UPDATE scholarship SET
  amount_detail = '등록금 전액 감면',
  application_period = NULL,
  application_method = '자동선발',
  description = '교직원 직계자녀 대상.'
WHERE id = 183;

UPDATE scholarship SET
  amount_detail = '등록금 전액 감면',
  application_period = NULL,
  application_method = '자동선발',
  description = '북한이탈주민 대상.'
WHERE id = 184;

UPDATE scholarship SET
  amount_detail = '50만원 지급',
  application_period = NULL,
  application_method = '자동선발',
  description = '다문화가정 학생 대상.'
WHERE id = 185;

UPDATE scholarship SET
  amount_detail = '50만원 지급',
  application_period = '매 학기',
  application_method = '봉사시간 인증 후 선발',
  description = '학기당 봉사활동 120시간 이상 수행한 학생 대상.'
WHERE id = 186;

UPDATE scholarship SET
  application_period = NULL,
  application_method = '심의',
  description = '대외 활동 등으로 대학의 명예를 선양한 학생 대상(성적 제한 없음, 사례별 심의).'
WHERE id = 187;

UPDATE scholarship SET
  amount_detail = '등록금 40% 이상 감면',
  application_period = NULL,
  application_method = '자동선발',
  description = '외국인 유학생 대상.'
WHERE id = 188;

UPDATE scholarship SET
  amount_detail = '4년간 등록금 전액+기숙사비 지원(2년차부터 평점 3.5 이상 유지 조건)',
  application_period = '입학 시',
  application_method = '자동선발',
  description = '수시 학생부교과전형 수석합격자 대상.'
WHERE id = 189;

UPDATE scholarship SET
  amount_detail = '1년 등록금 전액(2년차부터 평점 3.5 이상 유지 조건)',
  application_period = '입학 시',
  application_method = '자동선발',
  description = '수시 교과전형 등 단과대학 수석합격자 대상.'
WHERE id = 190;

UPDATE scholarship SET
  amount_detail = '1학기 등록금 70% 지원',
  application_period = '입학 시',
  application_method = '자동선발',
  description = '각 학부 수시전형 수석합격자 대상.'
WHERE id = 191;

UPDATE scholarship SET
  amount_detail = '1년 등록금 전액(2년차부터 평점 3.5 이상 유지 조건)',
  application_period = '입학 시',
  application_method = '자동선발',
  description = '수시 학생부종합전형 수석합격자 대상.'
WHERE id = 192;

UPDATE scholarship SET
  amount_detail = '4년 등록금 전액+학업장려금 연 320만원(2년차부터 평점 3.5 이상 유지 조건)',
  application_period = '입학 시',
  application_method = '자동선발',
  description = '정시모집 수능 국어·수학·영어 모두 1등급 대상.'
WHERE id = 193;

UPDATE scholarship SET
  amount_detail = '4년 등록금 전액+연 120만원(2년차부터 평점 3.5 이상 유지 조건)',
  application_period = '입학 시',
  application_method = '자동선발',
  description = '정시모집 수능 3과목 합 4등급 이내 대상.'
WHERE id = 194;

UPDATE scholarship SET
  amount_detail = '4년 등록금 전액+연 80만원(2년차부터 평점 3.5 이상 유지 조건)',
  application_period = '입학 시',
  application_method = '자동선발',
  description = '정시모집 수능 3과목 합 5등급 이내 대상.'
WHERE id = 195;

UPDATE scholarship SET
  amount_detail = '1위: 4학기
2위: 2학기
3위: 1학기
(등록금 100% 지원)',
  application_period = '상시',
  application_method = '서류제출(입상실적증명서)',
  description = '음악·미술 등 실기전형 입상자 대상.'
WHERE id = 196;

UPDATE scholarship SET
  amount_detail = '1학기 등록금 전액 지원',
  application_period = '상시',
  application_method = '서류제출(공인영어시험 성적표)',
  description = 'TOEIC 900점 이상 또는 TOEFL IBT 100점 이상 신입생 대상.'
WHERE id = 197;

UPDATE scholarship SET
  amount_detail = '첫 학기 100만원 지급',
  application_period = '상시',
  application_method = '서류제출(부모 졸업증명서)',
  description = '부모 모두 목원대학교 졸업생인 신입생 대상.'
WHERE id = 198;

UPDATE scholarship SET
  amount_detail = '최초합격: 1학기 80만원 감면
충원합격: 1학기 40만원 감면',
  application_period = '입학 시',
  application_method = '자동선발',
  description = NULL
WHERE id = 199;
