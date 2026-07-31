# UniSco

Unisco — 대전 지역 대학생을 위한 맞춤형 장학금·지원금 매칭 서비스.

배경, 스코프, 왜 이렇게 결정했는지는 [PROJECT_BRIEF.md](./PROJECT_BRIEF.md) 참고.

## 배포 주소 (2026-07-31 기준)

- **서비스(프론트)**: https://unisco-pi.vercel.app — Vercel, `main` 브랜치 푸시할 때마다 자동 재배포
- **API(백엔드)**: https://unisco-production.up.railway.app — Railway, `main` 브랜치 푸시할 때마다 자동 재배포
- **DB**: Supabase 프로젝트 `unisco` (Studio 접근은 `supabase/README.md` 참고)

배포 설정(환경변수, Root Directory 등)은 Railway/Vercel 대시보드에만 있고 git엔 안 잡힘 — 새로 참여하는 사람은 각 서비스 대시보드에서 직접 확인해야 함.

## 스택

- **백엔드**: FastAPI (Python 3.13) + SQLModel
- **프론트엔드**: Next.js (App Router) + React + TypeScript + Tailwind CSS
- **데이터베이스**: PostgreSQL (Supabase — 호스팅형, 비개발자용 데이터 입력을 위한 스프레드시트 같은 Studio UI 포함)

## 프로젝트 구조

세 부분으로 나뉩니다. 각 폴더에 코드 설명과 셋업 방법이 담긴 README가 따로 있고, 이 파일은 전체 방향만 잡아줍니다.

```
UniSco/
├── backend/    # FastAPI 앱 — 매칭 로직, DB 통신. backend/README.md 참고
├── frontend/   # Next.js 앱 — 스펙 입력 폼 + 결과 UI. frontend/README.md 참고
└── supabase/   # 호스팅형 Postgres DB + Studio (친구용 데이터 입력 화면). supabase/README.md 참고
```

- [backend/README.md](./backend/README.md) — FastAPI 코드 구조, 로컬 셋업, 린트
- [frontend/README.md](./frontend/README.md) — Next.js/React 코드 구조, 로컬 셋업
- [supabase/README.md](./supabase/README.md) — 호스팅 DB가 뭔지, 친구가 Studio로 데이터 입력하는 방법

## 빠른 시작

```bash
# 백엔드
cd backend && source venv/bin/activate && uvicorn app.main:app --reload   # http://localhost:8000

# 프론트엔드 (별도 터미널)
cd frontend && npm run dev                                                # http://localhost:3000
```

최초 셋업(venv 생성, `pip install`, `.env` 파일 등)은 각 폴더 README에 있습니다.

## 진행 상황 (2026-07-31 기준)

1. ~~**Supabase 프로젝트 생성**~~ — 완료. `supabase/README.md` 참고.
2. ~~**데이터 모델 정의**~~ — 완료. `Scholarship`(자격조건 필드 + `category_l1`/`category_l2` 분류), `UserSpec`/`SavedSpec`, `User`, 관련 enum 전부 `backend/app/models/`에 있음.
3. **장학금 데이터 입력** — 진행 중. 친구가 Supabase Studio로 수동 입력 중(현재 133건). 최근 추가된 정밀 매칭 필드(`eligible_university`, `eligible_college`, `category_l1`/`l2` 등)는 새 항목부터 채워지는 중이고, 기존 항목 백필은 안 함.
4. ~~**매칭 엔드포인트**~~ — 완료. `POST /match`, `GET /scholarships`, `GET /scholarships/recommendations`(로그인 유저용) (`backend/app/api/`). 규칙 기반, ML 없음.
5. ~~**프론트엔드 스펙 입력 폼 + 결과 리스트**~~ — 완료. 로그인 → 2단계 스펙 위저드 → 매칭 결과(15개씩 페이지네이션). Toss 스타일 UI로 구현됨. `frontend/README.md` 참고.
6. **마이그레이션** — 아직 안 함. 스키마가 계속 바뀌는 중이라 지금은 `SQLModel.metadata.create_all()` + 수동 `ALTER TABLE`로 운영, 안정되면 Alembic 등 도입 검토.
7. ~~**실제 로그인 연동**~~ — 완료. 회원가입(이메일 인증)/로그인/스펙 저장·수정(마이페이지)까지 프론트-백엔드 전체 연결됨.
8. **장학금 상세 페이지** — 완료. `/scholarship/[id]` — 자격조건 체크리스트, 비슷한 장학금 추천, 신청 링크.
