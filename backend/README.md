# backend/

FastAPI 앱. 규칙 기반 매칭 로직을 처리하고 Supabase Postgres DB와 통신함.

## 코드 구조

```
app/
├── main.py             # 엔트리포인트 — FastAPI 앱 생성, 라우터 등록, CORS 설정
├── core/
│   └── config.py       # 타입 있는 설정값 (Settings 클래스), pydantic-settings로 .env에서 로드
├── db/
│   └── session.py      # SQLAlchemy/SQLModel 엔진 + DB 접근용 get_session() 디펜던시
├── api/
│   ├── health.py        # GET /health, {"status": "ok"} 반환
│   ├── scholarships.py  # GET /scholarships — 전체 장학금 목록 반환
│   └── match.py          # POST /match — 유저 스펙 받아서 자격조건으로 필터링한 장학금 목록 반환
└── models/
    ├── enums.py         # Gender, MilitaryStatus, EnrollmentStatus, CategoryL1/L2 등 자격조건·분류 enum
    ├── scholarship.py    # Scholarship 테이블 정의 (자격조건 필드 + category_l1/l2 분류 필드)
    └── user_spec.py      # UserSpec — /match 요청 바디 (DB 테이블 아님)
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

`api/match.py`의 `POST /match`. 프론트가 보낸 `UserSpec`(대학, 단과대, 학점, 나이, 성별, 지역, 병역, 소득분위, 장애/외국인 여부, 재학상태, 학년/과정구분)을 받아서 `Scholarship` 테이블 전체를 순회하며 `_is_eligible()`로 필터링 후 통과한 것만 반환함. 규칙 기반, ML 없음(v1 스코프대로).

`category_l1`/`category_l2`(장학금 분류)는 매칭 필터링에는 안 쓰임 — "누가 받을 수 있는지"가 아니라 "어떤 종류인지"라서 프론트 목록 화면 표시/그룹핑 전용. 자세한 값 목록은 [supabase/README.md](../supabase/README.md) 참고.

## 배포 (Railway)

Railway 대시보드에서 이 저장소를 연결하고, 서비스 설정의 **Root Directory**를 `backend`로 지정하면 됨. `Procfile`(`web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`)과 `.python-version`(`3.13`)을 이미 넣어놨기 때문에 Railway가 Nixpacks로 자동 인식함 — 빌드/시작 명령을 따로 안 적어줘도 됨.

Railway 프로젝트 환경변수(Variables 탭)에 등록해야 하는 값:

- `DATABASE_URL` — 로컬 `.env`에 있는 Supabase 커넥션 문자열과 동일 (Session pooler 버전)
- `CORS_ORIGINS` — 배포된 프론트 URL을 JSON 배열로. 예: `["https://unisco.vercel.app"]`
- `ENVIRONMENT` — `production`

배포되면 Railway가 `https://<프로젝트명>.up.railway.app` 같은 URL을 발급함 — 이걸 프론트의 `NEXT_PUBLIC_API_URL`로 등록하면 됨.

## 남은 것 (2026-07-30 기준)

- 기존에 입력된 장학금 데이터 중 `eligible_university`/`eligible_college`/`category_l1`/`category_l2` 등 새로 추가된 정밀 매칭·분류 필드가 비어있는 항목이 있음 — Supabase Studio에서 계속 채워지는 중.
- 스키마가 계속 바뀌고 있어서 마이그레이션 툴(Alembic 등)은 아직 도입 안 함 — 지금은 `SQLModel.metadata.create_all()` + 수동 `ALTER TABLE`로 운영.
