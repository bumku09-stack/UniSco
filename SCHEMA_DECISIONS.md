# 스키마 설계 결정사항

`scholarship`/`UserSpec` 관련 스키마를 바꿀 때마다 "왜 이렇게 바꿨는지"를 기록하는 문서입니다.
나중에 특정 변경의 이유가 궁금해지면 이 파일 하나만 보면 되도록 유지합니다.

형식:

```
### [날짜] 변경 제목
- 문제: (어떤 문제가 있었는지)
- 결정: (뭘로 바꿨는지)
- 이유: (왜 이렇게 했는지)
- 영향받는 테이블/쿼리: (실제로 같이 고친 파일 목록)
```

관련 문서: [supabase/matching_gaps.md](supabase/matching_gaps.md) (매칭 로직 미지원 자격조건 목록), [supabase/README.md](supabase/README.md), [EXTERNAL_SCHOLARSHIPS_PLAN.md](EXTERNAL_SCHOLARSHIPS_PLAN.md) (외부 재단/기업 장학금 수집 계획)

---

### 2026-08-05 부모 거주지역 필드 추가 (설계 완료, 구현 예정 — 아직 코드 반영 안 됨)

- 문제: "본인 또는 부모 중 1인이 OO 지역에 거주"가 자격조건인 장학금(재능키움 장학사업, 화성시인재육성재단 주거비지원, 인천 청년 해외배낭연수 장학생 등)이 실제로 존재하는데, `SavedSpec`/`UserSpec`엔 학생 본인의 `region`만 있어서 본인 거주지가 조건과 다르지만 부모가 그 지역에 사는 학생을 부당하게 걸러내고 있었음(false negative). 외부(재단/기업) 장학금을 새로 발굴하는 작업 중 발견 — `supabase/matching_gaps.md` 19번 참고.
- 결정:
  - `Scholarship.eligible_region`은 변경 없음(대상 지역 값 하나만 담으면 충분 — 본인/부모 중 누구 기준인지 구분할 필요 없음).
  - `SavedSpec`/`UserSpec`에 `parent_region: str | None` 추가(선택 입력, 본인 `region`과 동일한 시/도+구/군 옵션 재사용).
  - `backend/app/core/matching.py`의 `is_eligible()`에서 지역 조건을 `spec.region in eligible_region OR spec.parent_region in eligible_region`으로 변경.
  - 벤치마크로 참고한 Scholarships.com(매칭 항목 23종)에도 "부모 거주지역"이라는 별도 필드는 없었음(선례 없음, "직장" 항목만 본인/부모를 하나로 합쳐서 처리) — 참고만 하고 우리는 두 필드를 분리하기로 사용자가 직접 결정함.
  - 16번(부모 직업/소속 조건)은 이번엔 같이 처리 안 함 — 그쪽은 카테고리가 고정 목록이 아니라 계속 늘어나는 유형이라 설계에 시간이 더 필요해서 별도로 보류.
- 이유: 기존 데이터(`eligible_region` 값)를 재작업할 필요 없이, 학생 쪽 입력 필드 하나만 추가하고 매칭 로직만 OR 조건으로 바꾸는 게 가장 적은 변경으로 정확하게 고쳐짐.
- 영향받는 테이블/쿼리(예정, 아직 미구현): `savedspec` 테이블(`parent_region` 컬럼 추가), `backend/app/models/user_spec.py`, `backend/app/models/scholarship.py`(변경 없음, 확인만), `backend/app/core/matching.py`, `frontend/src/lib/spec.ts`, `frontend/src/app/spec/page.tsx`, `frontend/src/app/mypage/page.tsx`, `supabase/schema.sql`(스냅샷 갱신).
- **상태: 설계만 완료된 상태 — 실제 코드 변경은 아직 안 함.** 진행해도 좋다는 확인 있으면 다음 세션에서 구현.

---

### 2026-07-30 기존 133건에 구조화 필드(대학/단과대/재학상태/학년/석박사구분/대분류·중분류) 백필

- 문제: 호성이 `eligible_university`, `eligible_college`, `required_enrollment_status`, `min_grade`/`max_grade`, `required_degree_level`, `category_l1`/`category_l2` 컬럼을 추가했지만, 기존 133건은 전부 비어있어서 실제 매칭 동작을 확인할 수 없었음.
- 결정: 기존 `grade_level`/`major`/`affiliated_institution`(원문 텍스트)과 `name`(신입생/재학생 접미사 등)을 파싱해서 새 컬럼들을 채움. 128건은 규칙 기반으로 자동 판단, 5건(법학전문대학원 4건 + M.D.-Ph.D 1건)은 분류 체계 자체가 안 맞아 보류.
- 이유:
  - "학부생·대학원생 둘 다 대상"처럼 `required_enrollment_status`가 하나만 고르게 되어있어 표현이 안 되는 경우(인성장학금, 한국원자력학회장학금, 두산중공업장학금, KAIST 학생자치단체 간부장학금 3종, 감민호장학금)는 **비워둠(제한 없음)으로 처리** — `undergrad_enrolled`든 `post_undergrad`든 둘 다 통과되니 결과적으로 동일. (단, 학생 출산·육아지원금은 "휴학 중"만 대상이라 반대로 `undergrad_leave`로 명시 — 대학원생 휴학 케이스는 표현할 방법이 없어 근사치로 처리.)
  - 법학전문대학원(로스쿨) 4건과 M.D.-Ph.D 1건은 `eligible_college` 목록(`frontend/src/lib/universities.ts`)에 로스쿨 항목이 없고, `masters`/`doctoral`/`integrated_ms_phd` 어디에도 JD형·MD-PhD 통합과정이 깔끔히 안 맞아서 보류 — 호성이 백엔드에 학과/과정 추가하기로 함.
  - `category_l1`/`category_l2`는 호성이 정의한 taxonomy 그대로 적용(자격조건 아니라 표시/그룹핑용).
- 영향받는 테이블/쿼리: `scholarship` 테이블 데이터(스키마 변경 없음, UPDATE만). 코드 변경 없음 — 순수 데이터 백필.
- 알려진 한계(호성에게 전달 필요): `required_enrollment_status`가 "학부·대학원 둘 다 가능"이나 "대학원생 휴학"을 표현 못 함 — 향후 이런 케이스가 늘어나면 enum 확장이나 다중 선택 구조 고려 필요.

---

### 2026-07-31 편입 구분 추가 + 신입생 전용 장학금 학년 필터 백필

- 문제: 스펙 입력 위저드에서 재학상태를 "학부/대학원 등" → (학부인 경우) "재학/휴학/편입" → 학년 순으로 세분화하기로 했는데, `EnrollmentStatus`에 편입(transfer) 개념이 아예 없었음. 또한 "신입생" 전용 장학금 22건이 `min_grade`/`max_grade`가 비어있어서 학년 무관하게 전부 매칭되고 있었음(4학년도 신입생 전용 장학금에 매칭되는 상태) — 편입생을 신입생 전용 장학금에서 자동으로 걸러내려 해도 애초에 학년 필터 자체가 없어서 의미가 없었음.
- 결정:
  - `EnrollmentStatus`에 `UNDERGRAD_TRANSFER = "undergrad_transfer"` 추가 (Postgres `enrollmentstatus` enum에 `ALTER TYPE ... ADD VALUE`로 반영, 기존 133건 값은 안 건드림 — 추가만 하는 안전한 변경).
  - 매칭 로직(`backend/app/api/match.py`)에서 `required_enrollment_status = undergrad_enrolled`인 장학금은 `undergrad_transfer`도 통과시키도록 처리 — 기존 100여 건의 "재학생" 장학금이 편입생을 부당하게 걸러내지 않게 하기 위함.
  - "신입생" 이름이 붙은 장학금 중 `required_enrollment_status = undergrad_enrolled`이고 학년 제한이 비어있던 22건(대학원 신입생 7건은 애초에 학년 개념이 없어서 제외)에 `min_grade=1, max_grade=1` 백필.
- 이유: 편입생은 국내 대학 특성상 1학년으로 편입하는 경우가 사실상 없어서, "신입생 전용 = min_grade=1·max_grade=1"로 표현하면 별도 컬럼 없이도 편입생이 자연스럽게 걸러짐 — `required_enrollment_status`를 통한 배제보다 이 방식이 기존 데이터(어느 것도 편입 여부를 안 담고 있었음)와 더 안전하게 호환됨.
- 영향받는 테이블/쿼리: `enrollmentstatus` Postgres enum 타입(값 추가), `scholarship` 테이블 데이터(id 7,8,9,10,11,12,13,14,17,18,19,23,24,25,26,27,28,29,30,33,34,35의 `min_grade`/`max_grade` UPDATE), `backend/app/models/enums.py`, `backend/app/api/match.py`, `frontend/src/lib/spec.ts`, `frontend/src/app/spec/page.tsx`.

---

### 2026-08-05 부모님 거주지역(parent_region) 추가 — "본인 또는 부모" 거주지 OR 조건 지원

- 문제: 외부(재단/지자체) 장학금 발굴 작업 중 확인된 패턴 — 지자체 장학금은 대부분 "본인 또는
  부모 중 1인이 OO에 1년 이상 거주"처럼 학생 본인이 아니라 부모 주소지 기준으로도 자격이
  되는 OR 조건인데(예: `data_cnu.sql`의 "2026년 재능키움 장학사업(2차)" — `eligible_region='충남'`),
  기존 매칭 로직은 `spec.region`(본인 거주지)만 봤음 — 부모님은 충남에 살지만 학생 본인은
  대전에서 자취/기숙사 생활 중인 경우 실제로는 자격이 되는데도 매칭에서 빠지는 과소매칭 문제.
- 결정: `SavedSpec`/`UserSpec`에 `parent_region: str | None`(선택 입력) 추가. 새 컬럼을
  `scholarship` 쪽에 추가하는 대신, 기존 `eligible_region` 문자열은 그대로 두고 매칭 로직만
  "본인 거주지 OR 부모 거주지" OR으로 바꿈(`backend/app/core/matching.py`의
  `region_matches()`) — `eligible_region` 값 자체가 자격 지역명 하나뿐이라 본인/부모 어느 쪽이
  그 지역이든 결과는 같기 때문에 스키마를 스콜라십 쪽까지 건드릴 필요가 없었음.
  `parent_region`이 비어있으면(선택 안 함) 기존과 완전히 동일하게 본인 거주지만으로 판단함 —
  다른 선택 입력 필드들(소득분위·특수상황 등)과 달리 "안 넣으면 조건을 거르지 않는다"가 아니라
  "안 넣으면 원래 하던 대로 본인 거주지만 본다"는 뜻(원래도 그렇게 동작했으니 회귀 없음).
- 이유: 지자체 장학금 데이터를 새로 스캔한 366건 대조 결과, 시/도 단위로 지역 조건이 걸린
  건 대부분 이 "본인 또는 부모" 문구를 쓰고 있었고, 본인만 거주해야 한다는 명시적 반례는
  못 찾음 — OR로 넓히는 쪽이 항상 매칭을 늘리기만 하지 기존에 맞던 매칭을 틀리게 만들
  위험이 없어서, 스콜라십별로 "부모 인정 여부"를 따로 구분하는 컬럼 없이 전체 `eligible_region`
  조건에 일괄 적용하기로 함.
  프론트 UX: `/spec` 3페이지·`/mypage` 둘 다 기존 "선택 입력" 토글 패턴(어학점수·특수상황과
  동일한 `CollapsibleToggle`)으로 추가. 토글을 처음 켤 때 드롭다운 기본값을 본인이 이미
  고른 거주지역으로 미리 채워둠(`regionShortName(spec.sido, spec.district)`) — 부모님이
  본인과 같은 지역에 사는 학생이 많을 것으로 보고, 다르면 그때 바꾸도록 해서 입력 부담을
  줄임. 구/군 단위는 안 물어봄 — `eligible_region` 매칭 자체가 시/도(shortName) 단위까지만
  쓰여서(14번 갭 참고) 본인 거주지 쪽도 구/군은 매칭에 안 쓰이는 것과 동일.
- 영향받는 테이블/쿼리: `savedspec.parent_region` 컬럼 추가(`supabase/tools/migration_2026-08-05_parent_region.sql`,
  **사용자가 직접 `python run_sql.py migration_2026-08-05_parent_region.sql`로 실행해야 함**),
  `backend/app/models/user_spec.py`, `backend/app/models/saved_spec.py`, `backend/app/core/matching.py`,
  `frontend/src/lib/regions.ts`(`PARENT_REGION_OPTIONS` 추가), `frontend/src/lib/spec.ts`,
  `frontend/src/app/spec/page.tsx`, `frontend/src/app/mypage/page.tsx`. 기존 366건 장학금
  데이터는 수정 불필요(스콜라십 쪽 스키마/값 변경 없음, `eligible_region` 그대로 재사용) —
  이 기능은 순수하게 "학생이 입력할 수 있는 항목 + 매칭 판단 로직" 확장이라 새 매칭 갭 문서
  번호(19번)로 `matching_gaps.md`에 기록함.

---

### 2026-08-05(같은 날 이어서) 시/군/구 단위 지자체 장학금 매칭 — district/parent_district 추가

- 문제: 위 `parent_region` 작업 직후 사용자가 "정읍시민장학재단 이런 건 어떻게 해결할 건데"라고
  지적함 — 정읍시민장학재단(`data_cnu.sql`)은 "부 또는 모 1인이 정읍시에 1년 이상 거주" 조건인데,
  `eligible_region`이 시/도 단위 문자열만 담을 수 있어서(2026-08-02 기록된 14번 갭) 여태
  `eligible_region`을 비워두고 `description`에만 텍스트로 남기는 임시방침(과다노출)으로
  버티고 있었음.
- 결정: `SavedSpec`/`UserSpec`에 `district`(본인 기초자치단체)·`parent_district`(부모 쪽)
  추가. `region_matches()`를 "본인 시/도·본인 시/군/구·부모 시/도·부모 시/군/구" 4개 후보
  중 하나라도 `eligible_region`에 부분 문자열로 포함되면 통과하도록 확장 — `eligible_region`
  쪽 스키마는 그대로 두고(시/도 문자열이든 "정읍시" 같은 시/군/구 문자열이든 같은 컬럼에
  그대로 넣음), 비교 로직만 확장해서 처리함.
- 이유: 본인 쪽 `district`는 사실 프론트 스펙 입력 위저드가 이미 "기초자치단체" 드롭다운으로
  물어보고 있던 값이었음 — 2026-07-30 초기 설계 당시 "매칭에 아직 구 단위까지는 안 쓴다"고
  의도적으로 버렸던 것뿐이라, 서버로 그냥 보내기만 하면 되는 상태였음(새 UI를 만들 필요가
  없었음). 시/도든 시/군/구든 "eligible_region 문자열에 부분 문자열로 포함되는지"라는 동일한
  검사로 처리 가능해서(구/군 이름이 시/도 shortName의 부분 문자열이 되는 경우가 없음) 별도
  타입/컬럼 분기 없이 기존 `parent_region` OR 로직에 자연스럽게 합류시킴.
  **구현 중 발견한 버그**: `district`가 빈 문자열("", 세종처럼 하위 구/군이 없는 시/도의
  기본값)일 때 이걸 그대로 후보에 넣으면 파이썬 `"" in eligible_region`이 항상 `True`라서
  지역 조건이 있는 장학금이 전부 통과해버리는 심각한 과다노출 버그가 됨 — 빈 문자열은 후보
  목록에서 제외하도록 수정, synthetic 테스트로 확인.
  366건 전체를 "OO시/OO군/OO구 ... 거주" 패턴으로 재검색해서 정읍시민장학재단·화성시인재육성재단
  소상공인 장학금 2건 외에 다른 미해결 사례가 없음을 확인하고, 이 2건의 `eligible_region`을
  각각 "정읍시"/"화성시"로 채움(운영 DB 데이터 UPDATE — 스키마 변경이 아니라 값 채우기라
  기존 관례대로 직접 실행함, `data_cnu.sql` 백업도 동기화).
- 영향받는 테이블/쿼리: `savedspec.district`/`savedspec.parent_district` 컬럼 추가
  (`supabase/tools/migration_2026-08-05b_district.sql`, **사용자가 직접 `python run_sql.py
  migration_2026-08-05b_district.sql`로 실행 필요**), `scholarship` 테이블 데이터(id 74·75의
  `eligible_region` UPDATE, 운영 DB + `data_cnu.sql`), `backend/app/models/user_spec.py`,
  `backend/app/models/saved_spec.py`, `backend/app/core/matching.py`,
  `frontend/src/lib/spec.ts`, `frontend/src/lib/regions.ts`(`PARENT_REGION_OPTIONS` 제거 —
  이제 부모님 쪽도 본인과 동일한 시/도+구/군 캐스케이딩 드롭다운을 써서 평평한 shortName
  목록이 필요 없어짐), `frontend/src/app/spec/page.tsx`, `frontend/src/app/mypage/page.tsx`.

---
