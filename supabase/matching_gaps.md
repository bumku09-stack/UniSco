# 매칭 로직 미지원 자격조건 목록 (호성 전달용)

이 파일은 실행되는 코드가 아니라, `scholarship` 테이블에는 크롤링으로 계속 데이터가 쌓이는데 백엔드 매칭 로직(`backend/app/models/user_spec.py`의 `UserSpec`)이 아직 걸러내지 못하는 자격조건을 놓치지 않고 기록해두는 목록입니다.

**규칙: 크롤링하다가 아래 표에 없는 새로운 미지원 조건이 나오면 이 파일에 바로 추가할 것.**

마지막 업데이트: 2026-07-30 (호성이 university/college/enrollment-status/degree-level/category 컬럼과 `/match` 엔드포인트를 실제로 구현·배포함에 따라 아래 표 갱신 — 1·3번 해결, 새 이슈 2건 발견)

---

## 확인된 사실 (backend/app/models/ 코드 기준, 2026-07-30)

`UserSpec`(사용자 입력값): `university`, `college`, `gpa`, `age`, `gender`, `region`, `military_status`, `income_bracket`, `has_disability`, `is_foreigner`, `enrollment_status`, `grade`, `degree_level`.

`scholarship` 테이블에서 실제로 매칭되는 필드(`backend/app/api/match.py`): `min_age`/`max_age`, `required_gender`, `eligible_region`, `required_military_status`, `max_income_bracket`, `min_gpa`, `requires_disability`, `foreigner_eligibility`, `eligible_university`, `eligible_college`, `required_enrollment_status`, `min_grade`/`max_grade`, `required_degree_level`.

기존 133건 중 128건은 이 신규 필드까지 실제 값으로 백필 완료(2026-07-30, `SCHEMA_DECISIONS.md` 참고). 나머지 필드(`grade_level`, `major`, `affiliated_institution`, `min_credits`, `admission_score_condition`, `headcount`, `application_period`, `category_l1`/`category_l2`)는 **컬럼은 있지만 매칭 로직에서는 전혀 안 쓰임**(`category_l1`/`l2`는 애초에 자격조건이 아니라 분류용이라 매칭 대상이 아닌 게 의도된 설계).

## GPA 관련 참고 (혼동 방지용)

`min_gpa`(장학금 쪽 최소학점 조건)는 **이미 컬럼도 있고 데이터도 채워지고 있음** — 크롤링 중 등급→GPA 환산 기준을 대학마다 한 번 확정해서 적용 중(예: 충남대 A0=4.0/4.5만점, KAIST는 4.3만점제 별도 환산표 사용). 이건 갭이 아님.

진짜 갭은 **`UserSpec.gpa`(사용자가 직접 입력하는 값)의 스케일이 정의·검증되지 않는다는 것**: 4.5만점제 학교 학생과 KAIST처럼 4.3만점제 학교 학생이 서로 다른 기준으로 숫자를 넣어도 시스템이 구분 못 함 → 아래 표 4번. **(2026-07-30 추가 확인: `universities.ts`에 학교별 `gpaScale`이 이미 있고 프론트 라벨에도 반영되는데, 실제 제출값을 그 스케일로 환산하는 로직이 없어서 여전히 버그로 남아있음 — `backend/app/api/match.py`의 `spec.gpa < scholarship.min_gpa` 직접비교 부분.)**

## 매칭 안 되는 자격조건 목록

| # | 조건 | scholarship 테이블 컬럼 | 상태 |
|---|---|---|---|
| 1 | 소속 대학 | `eligible_university` | ✅ **해결** (2026-07-29, `eligible_university`/`eligible_college` + `UserSpec.university`/`college`로 매칭됨) |
| 2 | 전공 | `major` | 아직 미해결 — `major` 컬럼은 있지만 `UserSpec`에 대응 필드 없음 |
| 3 | 학년/과정(신입생·재학생, 학부·대학원) | `required_enrollment_status`/`required_degree_level` | ✅ **해결** (2026-07-29, `EnrollmentStatus`/`DegreeLevel` enum + `min_grade`/`max_grade`로 매칭됨). **단, 새로 발견된 한계 2건은 아래 "3번 후속" 참고** |
| 4 | 사용자 GPA 입력 스케일 검증 | (UserSpec.gpa 자체) | 아직 미해결 — 위 GPA 참고 항목 참조 |
| 5 | 이수학점 | `min_credits` | 컬럼 있음(텍스트), 매칭 로직 없음 |
| 6 | 입학성적(수능/내신) 조건 | `admission_score_condition` | 컬럼 있음(텍스트), 매칭 로직 없음 |
| 7 | 마감일(구조화된 날짜) | `application_period`(텍스트만) | 구조화된 date 컬럼 자체가 없음 → DB에 넣은 뒤 마감이 지나도 자동으로 안 빠짐 |
| 8 | 선발인원 | `headcount` | 컬럼 있음(텍스트), 매칭/정렬에 활용 안 됨 |
| 9 | 특수상황 신분(다문화가정·아동양육시설 생활자/퇴소자·학생자치단체 임원 등) | 없음 | 아직 미해결 — **사용자 확정(2026-08-01): 나중에 "특수상황 조건" 카테고리를 새로 만들 때 새터민(북한이탈주민)과 함께 묶어서 처리하기로 함.** 지금은 각 장학금 `description`에 텍스트로만 남겨둠(예: 한밭대 다문화가정장학금 id 147, 혜윰Ⅲ장학금 id 139) |
| 10 | 외국어 시험 점수(TOPIK/IELTS/TOEIC 등) | 없음 | 아직 미해결 — 사용자 제안(2026-08-01): "외국어 점수" 입력칸 추가. **주의**: 시험마다 종류·점수체계가 다 다름(TOPIK은 1~6급, IELTS는 0~9밴드, TOEIC은 0~990점) — GPA 스케일 문제(4번)와 같은 종류의 함정이라 단순 숫자 하나로는 안 되고 "시험 종류 + 점수"를 같이 받아야 함. 스키마 변경이라 호성 확인 필요 |
| 11 | 학교 자체 비학점(비교과) 프로그램 이수 조건(한밭대 "비교과 유닛" 등) | 없음 | ✅ **필터링 대상 아님으로 확정(2026-08-01, 사용자 결정)** — 학교마다 명칭·기준이 다 달라서 표준화된 필드로 만들기 어려움. 별도 매칭 컬럼 만들지 않고 `description`에 텍스트로만 기록하는 것으로 방침 확정. 앞으로 크롤링하다 비슷한 "학교 자체 비학점 이수 조건"(예: 타 대학의 유사 비교과 프로그램) 나오면 이 방침 그대로 적용 |
| 12 | 장애인 세부 유형 | 없음(`has_disability`는 boolean만) | 아직 미해결 — 2026-08-02 사용자 확정: 세부유형을 실제 선택지로 받기로 함. 아래 "9·10·12번 프론트 시안" 참고 |

### 9·10·12번 프론트 시안 — 2026-08-02 (스키마 미반영, 로컬 프리뷰만)

`frontend/src/app/spec/page.tsx`(1·2페이지 + "선택페이지" 3페이지 구조로 개편)와 `frontend/src/app/mypage/page.tsx` 둘 다에, 사용자가 스케치로 그려준 대로 어학점수·장애인 세부유형·특수상황 3개 항목을 접혔다 펼치는 토글 형태로 만들어둠(공통 옵션 목록은 `frontend/src/lib/spec.ts`). **다만 DB/백엔드에 이 값들을 저장할 칸이 아직 없어서, 지금은 화면 입력만 되고 실제 제출(`POST`/`PUT /users/me/spec`) 바디에는 안 실림** — [[CLAUDE.local.md]] 방침대로 스키마는 손대지 않고 프론트만 먼저 만들어서 로컬에서 확인받는 중.

호성이 스키마 추가할 때 필요한 것:
- **어학점수**: 시험 종류(`TOEIC`/`TOEFL`/`IELTS`/`TOPIK`/`기타`) + 점수(숫자) 두 값.
- **장애인 세부유형**: 단일 선택 — **2026-08-02 사용자 지정: Scholarships.com의 "Physical Disabilities" 카테고리(7개 전체)를 그대로 채택**(`scholarships_com_전체항목_한국어정리.pdf`, 사용자 컴퓨터 Downloads 폴더에 보관 중 — 새로 만든 목록 아니고 기존 조사 자료에서 가져옴): `physical_impairment`(신체적 장애)/`learning_disability`(학습장애)/`medical_disability`(의료적 장애·질환)/`mental_impairment`(정신적 장애)/`muscular_dystrophy`(근이영양증)/`developmental_impairment`(발달장애)/`disabled_parent`(장애가 있는 부모·자녀 대상). 기존 `has_disability` boolean은 그대로 두고 세부유형만 추가 컬럼으로. **주의**: 마지막 `disabled_parent`는 본인 장애가 아니라 "부모가 장애인인 학생" 대상이라 성격이 다른 항목인데, Scholarships.com 원본 카테고리에 포함돼 있어서 그대로 가져옴.
- **특수상황**: 다중 선택 가능(사용자 확정, 2026-08-01) — `north_korean_defector`(북한이탈주민)/`multicultural_family`(다문화가정)/`child_care_facility`(아동양육시설 생활자·퇴소자)/`student_council_officer`(학생회장·임원)까지는 사용자가 직접 지정한 4개, 나머지 `single_parent_family`(한부모가정)/`grandparent_family`(조손가정)/`multi_child_family`(다자녀가정 3자녀 이상)/`national_merit`(국가보훈대상자) 4개는 크롤링 중 반복적으로 나온 실제 장학금 조건들(`scholarship_dedup_list.md` 참고: 보훈/다자녀/국가유공자 등)을 근거로 Claude가 판단해서 추가함 — 사용자에게 "잘 판단해서 만들어보라"는 위임을 받고 진행(최종 확정은 아니니 호성·사용자가 다시 검토해도 됨).
- 세 항목 모두 `SavedSpec`(저장용 테이블)과, 매칭에 실제로 쓰려면 `Scholarship` 쪽에도 대응 컬럼이 있어야 함 — 지금은 프론트 UI만 있고 어느 쪽 테이블도 안 건드림.

### 3번 후속: 백필하면서 새로 발견된 한계 (2026-07-30)

기존 133건 중 128건에 실제 값을 채우면서 확인된, `required_enrollment_status`(`undergrad_enrolled`/`undergrad_leave`/`post_undergrad` 3택1) 설계의 한계:

1. **"학부생·대학원생 둘 다 대상"을 표현 못 함** — 실제로 이런 장학금이 7건 있었음(KAIST 인성장학금, 한국원자력학회장학금, 두산중공업장학금, 학생자치단체 간부장학금 3종, 감민호장학금). 지금은 그냥 비워둠(제한 없음)으로 처리했는데, 이게 결과적으로는 맞지만(둘 다 통과되니) — "휴학생은 제외하고 재학 중인 학부/대학원생만"처럼 더 세밀한 조건은 표현이 안 됨.
2. **대학원생의 "휴학" 상태를 표현 못 함** — `undergrad_leave`만 있고 대학원 버전이 없음. "학생 출산·육아지원금"(KAIST, 휴학 중인 사람 대상)은 학부생 기준(`undergrad_leave`)으로 근사 처리함 — 대학원생이 이 사유로 휴학 중이면 지금 시스템에서 놓치게 됨.
3. **법학전문대학원(로스쿨) 계열이 분류 체계에 안 맞음** — ✅ **부분 해결 (2026-07-31)**. `frontend/src/lib/universities.ts`의 충남대 단과대 목록에 `법학전문대학원`/`의학전문대학원`을 추가하고, 로스쿨 장학금 4건(id 15·16·43·44)은 `eligible_university=충남대학교`/`eligible_college=법학전문대학원`/`required_enrollment_status=post_undergrad`로, MD-Ph.D 통합과정 1건(id 92)은 같은 방식+`eligible_college=의학전문대학원`으로 분류함. `required_degree_level`은 JD형 전문대학원엔 맞는 값이 없어서 비워둠(제한 없음) — 어차피 `eligible_college`로 이미 좁혀지니 결과적으로는 문제없음. 다만 MD-Ph.D의 `required_degree_level=integrated_ms_phd`는 정확한 값이 없어서 가장 가까운 값으로 근사 처리한 것 — 정식으로 JD/MD-PhD 전용 값을 enum에 추가할지는 호성과 논의 필요.

---

## 그 외 호성과 논의할 사항 (자격조건 매칭과는 별개)

1. **UserSpec 저장** — 🔶 부분 해결(2026-07-29): 로그인 없이 프론트 `localStorage`에 클라이언트 저장하는 방식으로 일단 재입력 부담은 줄임(`user_spec.py` 주석: "Once auth exists this should move to a real per-user table instead"). 서버 쪽 진짜 계정/프로필 저장은 아직 없음 — 나중에 로그인 도입 여부 결정 필요.
2. **DB에 중복 방지 제약이 없음** — 지금 중복 제거는 `scholarship_dedup_list.md`를 사람이 손으로 대조하는 방식뿐. 대학이 늘어날수록(한밭대·카이스트 이후 계속) 깨지기 쉬움 — `name+provider` 유니크 제약이나 INSERT 전 자동 중복검사를 백엔드에 둘지 논의. **(아직 미해결)**
3. ~~새 필드 추가 시 프론트엔드도 같이 손봐야 함~~ — ✅ 해결(2026-07-29, 대학/단과대/학년/재학상태 드롭다운 있는 스펙 입력 마법사(`frontend/src/app/spec/page.tsx`)로 이미 구현됨).
4. **마감일 자동 정리** (위 표 7번의 연장) — 대학이 늘어나면 이미 넣은 장학금들의 마감이 하나둘 지나갈 텐데, 주기적 재크롤링/정리 계획이 필요한지, 구조화된 deadline 컬럼으로 자동 필터링할지 방향 결정 필요. **(아직 미해결)**
5. **한밭대·배재대·목원대·우송대·한남대가 `frontend/src/lib/universities.ts` 대학 드롭다운에 없음** (2026-08-01 발견) — `scholarship` 테이블에는 5개 대학 전부 이미 데이터 넣었지만(한밭대 20건 id 134~153, 배재대 21건 id 154~174, 목원대 25건 id 175~199, 우송대 16건 id 200~215, 한남대 35건 id 216~250, 총 117건), 프론트 스펙 입력 마법사의 대학 선택지에 없으면 이 5개 대학 학생은 애초에 스펙을 입력할 수 없어서 전부 매칭에서 안 걸림(충남대 전례와 동일한 문제, 당시 규칙 1번 참고). 코드 변경(`universities.ts`)이라 [[CLAUDE.local.md]] 방침대로 직접 고치지 않고 여기 기록만 해둠 — 호성이 대학들 추가할 때 **대학별 GPA 스케일을 각각 다르게** 넣어야 함:
   - 한밭대·배재대·목원대·우송대: 4.5만점, A0=4.00 (충남대와 동일)
   - **한남대만 예외**: 등급이 +/0/- 세 단계라 A0=4.30, A-=4.00 (전체 환산표는 `scholarship_dedup_list.md` 한남대 섹션 참고) — 다른 대학과 똑같이 "A0=4.0"으로 넣으면 틀림.
   **(아직 미해결)**

---

## 참고

관련 크롤링 규칙: [supabase/scholarship_dedup_list.md](scholarship_dedup_list.md), [supabase/README.md](README.md)
