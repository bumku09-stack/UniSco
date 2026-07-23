# backend/

FastAPI 앱. 매칭 로직(작성 예정)을 처리하고 Supabase Postgres DB와 통신함.

## 코드 구조

```
app/
├── main.py         # 엔트리포인트 — FastAPI 앱 생성, 라우터 등록, CORS 설정
├── core/
│   └── config.py   # 타입 있는 설정값 (Settings 클래스), pydantic-settings로 .env에서 로드
├── db/
│   └── session.py  # SQLAlchemy/SQLModel 엔진 + DB 접근용 get_session() 디펜던시
├── api/
│   └── health.py   # 예시 라우트 모듈 — GET /health, {"status": "ok"} 반환
└── models/         # 아직 비어있음 — SQLModel 테이블 클래스(Scholarship 등)가 여기 들어감
```

### 어떻게 맞물려 돌아가는지

- `main.py`가 `uvicorn`이 실행하는 대상임. `FastAPI()` 앱 객체를 만들고, `api/`의 각 라우트 모듈마다 `app.include_router(...)`를 호출함. 새 기능 추가 = `api/`에 파일 하나 추가하고 `main.py`에 한 줄 등록.
- `core/config.py`의 `Settings` 클래스는 환경변수(`.env`에서, `.env.example` 참고)를 타입 있는 객체로 읽어들임. 설정값 필요할 땐 `os.environ` 직접 호출하지 말고 어디서든 `settings`를 import해서 쓰면 됨.
- `db/session.py`는 `settings.database_url`로부터 SQLAlchemy `engine`을 만들고, `get_session()`을 제공함 — FastAPI 디펜던시로 쓰도록 만든 제너레이터(`Session = Depends(get_session)`)라서 요청마다 각자의 DB 세션을 받고 자동으로 닫힘.
- `models/`엔 앞으로 SQLModel 클래스들이 들어감 — SQLModel 클래스는 DB 테이블 정의와 Pydantic 요청/응답 스키마 역할을 동시에 하기 때문에, ORM 모델과 API 스키마를 따로 안 짜도 됨.

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

아직 안 짰음. 브리프 기준으로는 규칙 기반 필터링이 될 예정: 유저 스펙(학년, 전공, 소득분위, 지역 등)을 입력받아서 `models/`의 장학금 테이블을 자격조건으로 필터링하고 매칭 결과를 반환. v1은 ML 없음 — 현재 계획은 루트 [README.md](../README.md)의 "다음 단계" 참고.
