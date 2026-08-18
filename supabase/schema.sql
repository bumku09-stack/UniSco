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
CREATE TYPE militarystatus AS ENUM ('completed', 'exempted', 'not_served', 'rotc_candidate');
CREATE TYPE dischargetype AS ENUM ('enlisted', 'officer_or_nco');
CREATE TYPE foreignereligibility AS ENUM ('korean_only', 'foreigner_only');
-- gpabasis(2026-08-02 추가, 'both'는 2026-08-03 추가): min_gpa가 직전학기 성적 기준인지
-- 전체 재학기간 누적(CGPA) 기준인지, 아니면 둘 다 동시에 만족해야 하는지 구분. NULL이면
-- 미지정 — matching.py에서 둘 중 하나만 만족해도 통과시키는 관대한 기본값으로 처리함
-- (matching_gaps.md 13번 참고).
CREATE TYPE gpabasis AS ENUM ('semester', 'cumulative', 'both');
-- languagetesttype/disabilitytype/specialstatus (2026-08-03 추가, matching_gaps.md 9·10·12번)
CREATE TYPE languagetesttype AS ENUM ('TOEIC', 'TOEFL', 'IELTS', 'TOPIK', '기타');
CREATE TYPE disabilitytype AS ENUM (
    'physical_impairment', 'learning_disability', 'medical_disability', 'mental_impairment',
    'muscular_dystrophy', 'developmental_impairment', 'disabled_parent'
);
-- specialstatus: Scholarship/SavedSpec 둘 다 다중 선택(TEXT[]로 저장, 아래 두 테이블 참고 —
-- Scholarship 쪽은 2026-08-03에 단일값에서 리스트로 변경, 배재사랑장학금 "장애학생 또는
-- 다문화가정" 같은 OR조건 표현 위함). 매칭 로직이 다른 필드들과 다름
-- (backend/app/core/matching.py의 special_status_matches() 참고). 이 CREATE TYPE 자체는
-- 실제 컬럼 타입으로는 안 쓰이고(둘 다 TEXT[]) Python 쪽 enum 값 참고용 문서화 목적.
CREATE TYPE specialstatus AS ENUM (
    'north_korean_defector', 'multicultural_family', 'child_care_facility',
    'student_council_officer', 'single_parent_family', 'grandparent_family',
    'multi_child_family', 'national_merit',
    -- 2026-08-03 추가 — 희망복지장학금·장학사정관장학금 등 복합조건 장학금 재분류하며 필요해짐
    'basic_livelihood_recipient', 'near_poor', 'severe_illness_or_injury',
    'job_loss_or_disaster', 'financial_emergency',
    -- 2026-08-12 추가 — 경쟁 서비스(이루리) 회원가입 폼 검토 중 발견, 실제 DB 재검토로 확인.
    'rural_student', 'parent_university_staff', 'parent_university_alumni'
);
-- undergrad_transfer(편입)는 2026-07-31 ALTER TYPE으로 추가됨. 매칭 시 undergrad_enrolled
-- 요구조건은 undergrad_transfer도 만족시키는 것으로 취급함(둘 다 "현재 재학중") —
-- backend/app/core/matching.py의 enrollment_status_matches() 참고.
CREATE TYPE enrollmentstatus AS ENUM ('undergrad_enrolled', 'undergrad_transfer', 'undergrad_leave', 'post_undergrad');
CREATE TYPE degreelevel AS ENUM ('masters', 'doctoral', 'integrated_ms_phd');
-- admissiontrack (2026-08-12 추가): major(전공)와 별개인 "어떻게 입학했는지" 축. 지금까지
-- 확인된 실제 사례는 체육특기자 전형뿐이라 그것만 전용 값, 나머지(예능특기자·농어촌전형 등)는
-- other_specialty로 뭉뚱그려 둠 — backend/app/models/enums.py의 AdmissionTrack 참고.
CREATE TYPE admissiontrack AS ENUM ('general', 'athletic_specialty', 'other_specialty');
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
    required_discharge_type dischargetype,
    max_income_bracket INTEGER,
    min_gpa FLOAT,
    min_gpa_basis gpabasis,  -- 2026-08-02 추가
    -- 2026-08-18 추가 — min_gpa(4.5만점 GPA)와 별개 축. 일부 외부(재단) 장학금은 성적조건을
    -- GPA가 아니라 100점 만점 백분위/백분율 점수로 걺("전체학기 평점 백분위 90점 이상" 등).
    -- 학생의 GPA를 본인 대학 만점 기준으로 100점 환산해서 비교(core/matching.py의
    -- normalized_percentile() 참고) — 공식 등급→백분율 환산표가 아니라 만점 대비 비율로
    -- 근사한 값이라는 한계 있음(사용자 확인 후 채택, 2026-08-18).
    min_score_percentile FLOAT,
    requires_disability BOOLEAN,
    required_disability_type disabilitytype,  -- 2026-08-03 추가
    foreigner_eligibility foreignereligibility,
    language_test_type languagetesttype,  -- 2026-08-03 추가
    language_test_min_score FLOAT,  -- 2026-08-03 추가
    required_special_status TEXT[] NOT NULL DEFAULT '{}',  -- 2026-08-03 추가, 같은날 단일->리스트 변경
    -- 2026-08-10 추가 — required_special_status(OR)와 별개로 "이 태그들 전부 다 있어야 함".
    required_special_status_all TEXT[] NOT NULL DEFAULT '{}',
    -- 2026-08-11 추가 — "이 태그 있으면 무조건 탈락"(excluded_major와 동일 컨벤션).
    excluded_special_status TEXT[] NOT NULL DEFAULT '{}',
    application_deadline DATE,  -- 2026-08-03 추가(matching_gaps.md 7번). NULL=상시/마감정보 없음
    -- (레거시) 구조화 전 원문 텍스트 — 매칭에는 안 쓰고 참고용/미래 정밀매칭 재료로 남겨둠
    grade_level VARCHAR,
    -- major: 2026-08-03부터 UserSpec.department와 실제 매칭에 씀(matching_gaps.md 2번) —
    -- 더는 순수 레거시가 아님, 위 목록에서 뺌
    major VARCHAR,
    -- 2026-08-10 추가 — "이 학과만 빼고 나머지 전부 됨"(major와 반대 방향).
    excluded_major VARCHAR,
    affiliated_institution VARCHAR,
    min_credits VARCHAR,
    -- 2026-08-12 추가 — min_credits 원문 중 "직전학기 N학점 이상"으로 안전하게 환산되는
    -- 경우만 구조화해서 실제 매칭에 씀(GPA와 동일한 패턴).
    min_credits_last_semester INTEGER,
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
    -- 2026-08-12 추가 — major와 별개인 "어떻게 입학했는지" 축(admissiontrack 참고).
    admission_track admissiontrack,
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
    -- 2026-08-13 카카오 로그인 추가로 email/hashed_password 둘 다 NOT NULL 제약 제거 —
    -- 소셜 전용 계정은 이메일 동의를 안 받았을 수 있고(email=NULL) 비밀번호 자체가 없음
    -- (hashed_password=NULL). Postgres UNIQUE 컬럼은 NULL을 여러 개 허용하므로 소셜 유저
    -- 여럿이 email=NULL이어도 유니크 제약과 충돌 안 함.
    email VARCHAR,
    hashed_password VARCHAR,
    is_verified BOOLEAN NOT NULL,
    -- 2026-08-13 추가 — 카카오 회원번호. None이면 카카오로 로그인한 적 없는 계정.
    kakao_id VARCHAR,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id)
);
CREATE UNIQUE INDEX ix_user_username ON "user" (username);
CREATE UNIQUE INDEX ix_user_email ON "user" (email);
CREATE UNIQUE INDEX ix_user_kakao_id ON "user" (kakao_id);
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

-- 유저별 저장된 스펙 (2026-07-31 추가). UserSpec(요청 바디로만 쓰이는 비-테이블
-- 스키마, backend/app/models/user_spec.py)의 저장형 짝 — 필드 구성이 동일함.
-- user_id가 UNIQUE라서 유저당 최대 한 행만 존재(1:1) — 있으면 "스펙 설정 완료".
CREATE TABLE savedspec (
    id SERIAL NOT NULL,
    user_id INTEGER NOT NULL REFERENCES "user" (id),
    university VARCHAR NOT NULL,
    college VARCHAR NOT NULL,
    department VARCHAR,  -- 2026-08-03 추가(matching_gaps.md 2번), 선택 입력
    semester_gpa FLOAT NOT NULL,  -- 2026-08-02: 기존 gpa 컬럼을 semester_gpa로 개명
    cumulative_gpa FLOAT NOT NULL,  -- 2026-08-02 신규 추가
    credits_last_semester INTEGER,  -- 2026-08-12 추가, 선택 입력(null=모름)
    age INTEGER NOT NULL,
    gender gender NOT NULL,
    region VARCHAR NOT NULL,
    district VARCHAR,  -- 2026-08-05 추가(matching_gaps.md 14번), 선택 입력(세종 등은 없음)
    parent_region VARCHAR,  -- 2026-08-05 추가(matching_gaps.md 19번), 선택 입력
    parent_district VARCHAR,  -- 2026-08-05 추가(matching_gaps.md 14번 후속), 선택 입력
    military_status militarystatus NOT NULL,
    discharge_type dischargetype,  -- 2026-08-15 추가, military_status=completed일 때만 의미
    income_bracket INTEGER NOT NULL,
    has_disability BOOLEAN NOT NULL,
    is_foreigner BOOLEAN NOT NULL,
    enrollment_status enrollmentstatus NOT NULL,
    grade INTEGER,
    degree_level degreelevel,
    -- 2026-08-12 추가 — NULL이면 매칭 시 general로 간주(admission_track_matches() 참고).
    admission_track admissiontrack,
    -- 2026-08-03 추가 (matching_gaps.md 9·10·12번, 전부 선택 입력)
    language_test_type languagetesttype,
    language_test_score FLOAT,
    disability_type disabilitytype,
    special_status TEXT[] NOT NULL DEFAULT '{}',  -- 다중 선택이라 ARRAY(Enum) 대신 TEXT[]로 저장
    PRIMARY KEY (id)
);
CREATE UNIQUE INDEX ix_savedspec_user_id ON savedspec (user_id);
ALTER TABLE savedspec ENABLE ROW LEVEL SECURITY;
