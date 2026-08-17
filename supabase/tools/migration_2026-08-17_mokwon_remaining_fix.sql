-- 2026-08-17 목원대 재검증 나머지 14건 정정

BEGIN;

UPDATE scholarship
SET min_gpa = 3.5,
    min_credits_last_semester = 14,
    description = '재학중 직전학기 평점평균 3.5 이상, 17학점(최종학년은 14학점) 이상 취득한 자 중 학과 내 학년별 최우수 성적자 대상.'
WHERE id = 176;

UPDATE scholarship
SET min_gpa = 3.5,
    min_credits_last_semester = 14,
    description = '재학중 직전학기 평점평균 3.5 이상, 17학점(최종학년은 14학점) 이상 취득한 자 중 학과/학년별 우수 성적자 대상.'
WHERE id = 177;

UPDATE scholarship
SET min_gpa = 3.0,
    min_credits_last_semester = 14,
    description = '복수전공·융복합전공·부전공 중 1개 이상을 이수 중인 재학생 대상(직전학기 평점평균 3.0 이상, 취득학점 17학점(최종학년 14학점) 이상, 해당 전공 교과목 직전학기 6학점 이상 취득).'
WHERE id = 178;

UPDATE scholarship
SET amount_detail = '교내 장학금 예산범위 내 등록금 일부 감면'
WHERE id = 179;

UPDATE scholarship
SET description = '국가유공자 본인·배우자·직계자녀 대상(본인·배우자는 성적 제한 없음, 직계자녀는 직전학기 평점평균 1.6 이상).'
WHERE id = 181;

UPDATE scholarship
SET amount = NULL,
    amount_detail = '본인 A급 100만원, 본인 B급 70만원, 부모 모두 A급 90만원, 부모 중 1인 A급 30만원(등급별 차등)'
WHERE id = 182;

UPDATE scholarship
SET min_gpa = 1.6,
    description = '북한이탈주민 본인 또는 그 자녀가 본교에 입학한 경우 대상(직전학기 평점평균 1.6 이상, 통일부 교육지원 업무기준에 의거 지원).'
WHERE id = 184;

UPDATE scholarship
SET min_gpa = 2.5,
    headcount = '단과대학별 3명',
    description = '학기당 봉사활동 120시간(30회) 이상 수행한 재학생 중 소속 대학장의 추천을 받은 자 대상(직전학기 평점평균 2.5 이상, 단과대학별 3명 한도).'
WHERE id = 186;

UPDATE scholarship
SET description = '단과대학 수석합격자 대상(수시: 교과전형·교과면접전형·실기교과전형·실기전형, 정시: 통합모집군 수석자도 동일 조건·금액으로 별도 지급, 연극영화영상학부·스포츠건강관리학과 제외).'
WHERE id = 190;

UPDATE scholarship
SET description = '학부(과) 수석합격자 대상(수시: 교과전형·교과면접전형·지역인재전형·실기교과전형·실기전형 통합, 정시도 동일 조건·금액으로 별도 지급, 연극영화영상학부·스포츠건강관리학과 제외).'
WHERE id = 191;

UPDATE scholarship
SET min_gpa = 3.0,
    description = '음악대학·미술디자인대학·웹툰애니메이션게임대학 실기전형 입상자 대상(고교 졸업 당해년도 입시 응시·합격자 한정, 전공실기 평점평균 3.5 이상 및 전체 평점평균 3.0 이상).'
WHERE id = 196;

UPDATE scholarship
SET description = 'TOEIC 900점 이상 또는 TOEFL IBT 100점 이상 신입생 대상(최근 2년 이내 취득 성적에 한해 1회 인정).'
WHERE id = 197;

UPDATE scholarship
SET amount_detail = '인문·사회계열 최초합격 1학기 80만원 감면(충원합격 40만원), 이공계열·연극영화영상학부 최초합격 1학기 100만원 감면(충원합격 50만원)',
    description = '교과전형·학생부종합전형 등으로 입학한 신입생 대상.'
WHERE id = 199;

UPDATE scholarship
SET foreigner_eligibility = 'foreigner_only'
WHERE id = 1171;

COMMIT;
