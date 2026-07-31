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
-- undergrad_transfer(편입)는 2026-07-31 ALTER TYPE으로 추가됨. 매칭 시 undergrad_enrolled
-- 요구조건은 undergrad_transfer도 만족시키는 것으로 취급함(둘 다 "현재 재학중") —
-- backend/app/api/match.py의 _enrollment_status_matches() 참고.
CREATE TYPE enrollmentstatus AS ENUM ('undergrad_enrolled', 'undergrad_transfer', 'undergrad_leave', 'post_undergrad');
CREATE TYPE degreelevel AS ENUM ('masters', 'doctoral', 'integrated_ms_phd');
CREATE TYPE categoryl1 AS ENUM ('school_internal', 'school_external', 'support_fund');
CREATE TYPE categoryl2 AS ENUM (
    'academic_merit', 'welfare_living', 'special_target', 'activity_merit', 'research',
    'international_exchange', 'department_alumni',
    'national_scholarship', 'local_gov', 'private_foundation', 'association',
    'youth_living_support', 'activity_participation_support'
);

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
    -- 분류 체계 (자격조건 아님, 목록 표시/그룹핑용) (2026-07-28 추가)
    category_l1 categoryl1,
    category_l2 categoryl2,
    PRIMARY KEY (id)
);

-- PostgREST(Supabase 자동 REST API) 경로로 익명 접근되는 것을 막음.
-- Studio(친구분 데이터 입력)와 backend/의 직접 Postgres 연결에는 영향 없음.
-- 정책(policy)을 따로 안 만든 건 의도한 것 — PostgREST 경로 자체를 완전히 막는 게 목적.
ALTER TABLE scholarship ENABLE ROW LEVEL SECURITY;

-- 회원가입/로그인 (2026-07-31 추가). "user"는 Postgres 예약어라 큰따옴표 필요.
CREATE TABLE "user" (
    id SERIAL NOT NULL,
    username VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    hashed_password VARCHAR NOT NULL,
    is_verified BOOLEAN NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id)
);
CREATE UNIQUE INDEX ix_user_username ON "user" (username);
CREATE UNIQUE INDEX ix_user_email ON "user" (email);
ALTER TABLE "user" ENABLE ROW LEVEL SECURITY;

CREATE TABLE emailverification (
    id SERIAL NOT NULL,
    user_id INTEGER NOT NULL REFERENCES "user" (id),
    code VARCHAR NOT NULL,
    expires_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    is_used BOOLEAN NOT NULL,
    attempts INTEGER NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id)
);
CREATE INDEX ix_emailverification_user_id ON emailverification (user_id);
ALTER TABLE emailverification ENABLE ROW LEVEL SECURITY;
