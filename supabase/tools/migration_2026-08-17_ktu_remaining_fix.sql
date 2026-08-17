-- 2026-08-17 침신대 재검증 나머지 8건 + 원문에서 발견된 누락 장학금 2건 추가

BEGIN;

UPDATE scholarship
SET description = '한국침례회 해외선교회 소속 장기선교사(북한 선교사 포함)의 자녀 대상(재외국민교육원 수혜자는 제외).'
WHERE id = 325;

UPDATE scholarship
SET amount_detail = '수업료 50% 지원',
    description = '북한이탈주민의 보호 및 정착지원에 관한 법률에 따라 정착지원금을 지원받는 재학생 대상(대응 지원, 한 번 신청으로 졸업 시까지 인정).'
WHERE id = 330;

UPDATE scholarship
SET description = '취창업지원센터의 추천을 받은 학생 대상(각종 대회 격려 포함).'
WHERE id = 341;

UPDATE scholarship
SET description = '사회복지학과·유아교육과는 수시에서 성적우수B, 정시에서 성적우수A로 선발하며, 나머지 학과는 수시·정시 통합 입시총점 상위자 순으로 선발.'
WHERE id = 344;

UPDATE scholarship
SET description = '대학수학능력시험 국어·수학·영어 전 영역 1등급(예능계열 제외) 신입생 대상.'
WHERE id = 345;

UPDATE scholarship
SET description = '2026학년도 신입학·편입학생 대상 1년간 한정 지원.'
WHERE id = 347;

UPDATE scholarship
SET description = '일반대학원 기독교교육전공 재학생 대상(1순위 M.A.(C).E., 2순위 Ph.D.(기독교교육학)).'
WHERE id = 359;

-- 원문(mn303)에 있는데 45건 DB에 빠져있던 별개 장학금 2건 추가
INSERT INTO scholarship (name, provider, eligible_university, application_url, amount_detail, application_period, application_method, min_grade, description)
VALUES
('겨자씨장학금(기금이자장학)', '한국침례신학대학교', '한국침례신학대학교', 'http://www.kbtus.ac.kr/kor/CMS/Contents/Contents.do?mCode=MN303', '등록금 이내 지급', '학기말 시험기간', '신청', 1, '성적이 우수하고 가정 형편이 어려운 학생 대상.'),
('기타기금 이자장학금', '한국침례신학대학교', '한국침례신학대학교', 'http://www.kbtus.ac.kr/kor/CMS/Contents/Contents.do?mCode=MN303', '등록금 이내 지급', '학기말 시험기간', '신청', 1, '장학사정관 심의로 결정.');

COMMIT;
