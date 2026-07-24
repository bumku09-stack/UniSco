# supabase/

이 폴더는 애플리케이션 코드가 아니라, UniSco를 뒷받침하는 호스팅 DB를 문서화(그리고 나중엔 버전관리)하는 곳입니다.

## 여기 뭐가 있나

- 실제 데이터베이스는 [Supabase](https://supabase.com)(매니지드 PostgreSQL)가 호스팅하고 있고, 로컬에서 돌리는 게 아님. 이 폴더 안에서 띄울 서버 같은 건 없음.
- 스키마가 안정화되면 SQL 마이그레이션 파일들이 여기 들어올 예정 (`supabase db diff` / `supabase migration new` 등을 통해) — 그래야 스키마 변경 이력이 대시보드 클릭질로만 남지 않고 git으로 추적됨. 지금은 스키마가 `backend/app/models/`(Python/SQLModel)에 코드로 정의돼 있고, `SQLModel.metadata.create_all()`을 한 번 실행해서 실제 테이블을 만든 상태 — 별도 마이그레이션 툴은 아직 안 씀.

## 보안 — 새 테이블 만들 때마다 확인할 것

Supabase는 `public` 스키마의 모든 테이블을 PostgREST(자동 REST API)로도 노출시킴. **RLS(Row Level Security)를 안 켜면 anon key로 아무나 테이블을 읽고 쓸 수 있음.** 우리는 PostgREST를 안 쓰고(프론트→백엔드→직접 Postgres 연결 구조) Studio/백엔드 접근엔 영향 없으니, 새 테이블 만들 때마다:

```sql
ALTER TABLE <table_name> ENABLE ROW LEVEL SECURITY;
```

정책(policy)은 따로 안 만들어도 됨 — 목적이 "PostgREST 경로 자체를 막는 것"이라 정책 없는 RLS면 충분함. (`scholarship` 테이블엔 이미 적용됨.)

## 왜 로컬 Postgres 대신 Supabase인가

이유 두 가지:
1. `backend/` 앱과 비개발자용 데이터 입력 작업이 같은 하나의 호스팅 DB를 바라볼 수 있음 — "누구 노트북에 진짜 데이터가 있는지" 문제가 안 생김.
2. **Supabase Studio** — 테이블 행을 편집할 수 있는 스프레드시트 같은 웹 UI — 를 무료로 제공하기 때문에, 장학금 데이터를 모으는 친구가 코드나 SQL 없이 브라우저에서 바로 행을 추가/수정할 수 있음.

## 데이터 입력을 맡은 친구에게 (비개발자용)

1. Supabase 프로젝트에 초대받기 (호성한테 Supabase 대시보드 → Project Settings → Team에서 초대해달라고 요청).
2. [supabase.com](https://supabase.com)에서 로그인 → `unisco` 프로젝트 열기.
3. 왼쪽 사이드바 → **Table Editor**. 스프레드시트처럼 생겼고 그렇게 쓰면 됨 — 행 하나가 장학금/지원금 레코드 하나.
4. `scholarship` 테이블 열어서 바로 행 추가/수정하면 됨. 설치도, 코드도 필요 없음.

**컬럼 설명:**

| 컬럼 | 의미 | 비워두면 |
|---|---|---|
| `name` | 장학금 이름 | (필수) |
| `provider` | 주관 기관 | - |
| `description` | 설명 | - |
| `amount` | 금액 | - |
| `application_url` | 신청 링크 | - |
| `min_age` / `max_age` | 나이 제한 | 제한 없음 |
| `required_gender` | 성별 제한 (`male`/`female`) | 무관 |
| `eligible_region` | 대상 지역 | 제한 없음 |
| `required_military_status` | 병역 (`completed`=군필/`exempted`=면제/`not_served`=미필) | 무관 |
| `max_income_bracket` | 소득분위 N 이하 | 제한 없음 |
| `min_gpa` | 최소 학점 (4.5 만점) | 제한 없음 |
| `requires_disability` | 장애인 한정 여부 (true/false) | 무관 |
| `foreigner_eligibility` | 국적 제한 (`korean_only`/`foreigner_only`) | 무관 |

**즉, 조건이 없는 항목은 그냥 비워두면 됩니다** (예: 나이 제한 없는 장학금이면 `min_age`/`max_age` 둘 다 비워둠).

## 백엔드를 이 DB에 연결하기

`backend/.env`의 `DATABASE_URL`이 이 Supabase 프로젝트의 Postgres connection string을 가리켜야 함 (Supabase 대시보드: Project Settings → Database → Connection string에서 확인). [backend/README.md](../backend/README.md) 참고.
