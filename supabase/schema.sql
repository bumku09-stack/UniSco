-- UniSco 데이터베이스 스키마 (개발자 기록용)
--
-- 이 파일은 실제로 실행되는 게 아니라, Supabase에 이미 만들어져 있는 테이블/설정을
-- git으로 기록해두기 위한 스냅샷입니다. 진짜 정의는 backend/app/models/ 의 Python
-- 코드(SQLModel)이고, 이 파일은 그 코드를 한 번 실행해서 실제로 만들어진 결과를
-- 그대로 옮겨 적은 것입니다. 스키마 바뀌면 이 파일도 같이 업데이트할 것.
--
-- (비개발자 친구분은 이 파일 안 보셔도 됩니다 — supabase/README.md 상단 안내만 보시면 됩니다.)

-- 자격조건 값들을 정해진 옵션으로만 제한하는 타입들.
-- 값은 소문자(예: 'male', 'foreigner_only')로 저장됨 — SQLAlchemy 기본값(대문자, enum
-- 멤버 이름)을 values_callable로 오버라이드해서 API JSON/문서와 casing을 통일함.
CREATE TYPE gender AS ENUM ('male', 'female');
CREATE TYPE militarystatus AS ENUM ('completed', 'exempted', 'not_served');
CREATE TYPE foreignereligibility AS ENUM ('korean_only', 'foreigner_only');
CREATE TYPE enrollmentstatus AS ENUM ('undergrad_enrolled', 'undergrad_leave', 'post_undergrad');
CREATE TYPE degreelevel AS ENUM ('masters', 'doctoral', 'integrated_ms_phd');

CREATE TABLE scholarship (
    id SERIAL NOT NULL,
    name VARCHAR NOT NULL,
    provider VARCHAR,
    description VARCHAR,
    amount INTEGER,
    application_url VARCHAR,
    min_age INTEGER,
    max_age INTEGER,
    required_gender gender,
    eligible_region VARCHAR,
    required_military_status militarystatus,
    max_income_bracket INTEGER,
    min_gpa FLOAT,
    requires_disability BOOLEAN,
    foreigner_eligibility foreignereligibility,
    -- (레거시) 구조화 전 원문 텍스트 — 매칭에는 안 쓰고 참고용/미래 정밀매칭 재료로 남겨둠
    grade_level VARCHAR,
    major VARCHAR,
    affiliated_institution VARCHAR,
    min_credits VARCHAR,
    admission_score_condition VARCHAR,
    headcount VARCHAR,
    application_period VARCHAR,
    -- 구조화된 정밀 매칭용 필드 (2026-07-28 추가)
    eligible_university VARCHAR,
    eligible_college VARCHAR,
    required_enrollment_status enrollmentstatus,
    min_grade INTEGER,
    max_grade INTEGER,
    required_degree_level degreelevel,
    PRIMARY KEY (id)
);

-- PostgREST(Supabase 자동 REST API) 경로로 익명 접근되는 것을 막음.
-- Studio(친구분 데이터 입력)와 backend/의 직접 Postgres 연결에는 영향 없음.
-- 정책(policy)을 따로 안 만든 건 의도한 것 — PostgREST 경로 자체를 완전히 막는 게 목적.
ALTER TABLE scholarship ENABLE ROW LEVEL SECURITY;
