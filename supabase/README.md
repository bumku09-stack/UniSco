# supabase/

이 폴더는 애플리케이션 코드가 아니라, UniSco를 뒷받침하는 호스팅 DB를 문서화(그리고 나중엔 버전관리)하는 곳입니다.

## 여기 뭐가 있나

- **지금은 사실상 아무것도 없음.** 실제 데이터베이스는 [Supabase](https://supabase.com)(매니지드 PostgreSQL)가 호스팅하고 있고, 로컬에서 돌리는 게 아님. 이 폴더 안에서 띄울 서버 같은 건 없음.
- 스키마가 안정화되면 SQL 마이그레이션 파일들이 여기 들어올 예정 (`supabase db diff` / `supabase migration new` 등을 통해) — 그래야 스키마 변경 이력이 대시보드 클릭질로만 남지 않고 git으로 추적됨.

## 왜 로컬 Postgres 대신 Supabase인가

이유 두 가지:
1. `backend/` 앱과 비개발자용 데이터 입력 작업이 같은 하나의 호스팅 DB를 바라볼 수 있음 — "누구 노트북에 진짜 데이터가 있는지" 문제가 안 생김.
2. **Supabase Studio** — 테이블 행을 편집할 수 있는 스프레드시트 같은 웹 UI — 를 무료로 제공하기 때문에, 장학금 데이터를 모으는 친구가 코드나 SQL 없이 브라우저에서 바로 행을 추가/수정할 수 있음.

## 데이터 입력을 맡은 친구에게 (비개발자용)

1. Supabase 프로젝트에 초대받기 (호성한테 Supabase 대시보드 → Project Settings → Team에서 초대해달라고 요청).
2. [supabase.com](https://supabase.com)에서 로그인 → `unisco` 프로젝트 열기.
3. 왼쪽 사이드바 → **Table Editor**. 스프레드시트처럼 생겼고 그렇게 쓰면 됨 — 행 하나가 장학금/지원금 레코드 하나.
4. 여기서 바로 행을 추가/수정하면 됨. 설치도, 코드도 필요 없음.

(아직 테이블 구조가 없어서 — `backend/app/models/`에서 스키마가 정의되면 "각 컬럼이 뭘 의미하는지" 구체적인 안내가 이 섹션에 추가될 예정. 현재 진행 상황은 루트 [README.md](../README.md) "다음 단계" 참고.)

## 백엔드를 이 DB에 연결하기

`backend/.env`의 `DATABASE_URL`이 이 Supabase 프로젝트의 Postgres connection string을 가리켜야 함 (Supabase 대시보드: Project Settings → Database → Connection string에서 확인). [backend/README.md](../backend/README.md) 참고.
