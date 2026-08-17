-- 배재대학교 재검증(원문 재대조) — 신청기간 오류 정정 + 확실한 금액/조건 오류 정정
-- 원문 재확인 결과 "제출서류(매학기 6,12월)"가 거의 전 항목에 반복되는 실제 규정이고,
-- 제가 이전에 넣어둔 "2026년 공고 미확인, 직전 회차: 2025-09-01~09-25"라는 구체적 날짜는
-- 원문 어디에도 없음(KTU/목원대와 같은 유형의 문제).

UPDATE scholarship SET
  application_period = '매 학기 6월·12월(제출서류 접수기간)',
  application_method = '신청(서류 제출)'
WHERE id IN (155,156,160,161,162,163,164,166,167,169,170,171)
  AND application_period = '2026년 공고 미확인, 직전 회차: 2025-09-01~09-25';

-- id=155 배재하워드장학금: 등급별 혜택이 완전히 달랐음(1등급 트랙엔 학습장려금 300만원/학기가
-- 별도로 붙는데 누락돼 있었고, 3단계 등급 기준도 부정확했음)
UPDATE scholarship SET
  amount_detail = '국어·수학·영어 중 2개 영역 이상 전부 1등급: 4년 등록금 전액 + 학기당 학습장려금 300만원
국어2등급·수학2등급·영어1등급 이내(수시입학생 한정): 2년 등록금 전액
국어3등급·수학3등급·영어2등급 이내: 1년 등록금 전액',
  description = '대학수학능력시험 성적 기준 신입생 대상.'
WHERE id = 155;

-- id=160 배재가족자녀장학금: 금액이 통째로 빠져있었음
UPDATE scholarship SET
  amount_detail = '등록금(최초학기) 50만원(중복수혜 가능)',
  application_method = '신청(관련서류 제출)'
WHERE id = 160;

-- id=161 한가족장학금: GPA 조건 누락
UPDATE scholarship SET min_gpa = 1.91 WHERE id = 161;

-- id=163 교직원복지장학금: GPA 누락, "법인교직원복지장학금"은 별도 대상(대학 재직 vs 재단 재직)
UPDATE scholarship SET
  min_gpa = 2.75,
  description = '본교(배재대학교)에 재직 중인 교직원(정규직)의 자녀 대상, 정규학기까지 지급(정년·명예퇴직자는 재직 시와 동일 지급, 계약직원은 재직 중에 한함).'
WHERE id = 163;

-- id=164 배재사랑장학금: GPA 누락
UPDATE scholarship SET min_gpa = 1.91 WHERE id = 164;

-- id=167 희망복지장학금: "50% 이내"가 아니라 그냥 "50%", GPA 조건 누락
UPDATE scholarship SET
  amount_detail = '등록금 50%',
  min_gpa = 1.91,
  description = '기초생활수급자·차상위본인부담경감대상자·한부모가족증명서 제출 학생 대상.'
WHERE id = 167;

-- id=169 국가유공장학금: 교육보호 대상자는 성적기준이 면제되는데 이 분기가 빠져있었음
UPDATE scholarship SET
  amount_detail = '등록금 전액(국고 50%, 교비 50%) — 교육보호 대상자는 교비 100%',
  min_gpa = 1.75,
  description = '국가보훈대상자 본인 및 직계자녀 대상(교육보호 대상자는 성적 기준 없음).'
WHERE id = 169;

-- id=170/171 교역직계·교육직계장학금: 금액이 통째로 빠져있었음
UPDATE scholarship SET amount_detail = '수업료 일부(20만원, 중복수혜 가능)' WHERE id IN (170, 171);
