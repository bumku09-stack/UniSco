-- id=125~133 KAIST 학과별 장학금(원자력및양자공학과/신소재공학과/화학과) — 기존 description
-- 재분류. id=128은 min_gpa=3.0이 KAIST 4.3만점 원문 그대로였음 → 4.5만점 기준 3.14로 환산.
UPDATE scholarship SET amount_detail='50~100만원', application_method='직접 신청 필요(구체적 경로는 학과 공고 참고)', admission_score_condition='학부 3학년 이상, 경제적 어려움이 있는 학생 우선 선발', description=NULL WHERE id=125;
UPDATE scholarship SET amount_detail='100만원', application_method='학과 추천 필요(구체적 경로는 학과 공고 참고)', admission_score_condition='학부/대학원 성적·연구 우수자', description=NULL WHERE id=126;
UPDATE scholarship SET amount_detail='200만원', application_method='학과 추천 필요(구체적 경로는 학과 공고 참고)', admission_score_condition='우수 학부/대학원생', description=NULL WHERE id=127;
UPDATE scholarship SET amount_detail='20만원', application_method='자동선발 — 별도 신청 절차 없이 학과 성적 기준으로 선발', min_gpa=3.14, min_gpa_basis='semester', description=NULL WHERE id=128;
UPDATE scholarship SET amount_detail='50만원', application_method='자동선발 — 별도 신청 절차 없이 성적 기준으로 선발', admission_score_condition='2~4학년 성적우수자', description=NULL WHERE id=129;
UPDATE scholarship SET amount_detail='25만원', application_method='우수논문 제출 필요', admission_score_condition='우수논문 저자', description=NULL WHERE id=130;
UPDATE scholarship SET amount_detail='학기당 200만원', application_method='직접 신청 필요(구체적 경로는 학과 공고 참고)', admission_score_condition='신소재공학과 학부 3~4학년, 경제적 어려움이 있는 학생', description=NULL WHERE id=131;
UPDATE scholarship SET amount_detail='200만원(1회)', application_method='직접 신청 필요(구체적 경로는 학과 공고 참고)', admission_score_condition='화학과 학부생 대상, 봉사활동·생활고·리더십 등을 고려해 선발', description=NULL WHERE id=132;
UPDATE scholarship SET amount_detail='100만원(1회)', application_method='자동선발 — 별도 신청 절차 없이 선발', admission_score_condition='화학과 대학원 신입생 우수자', description=NULL WHERE id=133;
