-- 배재대학교 19건 4블록(금액/기간/신청방식) 분리 + 누락 구조화 필드 보강

UPDATE scholarship SET
  amount_detail = '4년간 등록금 전액 지원(2년차부터는 평점평균 3.7 이상 유지 조건)',
  application_period = '입학 시',
  application_method = '자동선발',
  description = '신입생 전체수석 대상.',
  min_credits_last_semester = 15
WHERE id = 154;

UPDATE scholarship SET
  amount_detail = '1년~4년 등록금 전액 지원(등급별 차등)',
  application_method = '신청',
  description = '수능성적 우수자(국어·수학 3등급, 영어 2등급) 대상.'
WHERE id = 155;

UPDATE scholarship SET
  amount_detail = '1년 등록금 전액~50% 지원(입상 등급별 차등)',
  application_method = '신청(입상실적 증빙 필요)',
  description = '신입생 중 경연대회 입상자 대상.'
WHERE id = 156;

UPDATE scholarship SET
  amount_detail = '입학학기 등록금 전액 지원',
  application_period = '입학 시',
  application_method = '자동선발',
  description = '체육특기자 전형 입학생 대상.'
WHERE id = 157;

UPDATE scholarship SET
  amount_detail = '입학 후 최초학기 등록금 전액 지원',
  application_period = '입학 시',
  application_method = '자동선발',
  description = '만 30세 이상 입학생 대상.'
WHERE id = 158;

UPDATE scholarship SET
  amount_detail = '전적대학 성적 기준으로 등급별 차등 지원',
  application_period = '입학 시',
  application_method = '자동선발',
  description = '편입학생 대상.'
WHERE id = 159;

UPDATE scholarship SET
  application_method = '신청',
  description = '배재대학교 출신 부모(동문)의 자녀 대상.'
WHERE id = 160;

UPDATE scholarship SET
  amount_detail = '등록금 30% 이내 지원',
  application_method = '신청',
  description = '2촌 이내 친족이 동시에 배재대에 재적 중인 학생 대상.'
WHERE id = 161;

UPDATE scholarship SET
  amount_detail = '등록금 전액 지원',
  application_method = '신청',
  description = '북한이탈주민 대상.'
WHERE id = 162;

UPDATE scholarship SET
  amount_detail = '등록금 전액 지원',
  application_method = '신청',
  description = '배재학당 소속 교직원의 자녀 대상.'
WHERE id = 163;

UPDATE scholarship SET
  amount_detail = '등록금 30% 지원',
  application_method = '신청',
  description = '장애학생 또는 다문화가정 학생 대상.'
WHERE id = 164;

UPDATE scholarship SET
  amount_detail = '수업료 전액 지원',
  application_period = NULL,
  application_method = '자동선발',
  description = '직전학기 평점평균 3.5 이상 재학생 대상(F학점 없음).',
  min_credits_last_semester = 15
WHERE id = 165;

UPDATE scholarship SET
  amount_detail = '1학기 수업료 전액 지원',
  application_method = '신청(TOEIC 성적표 제출)',
  description = 'TOEIC 900점 이상(영어 전공자는 950점 이상) 재학생 대상.'
WHERE id = 166;

UPDATE scholarship SET
  amount_detail = '등록금 50% 이내 지원',
  application_method = '신청',
  description = '기초생활수급자·차상위계층·한부모가족 학생 대상.'
WHERE id = 167;

UPDATE scholarship SET
  application_period = NULL,
  application_method = '학부(과)장 추천',
  description = '저소득층 학생 대상.'
WHERE id = 168;

UPDATE scholarship SET
  amount_detail = '등록금 전액 지원',
  application_method = '신청',
  description = '국가보훈대상자 대상.'
WHERE id = 169;

UPDATE scholarship SET
  application_method = '신청',
  description = '기독교대한감리회 교역자 자녀 대상.'
WHERE id = 170;

UPDATE scholarship SET
  application_method = '신청',
  description = '초·중·고등학교 교사의 자녀 대상.'
WHERE id = 171;

UPDATE scholarship SET
  amount_detail = '수업료 일부 지원',
  application_period = NULL,
  application_method = '추천',
  description = '학생자치기구 임원·ROTC·체육부 등 소속 학생 중 추천을 받은 자 대상.',
  min_gpa = 1.91
WHERE id = 172;
