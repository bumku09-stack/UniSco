-- 2026-08-17 을지대 재검증 나머지 정정 (일현육성장학금 4종 마감일/카테고리, 을지가족/한마음봉사 설명 채움, 외국인장학금 조건 보완)
-- id=310의 "세종학당 중급2→토픽4급 인정" 매핑 문구는 원문 재확인이 더 필요해서 이번엔 손 안 댐

BEGIN;

UPDATE scholarship
SET application_deadline = '2026-05-20',
    category_l1 = 'school_internal',
    category_l2 = 'academic_merit'
WHERE id IN (1216,1217,1218,1219);

UPDATE scholarship
SET description = '교직원 직계자녀·협력병원 및 학교법인 재직자 자녀, 본교 졸업생 자녀, 또는 형제자매 2인 이상 재학 중인 학생 대상.'
WHERE id = 305;

UPDATE scholarship
SET description = '학생봉사단 "빛길" 활동자 또는 재학 중 누적 봉사시간 300시간 이상인 학생 대상.'
WHERE id = 314;

UPDATE scholarship
SET amount_detail = '평점평균 4.0 이상: 등록금 최소 50% 지원(토픽 성적별 차등, 예: 토픽 6급 80% 감면~)
3.0 이상: 최소 30% 지원(토픽 성적별 차등)
2.0 이상~3.0 미만: 등록금 1/5(20%) 지원(단, 토픽 3급 미만)
(세종학당 중급2 이수자는 토픽4급, 중급1 이수자는 토픽3급에 준하여 인정, 법무부 사회통합프로그램 이수자도 인정)'
WHERE id = 310;

COMMIT;
