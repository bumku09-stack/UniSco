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

### 3번 후속: 백필하면서 새로 발견된 한계 (2026-07-30)

기존 133건 중 128건에 실제 값을 채우면서 확인된, `required_enrollment_status`(`undergrad_enrolled`/`undergrad_leave`/`post_undergrad` 3택1) 설계의 한계:

1. **"학부생·대학원생 둘 다 대상"을 표현 못 함** — 실제로 이런 장학금이 7건 있었음(KAIST 인성장학금, 한국원자력학회장학금, 두산중공업장학금, 학생자치단체 간부장학금 3종, 감민호장학금). 지금은 그냥 비워둠(제한 없음)으로 처리했는데, 이게 결과적으로는 맞지만(둘 다 통과되니) — "휴학생은 제외하고 재학 중인 학부/대학원생만"처럼 더 세밀한 조건은 표현이 안 됨.
2. **대학원생의 "휴학" 상태를 표현 못 함** — `undergrad_leave`만 있고 대학원 버전이 없음. "학생 출산·육아지원금"(KAIST, 휴학 중인 사람 대상)은 학부생 기준(`undergrad_leave`)으로 근사 처리함 — 대학원생이 이 사유로 휴학 중이면 지금 시스템에서 놓치게 됨.
3. **법학전문대학원(로스�쿨) 계열이 분류 체계에 안 맞음** — `eligible_college` 목록(`frontend/src/lib/universities.ts`)에 로스쿨 항목 자체가 없고, `required_degree_level`(masters/doctoral/integrated_ms_phd)도 JD형 전문대학원엔 안 맞음. CNU 로스쿨 장학금 4건 + MD-Ph.D 통합과정 1건, 총 5건이 이 문제로 아직 미분류 상태로 남아있음 — 호성이 백엔드에 학과/과정 추가 예정.

---

## 그 외 호성과 논의할 사항 (자격조건 매칭과는 별개)

1. **UserSpec 저장** — 🔶 부분 해결(2026-07-29): 로그인 없이 프론트 `localStorage`에 클라이언트 저장하는 방식으로 일단 재입력 부담은 줄임(`user_spec.py` 주석: "Once auth exists this should move to a real per-user table instead"). 서버 쪽 진짜 계정/프로필 저장은 아직 없음 — 나중에 로그인 도입 여부 결정 필요.
2. **DB에 중복 방지 제약이 없음** — 지금 중복 제거는 `scholarship_dedup_list.md`를 사람이 손으로 대조하는 방식뿐. 대학이 늘어날수록(한밭대·카이스트 이후 계속) 깨지기 쉬움 — `name+provider` 유니크 제약이나 INSERT 전 자동 중복검사를 백엔드에 둘지 논의. **(아직 미해결)**
3. ~~새 필드 추가 시 프론트엔드도 같이 손봐야 함~~ — ✅ 해결(2026-07-29, 대학/단과대/학년/재학상태 드롭다운 있는 스펙 입력 마법사(`frontend/src/app/spec/page.tsx`)로 이미 구현됨).
4. **마감일 자동 정리** (위 표 7번의 연장) — 대학이 늘어나면 이미 넣은 장학금들의 마감이 하나둘 지나갈 텐데, 주기적 재크롤링/정리 계획이 필요한지, 구조화된 deadline 컬럼으로 자동 필터링할지 방향 결정 필요. **(아직 미해결)**

---

## 참고

관련 크롤링 규칙: [supabase/scholarship_dedup_list.md](scholarship_dedup_list.md), [supabase/README.md](README.md)
