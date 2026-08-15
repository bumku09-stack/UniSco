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
| `eligible_region` | 대상 지역 — **짧은 태그로** (예: `대전`, `대전·충남·충북·세종`) | 지역 제한 없으면 비워둠 |
| `required_military_status` | 병역 조건 있으면 `completed`(군필) / `exempted`(면제) / `not_served`(미필) / `rotc_candidate`(학군사관후보생·ROTC, 2026-08-15 추가) 중 하나 | 병역 무관하면 비워둠 |
| `required_discharge_type` ⭐매칭에 실제로 쓰임 (2026-08-15 추가) | `required_military_status=completed`(군필)일 때만 의미 있는 세부 구분 — 병사로 전역이면 `enlisted`, 장교·부사관으로 전역이면 `officer_or_nco` | 군필이 아니거나 세부구분 무관하면 비워둠 |
| `max_income_bracket` | "소득분위 N 이하"의 그 N 숫자 | 소득 조건 없으면 비워둠 |
| `min_gpa` | 최소 학점 (4.5 만점 기준 숫자) | 학점 조건 없으면 비워둠 |
| `min_gpa_basis` | 위 `min_gpa`가 **직전학기** 성적 기준이면 `semester`, **전체 재학기간 누적(CGPA)** 기준이면 `cumulative` (2026-08-02 추가 — 같은 대학 안에서도 장학금마다 둘 중 하나를 요구하는 경우가 섞여 있어서 나눔) | 어느 쪽인지 설명에 안 나와 있거나 모르겠으면 비워둠(비워두면 둘 중 하나만 맞아도 통과되는 안전한 기본값으로 처리됨) |
| `requires_disability` | 장애인만 받는 장학금이면 `true`, 아니면 비워둠 | 비워둠 |
| `foreigner_eligibility` | 외국인만 되면 `foreigner_only`, 내국인만 되면 `korean_only` | 둘 다 되면 비워둠 |
| `major` ⭐매칭에 실제로 쓰임 | 전공 조건 — **실제 학과명으로, 여러 개면 콤마로** (예: `스포츠과학과,체육교육과`) | 전공 무관하면 비워둠. **비워두면 전교생에게 노출되니, 원문에 "OO학과 대상"/"OO특기자 전형 입학생 대상" 같은 조건이 있으면 반드시 채울 것**(2026-08-12 체육특기자 장학금이 전교생에게 노출된 사고 원인) |
| `excluded_major` ⭐매칭에 실제로 쓰임 | "이 학과만 빼고 나머지 전부 됨" 유형일 때만 사용 (예: `한의예과,군사학과`) — `major`와 정반대 방향, 둘을 같이 채우면 안 됨 | 해당 없으면 비워둠 |
| `admission_track` ⭐매칭에 실제로 쓰임 (2026-08-12 추가) | 입학전형 — `major`(전공)와 별개 축. "OO학과 대상"이 아니라 **"OO전형 입학생 대상"**이라고 적혀 있으면 여기 채울 것. `general`(일반전형) / `athletic_specialty`(체육특기자 전형) / `other_specialty`(기타 특기자·특별전형) | 전형 무관하면 비워둠. **`major`에 우회해서 넣지 말 것** — 2026-08-12 체육특기자 장학금 사고가 정확히 이 실수 때문이었음 |
| `grade_level` (참고용, 매칭 안 쓰임) | 학년 조건 원문 (예: "학부 3~8학기차") — `min_grade`/`max_grade`가 실제 필터링 담당, 이 칸은 표시도 안 됨(레거시) | 안 채워도 무방 |
| `affiliated_institution` (참고용, 매칭 안 쓰임) | 소속 대학/학과 조건 원문 | 안 채워도 무방 |
| `min_credits` (참고용, 매칭 안 쓰임) | 이수학점 조건 원문 — 상세페이지에 원문 그대로 표시만 됨 | 텍스트로 자유롭게, 없으면 비워둠 |
| `min_credits_last_semester` ⭐매칭에 실제로 쓰임 (2026-08-12 추가) | 이수학점 조건 — **"직전학기 N학점 이상" 형태로 안전하게 환산되는 경우만** 숫자로 (예: `12`). GPA와 동일한 방식으로 학생이 직접 입력한 값과 비교됨 | 특정 전공 교과목 학점처럼 다른 개념이거나 조건이 복잡하면 비워두고 `min_credits`(원문)만 채울 것 |
| `admission_score_condition` (참고용, 매칭 안 쓰임) | 입시(수능/내신) 성적 조건 — 상세페이지에 원문 그대로 표시만 됨 | 텍스트로 자유롭게, 없으면 비워둠 |
| `headcount` (참고용, 매칭 안 쓰임) | 선발 인원 — 상세페이지에 원문 그대로 표시만 됨 | 텍스트로 자유롭게, 없으면 비워둠 |
| `application_period` (참고용, 매칭 안 쓰임) | 신청 기간 원문 | 텍스트로 자유롭게, 없으면 비워둠 |
| `application_method` (참고용, 매칭 안 쓰임 — 단, 프론트 안내 문구 판정엔 쓰임) | 신청 방식 원문 (예: "자동선발, 별도 신청 없음", "홈페이지에서 직접 신청") — 상세페이지 "신청방식" 블록에 그대로 표시되고, "자동선발" 계열 문구면 신청 버튼 위에 안내 문구도 뜸(`frontend/src/lib/scholarship.ts`의 `isAutoSelected`) | 텍스트로 자유롭게, 없으면 비워둠. **반드시 원문에서 확인된 값만 넣을 것** — 2026-08-15, 형제 레코드끼리 패턴이 비슷해 보인다고 값을 추측해서 넣었다가 실제로는 출처에 없던 사고가 있었음(`harness/reverify.py`로 재검증해서 수정) |
| `application_deadline` ⭐매칭에 실제로 쓰임 | 확정 마감일 (날짜, 예: `2026-08-14`) — `application_period` 원문에 날짜가 있으면 여기도 같이 채울 것 | **비워두면 마감이 지나도 계속 노출됨**(2026-08-12 "마감 지난 장학금이 계속 뜬다" UX 리서치 1위 불만의 원인) — 원문에 확정 날짜가 없으면(매년 반복 공고 등) 그냥 비워두는 게 맞음, 추측해서 채우지 말 것 |
| `eligible_university` ⭐매칭에 실제로 쓰임 | 대상 대학 — **짧은 태그로** (예: `충남대학교`, `KAIST`) | 대학 무관하면 비워둠 |
| `eligible_college` ⭐매칭에 실제로 쓰임 | 대상 단과대 (예: `공과대학`) — 대학 이름 정확히 일치해야 매칭되니 `eligible_university`도 같이 채워야 의미 있음 | 단과대 무관하면 비워둠 |
| `required_enrollment_status` ⭐매칭에 실제로 쓰임 | 재학 상태 — `undergrad_enrolled`(학부재학) / `undergrad_transfer`(학부편입) / `undergrad_leave`(학부휴학) / `post_undergrad`(대학원 등) | 무관하면 비워둠 |
| `min_grade` / `max_grade` ⭐매칭에 실제로 쓰임 | 학부 학년 범위 (숫자, 예: 2학년 이상이면 min_grade=2) — `required_enrollment_status`가 학부 관련일 때만 의미 있음. **"신입생 전용" 장학금은 `min_grade=1, max_grade=1`로 입력** — 편입생은 1학년으로 들어오는 경우가 거의 없어서 이렇게만 해도 편입생이 자동으로 걸러짐 | 학년 제한 없으면 비워둠 |
| `required_degree_level` ⭐매칭에 실제로 쓰임 | 대학원 과정 구분 — `masters`(석사) / `doctoral`(박사) / `integrated_ms_phd`(석박사통합). `required_enrollment_status`가 `post_undergrad`일 때만 의미 있음 | 무관하면 비워둠 |
| `required_disability_type` ⭐매칭에 실제로 쓰임 | 장애 세부 유형 — `physical_impairment`/`learning_disability`/`medical_disability`/`mental_impairment`/`muscular_dystrophy`/`developmental_impairment`/`disabled_parent`(부모가 장애인, 본인 아님) 중 하나. `requires_disability`랑 별개 칸이라 자주 빠뜨림 | 세부 유형 무관하면 비워둠(`requires_disability=true`만으로 충분) |
| `language_test_type` / `language_test_min_score` ⭐매칭에 실제로 쓰임 | 어학 성적 조건 — 타입은 `TOEIC`/`TOEFL`/`IELTS`/`TOPIK`/`기타`, 점수는 숫자만 (예: `TOEIC`, `900`) | 어학 조건 없으면 둘 다 비워둠 |
| `required_special_status` ⭐매칭에 실제로 쓰임 | 특수상황 조건(여러 개 가능, OR — 이 중 하나라도 해당하면 통과) — 태그 전체 목록은 `data_collection_guide.md`의 "특수상황 태그 전체 목록" 참고 (예: `north_korean_defector`, `single_parent_family`) | 특수상황 조건 없으면 비워둠 |
| `required_special_status_all` ⭐매칭에 실제로 쓰임 | 특수상황 조건(여러 개면 AND — 전부 다 해당해야 통과, 예: "다문화가정이면서 차상위") — 태그는 `required_special_status`와 동일 목록 | 해당 없으면 비워둠 |
| `excluded_special_status` ⭐매칭에 실제로 쓰임 | "이 특수상황이면 무조건 탈락" 조건 — 태그는 위와 동일 목록 | 해당 없으면 비워둠 |
| `category_l1` | 대분류 — `school_internal`(교내장학금) / `school_external`(교외장학금) / `support_fund`(지원금) | 분류 안 정했으면 비워둠 |
| `category_l2` | 중분류 — 아래 표에서 `category_l1`에 맞는 값 골라서 입력 | 분류 안 정했으면 비워둠 |

**`category_l1`별로 고를 수 있는 `category_l2` 값:**

| category_l1 | 고를 수 있는 category_l2 값 |
|---|---|
| `school_internal` (교내장학금) | `academic_merit`(성적) / `welfare_living`(복지생활지원) / `special_target`(특수대상) / `activity_merit`(활동공로) / `research`(연구) / `international_exchange`(국제교류) / `department_alumni`(학과동문회자체) |
| `school_external` (교외장학금) | `national_scholarship`(국가장학금) / `local_gov`(지자체) / `private_foundation`(민간재단기업) / `association`(협회학회) |
| `support_fund` (지원금) | `youth_living_support`(청년생활지원) / `activity_participation_support`(활동참여지원) |

**핵심 규칙 하나만 기억하시면 됩니다: 조건이 없으면 그냥 그 칸을 비워두세요.** "제한 없음"을 뜻하는 별도 입력값 없이, 그냥 빈 칸으로 두면 시스템이 "모든 사람 해당"으로 처리합니다.

**규칙 하나 더(2026-08-15 추가): 비슷한 장학금이 이미 입력돼 있어도, 그 값을 그대로 베끼지 말고 원문에서 직접 확인하세요.** "다른 장학금이랑 비슷하니까 이것도 똑같겠지"라고 넘겨짚었다가 실제로는 원문에 아예 없던 내용이 들어간 사고가 있었습니다 — 특히 `application_period`/`application_method`(신청기간/신청방식)에서요. 원문에 없으면 그냥 비워두는 게 맞습니다.

**`category_l1`/`category_l2`는 다른 컬럼이랑 성격이 달라요** — "이 장학금 누가 받을 수 있는지"(자격조건)가 아니라 "이 장학금이 어떤 종류인지"(분류)라서, 매칭 필터링에는 안 쓰이고 목록 화면에 표시/그룹핑하는 용도입니다. 애매한 경우(예: 연구메이트 지원사업처럼 연구지도가 아니라 튜터링 활동비 성격이면 `activity_participation_support`) 판단 기준은 계속 상의해서 정하면 됩니다.

**⭐표시된 컬럼이 실제 매칭 필터링에 쓰이는 것들입니다.** `grade_level`/`affiliated_institution`/`min_credits`/`admission_score_condition`/`headcount`/`application_period`(참고용 표시)은 상세페이지에 원문 그대로 표시되거나(일부는 표시조차 안 됨) 아직 매칭 로직이 안 읽습니다. **`major`는 2026-08-03부터 매칭에 실제로 쓰입니다** — 예전엔 참고용이었지만 지금은 아니니 반드시 채울 것. (이 문서가 실제 매칭 로직과 어긋난 적이 있었음 — 헷갈리면 이 표보다 `backend/app/core/matching.py`의 `is_eligible()`이 최종 기준입니다.)

**`required_enrollment_status`에 `undergrad_enrolled`(학부재학)만 넣어도 편입생은 자동으로 포함됩니다** — "재학생 대상"이라고만 되어있는 장학금이면 편입생도 보통 해당되니, 편입생을 일부러 제외하고 싶은 장학금이 아닌 이상 `undergrad_transfer`를 따로 입력할 필요는 없습니다. 진짜로 "일반 신입생만(편입생 제외)"인 장학금이면 `min_grade=1, max_grade=1`을 같이 입력해주세요.

**`eligible_region`만 예외로 주의하세요**: 여기는 나중에 "사용자 지역 == 이 값"으로 정확히 비교하는 자동 매칭에 쓰일 예정이라, `대전 거주자가 타지역 대학 다니는 경우 대상` 같은 긴 설명 문장을 넣으면 그 장학금이 매칭에서 영원히 빠질 수 있습니다. 짧은 지역 태그만 넣고, 나머지 세부 조건은 `description`에 적어주세요.

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
