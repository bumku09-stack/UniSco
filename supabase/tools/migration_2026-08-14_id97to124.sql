-- id=97~124 KAIST 장학금 페이지(kaist.ac.kr/kr/html/edu/03110503.html) 재대조
-- 발견: id=99/100의 min_gpa=2.7이 KAIST 자체 4.3만점 기준 원문 그대로 들어가 있었음(우리
-- DB 컨벤션은 min_gpa를 항상 4.5만점 기준으로 저장) — 2.7×4.5/4.3=2.83으로 환산해서 수정.
-- id=102도 동일하게 환산.

UPDATE scholarship SET amount_detail='최대 1,743,000원/학기', application_method='자동선발 — 별도 신청 절차 없이 선발', admission_score_condition='전체 재학생', headcount='정원 내(구체적 인원수 원문에 없음)', description=NULL WHERE id=97;
UPDATE scholarship SET amount_detail='최대 1,690,000원/학기', application_method='자동선발 — 별도 신청 절차 없이 선발', admission_score_condition='2학기 이내 재학생(1학년)', headcount='정원 내(구체적 인원수 원문에 없음)', description=NULL WHERE id=98;
UPDATE scholarship SET amount_detail='최대 1,690,000원/학기', application_method='자동선발 — 별도 신청 절차 없이 선발', min_gpa=2.83, headcount='정원 내(구체적 인원수 원문에 없음)', description=NULL WHERE id=99;
UPDATE scholarship SET amount_detail='최대 1,690,000원/학기', application_method='자동선발 — 별도 신청 절차 없이 선발', min_gpa=2.83, headcount='정원 내(구체적 인원수 원문에 없음)', description=NULL WHERE id=100;
UPDATE scholarship SET amount_detail='최대 1,690,000원/학기', application_method='자동선발 — 별도 신청 절차 없이 선발', headcount='정원 내(구체적 인원수 원문에 없음)', description='2015년도 이전 입학생 대상 — 현재는 거의 해당자가 없을 가능성이 높은 경과조치성 장학금(원문에 폐지 명시는 없음)' WHERE id=101;
UPDATE scholarship SET amount_detail='최대 500,000원/학기', application_method='자동지급 — 국가장학금 또는 교외장학금 수혜자 대상 자동 지급', min_gpa=2.83, min_gpa_basis='semester', headcount='정원 내(구체적 인원수 원문에 없음)', description='국가장학금 또는 교외장학금 수혜자만 해당' WHERE id=102;
UPDATE scholarship SET amount_detail='350,000원/월', application_method='입학사정 시 추천 — 별도 신청 불필요', admission_score_condition='입학 후 2년 경과 후 성적 판정', headcount='학과/단대별 TO 내', description=NULL WHERE id=103;
UPDATE scholarship SET amount_detail='1,000,000원/월', application_method='입학사정 시 추천 — 별도 신청 불필요', headcount='학과/단대별 TO 내', description=NULL WHERE id=104;
UPDATE scholarship SET amount_detail='300,000원/월', application_method='입학사정 시 추천 — 별도 신청 불필요', headcount='학과/단대별 TO 내', description=NULL WHERE id=105;
UPDATE scholarship SET amount_detail='500,000원', application_method='직접 신청 필요 — 학생과에 서류 제출(구체적 경로는 공고 원문 참고)', description=NULL WHERE id=106;
UPDATE scholarship SET amount_detail='1,000,000원/학기', application_method='자동선발 — 3~8학기, 15학점 이상 이수자 중 평점 순으로 선발', description=NULL WHERE id=107;
UPDATE scholarship SET amount_detail='800,000원/학기', application_method='자동선발 — 3~8학기, 15학점 이상 이수자 중 평점 순으로 선발', description=NULL WHERE id=108;
UPDATE scholarship SET amount_detail='800,000원/학기', application_method='자동선발 — 3~8학기, 15학점 이상 이수자 중 평점 순으로 선발', description=NULL WHERE id=109;
UPDATE scholarship SET amount_detail='2,000,000원/학기', application_method='학생 신청 대상 아님 — 회장/비상대책위원장 재직 여부로 자동 선발', description=NULL WHERE id=110;
UPDATE scholarship SET amount_detail='1,500,000원/학기', application_method='학생 신청 대상 아님 — 부회장/부비상대책위원장 재직 여부로 자동 선발', description=NULL WHERE id=111;
UPDATE scholarship SET amount_detail='500,000원/학기', application_method='학생 신청 대상 아님 — 임원진/학과대표 재직 여부로 자동 선발', description=NULL WHERE id=112;
UPDATE scholarship SET amount_detail='1,000,000원', application_method='추천 필요 — 타의 모범이 되는 학생으로 추천받아야 함', description=NULL WHERE id=113;
UPDATE scholarship SET amount_detail='4,000,000원(학기별 2,000,000원)', application_method='추천 필요 — 학업 우수·학술연구능력·리더십 자질 기준 추천 선발', description=NULL WHERE id=114;
UPDATE scholarship SET amount_detail='300,000원/월', application_method='자동지급 — 국가장학금 신청자 중 소득 0구간 해당자에게 자동 지급', description=NULL WHERE id=115;
UPDATE scholarship SET amount_detail='250,000원/월', application_method='자동지급 — 국가장학금 신청자 중 차상위계층 해당자에게 자동 지급', description=NULL WHERE id=116;
UPDATE scholarship SET amount_detail='200,000원/월', application_method='자동지급 — 국가장학금 신청자 중 소득 1구간 해당자에게 자동 지급', description=NULL WHERE id=117;
UPDATE scholarship SET amount_detail='250,000원/월', application_method='자동지급 — 국가장학금 신청 외국인 유학생에게 자동 지급', description=NULL WHERE id=118;
UPDATE scholarship SET amount_detail='200,000원/월', application_method='자동지급 — 국가장학금 신청자 중 기초생활수급자·차상위계층에게 자동 지급', description=NULL WHERE id=119;
UPDATE scholarship SET amount_detail='145,000원/월', application_method='입학사정 시 추천 — 학사과정 수시·정시 우수 입학생 대상, 별도 신청 불필요', headcount='정원 내(구체적 인원수 원문에 없음)', description=NULL WHERE id=120;
UPDATE scholarship SET amount_detail='3,000,000원(1회)', application_method='입학사정 시 추천 — 별도 신청 불필요', description=NULL WHERE id=121;
UPDATE scholarship SET amount_detail='연 700,000원', application_method='실적 제출 필요 — 연간 등산 실적 7회 이상 증빙', description=NULL WHERE id=122;
UPDATE scholarship SET amount_detail='연 300,000원', application_method='실적 제출 필요 — 연간 등산 실적 3~6회 증빙', description=NULL WHERE id=123;
UPDATE scholarship SET amount_detail='월 300,000원, 4개월 지급', application_method='직접 신청 필요 — 학생과에 서류 제출(구체적 경로는 공고 원문 참고)', description=NULL WHERE id=124;
