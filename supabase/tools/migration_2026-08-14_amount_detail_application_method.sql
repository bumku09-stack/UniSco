-- 2026-08-14: 상세페이지 "장학금 소개"를 금액/기간/신청방식/자격조건 4블록으로 재구성하기
-- 위해 컬럼 2개 추가. 매칭 필터링에는 안 씀(참고 표시용, description/application_period와
-- 동일한 성격).
--
-- amount_detail: 금액 상세 서술 — 지급주기/지급기간(매학기, N년간 등), 순위별 차등 금액 등
--   (예: "등록금 전액, 4년간 지급", "수석 전액·차석 50%")
-- application_method: 신청방식 — 자동선발/직접신청 여부와 그 방식 설명
--   (예: "정시 전형 결과로 자동 선발", "온라인 신청서 제출")
-- application_period는 앞으로 순수 신청기간(날짜/기간)만 담고, 지금까지 여기 섞여있던
-- "자동선발" 같은 방식 설명은 application_method로 분리함(기존 366건+ 데이터는 점진 백필).
--
-- 실행 방법: python run_sql.py migration_2026-08-14_amount_detail_application_method.sql

ALTER TABLE scholarship ADD COLUMN amount_detail VARCHAR;
ALTER TABLE scholarship ADD COLUMN application_method VARCHAR;
