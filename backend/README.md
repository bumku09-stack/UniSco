# backend/

FastAPI 앱. 규칙 기반 매칭 로직을 처리하고 Supabase Postgres DB와 통신함.

## 코드 구조

```
app/
├── main.py             # 엔트리포인트 — FastAPI 앱 생성, 라우터 등록, CORS 설정
├── core/
│   ├── config.py        # 타입 있는 설정값 (Settings 클래스), pydantic-settings로 .env에서 로드
│   ├── security.py       # 비밀번호 해싱(bcrypt) + JWT 발급/검증
│   ├── email.py           # Resend로 인증 코드 메일 발송
│   └── matching.py         # 자격조건 필터링 + 정렬 로직 (match.py, scholarships.py 둘 다 여기서 가져다 씀)
├── db/
│   └── session.py      # SQLAlchemy/SQLModel 엔진 + DB 접근용 get_session() 디펜던시
├── api/
│   ├── health.py        # GET /health, {"status": "ok"} 반환
│   ├── scholarships.py  # GET /scholarships (전체 목록), GET /scholarships/recommendations (로그인 유저 스펙 기준 추천)
│   ├── match.py          # POST /match — 요청 바디로 받은 스펙으로 즉석 매칭 (로그인 없이도 씀, 프론트 스펙 위저드가 아직 이걸 씀)
│   ├── auth.py            # 회원가입/이메일인증/로그인/토큰재발급 (POST /auth/*)
│   ├── users.py            # 로그인 유저 스펙 저장/조회/수정 (GET·POST·PUT /users/me/spec*)
│   └── deps.py              # get_current_user — Authorization 헤더의 JWT로 User 로드하는 공용 디펜던시
└── models/
    ├── enums.py         # Gender, MilitaryStatus, EnrollmentStatus, CategoryL1/L2 등 자격조건·분류 enum
    ├── scholarship.py    # Scholarship 테이블 정의 (자격조건 필드 + category_l1/l2 분류 필드)
    ├── user_spec.py      # UserSpec — /match 요청 바디 (DB 테이블 아님), SpecStatusResponse
    ├── saved_spec.py      # SavedSpec — UserSpec의 저장형(테이블), 유저당 한 행
    ├── user.py           # User, EmailVerification 테이블 정의
    └── auth.py            # SignupRequest 등 /auth 요청·응답 바디 (DB 테이블 아님)
```

### 어떻게 맞물려 돌아가는지

- `main.py`가 `uvicorn`이 실행하는 대상임. `FastAPI()` 앱 객체를 만들고, `api/`의 각 라우트 모듈마다 `app.include_router(...)`를 호출함. 새 기능 추가 = `api/`에 파일 하나 추가하고 `main.py`에 한 줄 등록.
- `core/config.py`의 `Settings` 클래스는 환경변수(`.env`에서, `.env.example` 참고)를 타입 있는 객체로 읽어들임. 설정값 필요할 땐 `os.environ` 직접 호출하지 말고 어디서든 `settings`를 import해서 쓰면 됨.
- `db/session.py`는 `settings.database_url`로부터 SQLAlchemy `engine`을 만들고, `get_session()`을 제공함 — FastAPI 디펜던시로 쓰도록 만든 제너레이터(`Session = Depends(get_session)`)라서 요청마다 각자의 DB 세션을 받고 자동으로 닫힘.
- `models/`의 SQLModel 클래스는 DB 테이블 정의와 Pydantic 요청/응답 스키마 역할을 동시에 하기 때문에, ORM 모델과 API 스키마를 따로 안 짜도 됨. `Scholarship`의 자격조건 필드는 값이 `None`이면 "그 조건 제한 없음"으로 취급함(예: `min_gpa=None`이면 학점 무관).

## 로컬 셋업

```bash
python3.13 -m venv venv        # venv/가 없으면 먼저 생성
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env           # 이후 실제 Supabase connection string으로 DATABASE_URL 채우기
uvicorn app.main:app --reload  # http://localhost:8000
```

살아있는지 확인: `curl http://localhost:8000/health` → `{"status": "ok"}`
FastAPI가 자동 생성해주는 API 문서: http://localhost:8000/docs

린트: `ruff check .` (이 디렉토리에서, venv 활성화한 채로)

## 실제 매칭 로직은 어디에

`core/matching.py`의 `is_eligible()`(자격조건 필터링) + `specificity_score()`(통과한 것들 중 더 구체적으로 타겟된 것을 우선 정렬). 규칙 기반, ML 없음(v1 스코프대로). 이 로직을 쓰는 진입점이 두 개 있음:

- `POST /match` (`api/match.py`) — 요청 바디로 받은 `UserSpec`을 그 자리에서 매칭. 로그인 없이도 되고, 지금 프론트 스펙 위저드가 쓰는 방식.
- `GET /scholarships/recommendations` (`api/scholarships.py`) — 로그인(JWT) 필요. 요청 바디 없이, DB에 저장된 그 유저의 `SavedSpec`을 불러와서 매칭. 2026-07-31 추가.

두 진입점 다 결과적으로 같은 `is_eligible`/`specificity_score`를 타므로 동작이 갈릴 일이 없음 — `POST /match`용으로 짠 로직을 다시 구현한 게 아니라 `core/matching.py`로 뽑아내서 그대로 재사용한 것.

`category_l1`/`category_l2`(장학금 분류)는 매칭 필터링에는 안 쓰임 — "누가 받을 수 있는지"가 아니라 "어떤 종류인지"라서 프론트 목록 화면 표시/그룹핑 전용. 자세한 값 목록은 [supabase/README.md](../supabase/README.md) 참고.

## 로그인 유저의 스펙 저장은 어디에

`api/users.py`의 `/users/me/spec*` 4개 엔드포인트 (전부 JWT 필요, `api/deps.py`의 `get_current_user`로 보호됨 — 요청에 실린 토큰의 유저 것만 접근 가능하고 다른 유저 것은 애초에 조회할 방법이 없음):

- `GET /users/me/spec-status` — `{"spec_completed": bool}`. **별도 플래그 컬럼을 안 두고** `SavedSpec`에 그 유저 행이 있는지로 판단함 — 플래그랑 실제 데이터가 따로 놀 걱정이 없음.
- `POST /users/me/spec` — 최초 저장. 이미 있으면 409(수정은 PUT으로 하라고 안내).
- `GET /users/me/spec` — 조회. 없으면 404.
- `PUT /users/me/spec` — 수정. 없으면 404(먼저 POST로 만들라고 안내).

**주의**: 이 저장소를 처음 받았을 당시 `User`/`Scholarship`에 스펙 관련 필드가 이미 있다고 알고 있었다면 그건 사실이 아니었음 — `UserSpec`(`models/user_spec.py`)은 처음부터 "저장 안 하는 `/match` 요청 바디"였고(주석에도 "로그인 생기면 실제 테이블로 옮길 것"이라고 적혀있었음), `User` 테이블엔 스펙 필드가 전혀 없었음. 그래서 새 테이블 `SavedSpec`을 추가했음 — `User` 테이블 자체는 안 건드림.

**매칭 재계산 캐싱은 안 함(제안)**: 스펙 수정 후 `/scholarships/recommendations`를 다시 부르면 매번 전체 `Scholarship` 테이블(현재 133건)을 다시 읽어서 필터링함. 지금 규모에선 이게 SQL 쿼리 한 번 + O(n) 필터링이라 밀리초 단위라 캐싱 안 함(캐시 무효화 로직이 버그 리스크 대비 얻는 게 적음). 장학금 건수가 수천 단위로 늘고 동시 사용자가 많아지면, 그때 "스펙 해시 → 결과" 캐시(스펙 수정 시 무효화)를 고려하면 됨 — 지금 붙이는 건 이르다고 판단.

## 회원가입/로그인은 어디에

`api/auth.py`, `core/security.py`(비밀번호 해싱 + JWT), `core/email.py`(인증 코드 이메일 발송) — 전부 2026-07-31에 추가됨.

- **비밀번호**: `bcrypt` 패키지로 직접 해싱함. 원래 `passlib[bcrypt]`로 시작했는데 passlib이 2020년 이후 유지보수가 끊겨서 최신 `bcrypt` 5.x랑 호환이 안 되는 문제(`AttributeError: module 'bcrypt' has no attribute '__about__'`)가 있어 — passlib 없이 `bcrypt.hashpw`/`bcrypt.checkpw`를 직접 씀.
- **JWT**: `pyjwt`. access token(`ACCESS_TOKEN_EXPIRE_MINUTES`, 기본 30분)은 매 요청에 실어 보내는 용도, refresh token(`REFRESH_TOKEN_EXPIRE_DAYS`, 기본 30일)은 `POST /auth/refresh`로 새 토큰 발급받을 때만 씀. 둘 다 페이로드에 `type`(`access`/`refresh`)을 넣어서 access token으로 refresh를 시도하는 걸 막음. 리프레시 토큰 회전/블랙리스트(탈취 시 무효화)는 아직 없음 — 필요해지면 추가.
- **이메일 인증 코드**: 6자리 숫자, 5분 유효, 계정당 시도 5회 실패하면 그 코드는 잠기고 재발송 필요(`POST /auth/resend-code`). `identifier`(username 또는 email) 아무거나로 조회 가능.
- **로그인 실패 메시지 통일**: 아이디가 없거나 비밀번호가 틀리거나 항상 "아이디 또는 비밀번호가 일치하지 않습니다"만 반환 — 아이디 존재 여부가 새지 않게. 단, "이메일 인증 안 됨"은 이미 로그인 자체는 맞게 한 사용자에게 알려줘야 하는 정보라 별도 403으로 분리함.

### 이메일 발송: Resend를 쓰는 이유

1. **Railway가 Hobby/Free 플랜에서 아웃바운드 SMTP(465/587 포트)를 막아둠** — Gmail SMTP 같은 전통적인 방식은 Railway에 배포하면 그냥 안 됨. Resend는 SMTP가 아니라 HTTPS API로 메일을 보내기 때문에 이 제한 자체가 적용 안 됨.
2. 무료 티어가 월 3,000통/일 100통(도메인 1개) — 지금 규모(대전 지역 대학생 대상 MVP)엔 충분함.
3. Python SDK 있고 API가 단순함(`core/email.py`의 `send_verification_code` 참고).

`RESEND_API_KEY`는 [resend.com](https://resend.com) 가입 후 발급 — 처음엔 그들이 주는 `onboarding@resend.dev` 발신 주소로 테스트 가능하고(수신자가 가입한 계정 이메일일 때만 동작), 실제 서비스로 쓰려면 본인 도메인을 Resend에 등록/인증(DNS에 DKIM 레코드 추가)해야 그 도메인 주소로 아무 수신자에게나 보낼 수 있음.

## 배포 (Railway)

Railway 대시보드에서 이 저장소를 연결하고, 서비스 설정의 **Root Directory**를 `backend`로 지정하면 됨. `Procfile`(`web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`)과 `.python-version`(`3.13`)을 이미 넣어놨기 때문에 Railway가 Nixpacks로 자동 인식함 — 빌드/시작 명령을 따로 안 적어줘도 됨.

Railway 프로젝트 환경변수(Variables 탭)에 등록해야 하는 값:

- `DATABASE_URL` — 로컬 `.env`에 있는 Supabase 커넥션 문자열과 동일 (Session pooler 버전)
- `CORS_ORIGINS` — 배포된 프론트 URL을 JSON 배열로. 예: `["https://unisco.vercel.app"]`
- `ENVIRONMENT` — `production`
- `SECRET_KEY` — `openssl rand -hex 32`로 생성한 랜덤 문자열 (JWT 서명용, 로컬 개발용 기본값을 그대로 배포에 쓰면 안 됨)
- `RESEND_API_KEY`, `EMAIL_FROM` — 회원가입 인증 메일 발송용 (`.env.example` 참고)

배포되면 Railway가 `https://<프로젝트명>.up.railway.app` 같은 URL을 발급함 — 이걸 프론트의 `NEXT_PUBLIC_API_URL`로 등록하면 됨.

## 남은 것 (2026-07-31 기준)

- 기존에 입력된 장학금 데이터 중 `eligible_university`/`eligible_college`/`category_l1`/`category_l2` 등 새로 추가된 정밀 매칭·분류 필드가 비어있는 항목이 있음 — Supabase Studio에서 계속 채워지는 중.
- 스키마가 계속 바뀌고 있어서 마이그레이션 툴(Alembic 등)은 아직 도입 안 함 — 지금은 `SQLModel.metadata.create_all()` + 수동 `ALTER TABLE`로 운영.
- 회원가입/로그인/스펙저장 API(`/auth/*`, `/users/me/spec*`, `/scholarships/recommendations`)는 프론트까지 연결 완료(2026-07-31) — `/` → `/signup` → `/spec`(최초 1회) → `/home` → `/mypage` 플로우 전체 구현됨. 자세한 건 `frontend/README.md` 참고. `POST /match`(로그인 없이 즉석 매칭)는 그대로 남아있지만 지금 프론트는 안 씀 — 나중에 "로그인 없이 미리 둘러보기" 같은 용도로 재활용하거나, 안 쓰면 정리 대상.
- 리프레시 토큰 회전/탈취 대응(블랙리스트 등) 없음 — access token이 30분마다 만료되는 것으로만 방어 중. 트래픽 늘면 재검토.
- Railway `RESEND_API_KEY`를 아직 실제 값으로 안 채워넣었으면 회원가입 시 이메일 발송이 502로 실패함 — 배포 전에 `resend.com`에서 키 발급하고 Variables에 등록 필요.
