# supabase/

> **데이터 입력을 맡은 친구분은 이 섹션만 보시면 됩니다.** 아래 "개발자용" 부분은 안 보셔도 괜찮아요.

## 장학금 데이터 입력 방법

1. [supabase.com](https://supabase.com) 접속 → 로그인 (초대 이메일 받은 계정으로)
2. `unisco` 프로젝트 클릭해서 들어가기
3. 왼쪽 메뉴에서 **Table Editor** 클릭
4. `scholarship`이라는 표(테이블) 열기 — 엑셀/구글시트처럼 생겼습니다
5. 아래쪽 **+ Insert row** (또는 `+` 버튼) 눌러서 장학금 하나씩 새 줄로 추가

설치할 것도, 코드 짤 것도 없습니다. 그냥 웹사이트에서 표 채우듯이 입력하시면 돼요.

### 각 칸에 뭘 적어야 하나

| 칸 이름 | 뭘 적나 | 모르거나 해당 없으면 |
|---|---|---|
| `name` | 장학금 이름 | (이건 꼭 채워야 함) |
| `provider` | 주는 기관 이름 (예: 대전시, 한국장학재단) | 비워둠 |
| `description` | 장학금 설명 | 비워둠 |
| `amount` | 지원 금액 (숫자만, 예: 500000) | 비워둠 |
| `application_url` | 신청하는 페이지 링크 | 비워둠 |
| `min_age` / `max_age` | 나이 제한 (최소/최대) | 나이 제한 없으면 둘 다 비워둠 |
| `required_gender` | 성별 제한 있으면 `male` 또는 `female` | 성별 무관하면 비워둠 |
| `eligible_region` | 대상 지역 (예: 대전) | 지역 제한 없으면 비워둠 |
| `required_military_status` | 병역 조건 있으면 `completed`(군필) / `exempted`(면제) / `not_served`(미필) 중 하나 | 병역 무관하면 비워둠 |
| `max_income_bracket` | "소득분위 N 이하"의 그 N 숫자 | 소득 조건 없으면 비워둠 |
| `min_gpa` | 최소 학점 (4.5 만점 기준 숫자) | 학점 조건 없으면 비워둠 |
| `requires_disability` | 장애인만 받는 장학금이면 `true`, 아니면 비워둠 | 비워둠 |
| `foreigner_eligibility` | 외국인만 되면 `foreigner_only`, 내국인만 되면 `korean_only` | 둘 다 되면 비워둠 |

**핵심 규칙 하나만 기억하시면 됩니다: 조건이 없으면 그냥 그 칸을 비워두세요.** "제한 없음"을 뜻하는 별도 입력값 없이, 그냥 빈 칸으로 두면 시스템이 "모든 사람 해당"으로 처리합니다.

헷갈리는 항목 있으면 호성한테 물어보시면 됩니다.

---

## 개발자용

이 폴더는 애플리케이션 코드가 아니라, UniSco를 뒷받침하는 호스팅 DB를 문서화/기록하는 곳입니다.

### 여기 뭐가 있나

- 실제 데이터베이스는 [Supabase](https://supabase.com)(매니지드 PostgreSQL)가 호스팅하고 있고, 로컬에서 돌리는 게 아님.
- 스키마의 진짜 정의는 `backend/app/models/`의 Python(SQLModel) 코드. `SQLModel.metadata.create_all()`을 한 번 실행해서 실제 테이블을 만든 상태.
- `schema.sql`은 그 결과를 git으로 기록해두기 위한 스냅샷 (실행용 아님, 참고용). 스키마 바뀌면 같이 업데이트할 것. 나중에 스키마가 자주 바뀌게 되면 `supabase db diff` 등으로 정식 마이그레이션 파일 관리로 전환 고려.

### 보안 — 새 테이블 만들 때마다 확인할 것

Supabase는 `public` 스키마의 모든 테이블을 PostgREST(자동 REST API)로도 노출시킴. **RLS(Row Level Security)를 안 켜면 anon key로 아무나 테이블을 읽고 쓸 수 있음.** 우리는 PostgREST를 안 쓰고(프론트→백엔드→직접 Postgres 연결 구조) Studio/백엔드 접근엔 영향 없으니, 새 테이블 만들 때마다:

```sql
ALTER TABLE <table_name> ENABLE ROW LEVEL SECURITY;
```

정책(policy)은 따로 안 만들어도 됨 — 목적이 "PostgREST 경로 자체를 막는 것"이라 정책 없는 RLS면 충분함. (`scholarship` 테이블엔 이미 적용됨, `schema.sql` 참고.)

### 왜 로컬 Postgres 대신 Supabase인가

이유 두 가지:
1. `backend/` 앱과 비개발자용 데이터 입력 작업이 같은 하나의 호스팅 DB를 바라볼 수 있음 — "누구 노트북에 진짜 데이터가 있는지" 문제가 안 생김.
2. **Supabase Studio**가 스프레드시트 같은 웹 UI를 무료로 제공해서, 데이터를 모으는 친구가 코드나 SQL 없이 브라우저에서 바로 입력 가능.

### 백엔드를 이 DB에 연결하기

`backend/.env`의 `DATABASE_URL`이 이 Supabase 프로젝트의 Postgres connection string을 가리켜야 함 (Supabase 대시보드: Project Settings → Database → Connection string에서 확인). [backend/README.md](../backend/README.md) 참고.
