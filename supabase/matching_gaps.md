# 매칭 로직 미지원 자격조건 목록 (호성 전달용)

이 파일은 실행되는 코드가 아니라, `scholarship` 테이블에는 크롤링으로 계속 데이터가 쌓이는데 백엔드 매칭 로직(`backend/app/models/user_spec.py`의 `UserSpec`)이 아직 걸러내지 못하는 자격조건을 놓치지 않고 기록해두는 목록입니다.

**규칙: 크롤링하다가 아래 표에 없는 새로운 미지원 조건이 나오면 이 파일에 바로 추가할 것.**

마지막 업데이트: 2026-08-02 (한남대/한밭대 재검증 작업 중 새 이슈 2건 발견 — 13번 GPA 직전학기/전체누적 구분, 14번 지자체 장학금 시/군/구 단위 거주지 매칭)

이전 업데이트: 2026-07-30 (호성이 university/college/enrollment-status/degree-level/category 컬럼과 `/match` 엔드포인트를 실제로 구현·배포함에 따라 아래 표 갱신 — 1·3번 해결, 새 이슈 2건 발견)

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
| 13 | GPA "직전학기" vs "전체(누적)" 기준 구분 | `min_gpa` (단일 컬럼) | 아직 미해결 — 2026-08-02 우송대 재검증 중 사용자 발견. 아래 "13번: GPA 직전학기/전체 구분" 참고 |
| 14 | 지자체 장학금의 거주지 세부단위(시/군/구) | `eligible_region` (시/도 단위 문자열만) | 아직 미해결 — 2026-08-02 발견. 아래 "14번: 거주지 세부단위 매칭" 참고 |

### 9·10·12번 프론트 시안 — 2026-08-02 (스키마 미반영, 로컬 프리뷰만)

`frontend/src/app/spec/page.tsx`(1·2페이지 + "선택페이지" 3페이지 구조로 개편)와 `frontend/src/app/mypage/page.tsx` 둘 다에, 사용자가 스케치로 그려준 대로 어학점수·장애인 세부유형·특수상황 3개 항목을 접혔다 펼치는 토글 형태로 만들어둠(공통 옵션 목록은 `frontend/src/lib/spec.ts`). **다만 DB/백엔드에 이 값들을 저장할 칸이 아직 없어서, 지금은 화면 입력만 되고 실제 제출(`POST`/`PUT /users/me/spec`) 바디에는 안 실림** — [[CLAUDE.local.md]] 방침대로 스키마는 손대지 않고 프론트만 먼저 만들어서 로컬에서 확인받는 중.

호성이 스키마 추가할 때 필요한 것:
- **어학점수**: 시험 종류(`TOEIC`/`TOEFL`/`IELTS`/`TOPIK`/`기타`) + 점수(숫자) 두 값.
- **장애인 세부유형**: 단일 선택 — **2026-08-02 사용자 지정: Scholarships.com의 "Physical Disabilities" 카테고리(7개 전체)를 그대로 채택**(`scholarships_com_전체항목_한국어정리.pdf`, 사용자 컴퓨터 Downloads 폴더에 보관 중 — 새로 만든 목록 아니고 기존 조사 자료에서 가져옴): `physical_impairment`(신체적 장애)/`learning_disability`(학습장애)/`medical_disability`(의료적 장애·질환)/`mental_impairment`(정신적 장애)/`muscular_dystrophy`(근이영양증)/`developmental_impairment`(발달장애)/`disabled_parent`(장애가 있는 부모·자녀 대상). 기존 `has_disability` boolean은 그대로 두고 세부유형만 추가 컬럼으로. **주의**: 마지막 `disabled_parent`는 본인 장애가 아니라 "부모가 장애인인 학생" 대상이라 성격이 다른 항목인데, Scholarships.com 원본 카테고리에 포함돼 있어서 그대로 가져옴.
- **특수상황**: 다중 선택 가능(사용자 확정, 2026-08-01) — `north_korean_defector`(북한이탈주민)/`multicultural_family`(다문화가정)/`child_care_facility`(아동양육시설 생활자·퇴소자)/`student_council_officer`(학생회장·임원)까지는 사용자가 직접 지정한 4개, 나머지 `single_parent_family`(한부모가정)/`grandparent_family`(조손가정)/`multi_child_family`(다자녀가정 3자녀 이상)/`national_merit`(국가보훈대상자) 4개는 크롤링 중 반복적으로 나온 실제 장학금 조건들(`scholarship_dedup_list.md` 참고: 보훈/다자녀/국가유공자 등)을 근거로 Claude가 판단해서 추가함 — 사용자에게 "잘 판단해서 만들어보라"는 위임을 받고 진행(최종 확정은 아니니 호성·사용자가 다시 검토해도 됨).
- 세 항목 모두 `SavedSpec`(저장용 테이블)과, 매칭에 실제로 쓰려면 `Scholarship` 쪽에도 대응 컬럼이 있어야 함 — 지금은 프론트 UI만 있고 어느 쪽 테이블도 안 건드림.
- 디자인 확인 완료(2026-08-02, 사용자 승인) — 이제 실제 구현은 호성 담당. 아래 "실제 구현 시 해야 할 일"과 "특수상황 매칭 로직" 참고.

### 실제 구현 시 해야 할 일 (호성 담당)

1. `backend/app/models/saved_spec.py`(`SavedSpec`)와 `backend/app/models/user_spec.py`(`UserSpec`, `/match` 요청 바디)에 새 필드 추가: 어학점수(시험종류+점수), 장애인 세부유형(단일 선택), 특수상황(다중 선택 리스트).
2. `backend/app/models/scholarship.py`(`Scholarship`)에도 대응 컬럼 추가: 장학금이 요구하는 어학점수 조건(있다면), 장학금이 요구하는 장애인 세부유형(있다면), 장학금이 요구하는 특수상황(있다면, 위 목록 중 1개 — 지금까지 크롤링한 133~250번대 기존 장학금 중 새터민/다문화가정/보훈 등 조건이 `description`에 텍스트로만 있던 것들은 이 새 컬럼으로 재분류 필요).
3. `backend/app/core/matching.py`의 `is_eligible()`에 세 필드 검사 로직 추가 — 특수상황은 아래 "특수상황 매칭 로직" 그대로, 어학점수·장애인 세부유형은 다른 필드들과 같은 표준 패턴(`scholarship.필드 is not None`이고 `spec.필드`가 없거나 안 맞으면 `return False`)으로 하면 됨.
4. `frontend/src/lib/spec.ts`의 `UserSpec`/`SpecForm`에 이 필드들 추가하고, `specFormToUserSpec`/`userSpecToSpecForm`에서 변환하도록 연결, `/spec`·`/mypage`의 `handleFinalSubmit`/`handleSubmit`이 실제로 서버에 보내도록 수정(지금은 `optionalInfo` state가 로컬에만 있고 제출 안 됨).

### 특수상황 매칭 로직 (2026-08-02, 사용자 확정 — 다른 필드들과 다른 예외 규칙)

다른 필드(성별·나이·GPA 등)는 전부 "장학금에 조건이 있으면, 유저가 그 조건에 안 맞을 때 제외" 방식임. **특수상황은 이거랑 다르게, "유저가 특수상황을 아예 선택 안 했으면 애초에 걸러내지 않는다"는 예외 규칙**을 사용자가 명시적으로 요구함:

- **유저가 특수상황을 하나도 선택 안 함** → 특수상황 조건이 걸려있는 장학금도 걸러내지 않고 그냥 다 보여줌 (마치 특수상황 필드 자체가 없는 것처럼 동작).
- **유저가 특수상황을 1개 이상 선택함** → 그때부터 특수상황 조건이 걸려있는 장학금만 필터링 시작: 유저가 선택한 항목과 장학금이 요구하는 항목이 일치하면 보여주고, 안 맞으면 제외. **특수상황 조건이 아예 없는 일반 장학금은 이 필터링과 무관하게 계속 다 보임.**

**이유(사용자 설명)**: 특수상황은 선택 항목(옵션)이라 안 누른 학생이 많을 텐데, "안 눌렀다"는 게 "나는 특수상황 대상자가 아니다"를 확정하는 게 아님 — 그냥 아직 대답 안 한 것뿐. 그런데 표준 방식대로 처리하면, 실제로는 다문화가정인 학생이 그 항목을 안 눌렀다는 이유만으로 다문화가정 전용 장학금이 안 보이게 될 수 있음 — 그건 잘못된 결과. 그래서 "선택 안 함 = 모르는 것 = 걸러내지 않음", "선택함 = 그 항목 기준으로만 좁힘"으로 설계함.

의사코드(참고용, 그대로 코드로 옮기면 됨):
```python
def special_status_matches(scholarship_special_status: str | None, spec_special_status: list[str]) -> bool:
    if scholarship_special_status is None:
        return True  # 특수상황 조건 없는 일반 장학금 — 항상 통과
    if not spec_special_status:
        return True  # 유저가 특수상황 아예 안 눌렀음 — 그래도 걸러내지 않음
    return scholarship_special_status in spec_special_status
```
`is_eligible()`에 다른 필드들과 같은 자리에 `if not special_status_matches(scholarship.required_special_status, spec.special_status): return False` 형태로 추가하면 됨.

### 3번 후속: 백필하면서 새로 발견된 한계 (2026-07-30)

기존 133건 중 128건에 실제 값을 채우면서 확인된, `required_enrollment_status`(`undergrad_enrolled`/`undergrad_leave`/`post_undergrad` 3택1) 설계의 한계:

1. **"학부생·대학원생 둘 다 대상"을 표현 못 함** — 실제로 이런 장학금이 7건 있었음(KAIST 인성장학금, 한국원자력학회장학금, 두산중공업장학금, 학생자치단체 간부장학금 3종, 감민호장학금). 지금은 그냥 비워둠(제한 없음)으로 처리했는데, 이게 결과적으로는 맞지만(둘 다 통과되니) — "휴학생은 제외하고 재학 중인 학부/대학원생만"처럼 더 세밀한 조건은 표현이 안 됨.
2. **대학원생의 "휴학" 상태를 표현 못 함** — `undergrad_leave`만 있고 대학원 버전이 없음. "학생 출산·육아지원금"(KAIST, 휴학 중인 사람 대상)은 학부생 기준(`undergrad_leave`)으로 근사 처리함 — 대학원생이 이 사유로 휴학 중이면 지금 시스템에서 놓치게 됨.
3. **법학전문대학원(로스쿨) 계열이 분류 체계에 안 맞음** — ✅ **부분 해결 (2026-07-31)**. `frontend/src/lib/universities.ts`의 충남대 단과대 목록에 `법학전문대학원`/`의학전문대학원`을 추가하고, 로스쿨 장학금 4건(id 15·16·43·44)은 `eligible_university=충남대학교`/`eligible_college=법학전문대학원`/`required_enrollment_status=post_undergrad`로, MD-Ph.D 통합과정 1건(id 92)은 같은 방식+`eligible_college=의학전문대학원`으로 분류함. `required_degree_level`은 JD형 전문대학원엔 맞는 값이 없어서 비워둠(제한 없음) — 어차피 `eligible_college`로 이미 좁혀지니 결과적으로는 문제없음. 다만 MD-Ph.D의 `required_degree_level=integrated_ms_phd`는 정확한 값이 없어서 가장 가까운 값으로 근사 처리한 것 — 정식으로 JD/MD-PhD 전용 값을 enum에 추가할지는 호성과 논의 필요.

### 13번: GPA "직전학기" vs "전체(누적)" 구분 (2026-08-02, 사용자 발견)

우송대 장학금 재검증 중 사용자가 발견: 같은 대학 안에서도 어떤 장학금은 **직전학기 성적만** 보고(예: 우송대 성적우수 교내장학금 "자립/단정/독행/협동" — 직전학기 평점평균 3.0이상), 어떤 장학금은 **전체 재학기간 누적(CGPA)** 을 보거나(예: 우송대 국제학생 대상 "글로벌 유학생 성적A~E" — "GPA(직전학기) 또는 CGPA(전체학기) 평균"), 아예 두 기준 중 유리한 쪽을 인정해주는 경우도 있음. 지금 `scholarship.min_gpa`는 이 둘을 구분 없이 숫자 하나로만 받고, `UserSpec.gpa`도 사용자가 "내 학점"이라고 입력하는 값이 직전학기 기준인지 전체 누적 기준인지 정의가 없어서, 사실상 서로 다른 두 종류의 조건을 같은 숫자 하나로 뭉뚱그려 비교하고 있는 셈임(4번 GPA 스케일 문제와는 별개의 새로운 갭).

- **영향**: 예를 들어 직전학기 성적은 낮았지만 전체 누적은 높은(혹은 그 반대) 학생이 있으면, 장학금이 실제로 어느 기준을 요구하는지에 따라 매칭 결과가 달라져야 하는데 지금은 구분이 안 돼서 부정확한 매칭이 날 수 있음.
- **제안(호성 검토 필요, 스키마 변경 사안이라 여기 문서화만 하고 직접 구현 안 함)**: `scholarship` 테이블에 `min_gpa`를 대체하거나 보완하는 방식으로 "이 장학금이 요구하는 게 직전학기 기준인지 전체누적 기준인지"를 나타내는 컬럼(예: `gpa_basis` enum: `semester`/`cumulative`/`either`) 추가 검토. `UserSpec`/`SavedSpec`도 마찬가지로 사용자가 직전학기 GPA와 전체누적 GPA를 각각 따로 입력받는 두 칸으로 나누는 방안 검토.
- 크롤링 데이터 입력 시 임시 방침: 지금은 어느 기준인지 `description` 텍스트에 명시해두고(예: "직전학기 평점평균 X 이상"), `min_gpa` 필드에는 기존처럼 숫자만 넣는 걸 유지함 — 구조화된 구분은 호성 확인 후 진행.

### 14번: 지자체 장학금의 거주지 세부단위(시/군/구) 매칭 (2026-08-02 발견)

한밭대 크롤링 배치에서 미확인으로 남겨뒀던 지자체 장학금 5건을 재검증하면서 발견: "울산 남구 우듬지인재키움"(울산 남구 거주자만 대상)이나 "익산시 대학생 학자금 이자지원"(익산시 거주자만 대상)처럼, **시/도 전체가 아니라 그 안의 특정 시/군/구 단위로만 자격을 제한하는 지자체 장학금**이 있음. 그런데 `frontend/src/lib/spec.ts`의 `region` 값은 `regionShortName()`을 거치면서 구/군 정보가 사라지고 시/도 단위(예: "울산", "전북")로만 저장됨(`regionShortName` 주석 참고: "region은 구/군 정보 없이 짧은 시/도 단위로만 저장돼 있어서"). 그래서 이런 시/군/구 단위 장학금을 `eligible_region`에 그대로 넣으면(예: "울산") 실제로는 자격이 안 되는 다른 구(중구·동구·북구·울주군)의 울산 거주자한테도 잘못 매칭되는 과다매칭(false positive) 문제가 생김.

- **영향**: 이런 장학금은 `eligible_region`을 비워두면 아예 안 걸러지고(과다노출), 시/도 단위로만 채우면 부정확하게 걸러짐(과다매칭) — 둘 다 틀림.
- **제안(호성 검토 필요, 스키마/프론트 변경 사안)**: `SIDO_LIST`(`frontend/src/lib/regions.ts`)의 구/군 목록을 활용해서 `region` 저장 시 구/군 정보도 유지하도록 바꾸거나, `eligible_region`을 "시/도" 텍스트 하나가 아니라 구조화(시/도+구/군)해서 정확히 비교하는 방식 검토.
- 크롤링 데이터 입력 시 임시 방침: 시/도 전체가 대상인 지자체 장학금(예: 인천·전북 전역)은 `eligible_region`에 시/도 단위 텍스트를 그대로 넣어도 안전하지만, 시/군/구 단위로 좁혀진 장학금(우듬지인재키움·익산시 사례)은 **`eligible_region`을 비워두고 `description`에 정확한 대상 지역을 텍스트로만 명시**하는 걸로 유지(과다매칭보다 과다노출이 덜 해로움 — 사용자가 설명을 읽고 스스로 판단 가능).

---

## 그 외 호성과 논의할 사항 (자격조건 매칭과는 별개)

1. **UserSpec 저장** — 🔶 부분 해결(2026-07-29): 로그인 없이 프론트 `localStorage`에 클라이언트 저장하는 방식으로 일단 재입력 부담은 줄임(`user_spec.py` 주석: "Once auth exists this should move to a real per-user table instead"). 서버 쪽 진짜 계정/프로필 저장은 아직 없음 — 나중에 로그인 도입 여부 결정 필요.
2. **DB에 중복 방지 제약이 없음** — 지금 중복 제거는 `scholarship_dedup_list.md`를 사람이 손으로 대조하는 방식뿐. 대학이 늘어날수록(한밭대·카이스트 이후 계속) 깨지기 쉬움 — `name+provider` 유니크 제약이나 INSERT 전 자동 중복검사를 백엔드에 둘지 논의. **(아직 미해결)**
3. ~~새 필드 추가 시 프론트엔드도 같이 손봐야 함~~ — ✅ 해결(2026-07-29, 대학/단과대/학년/재학상태 드롭다운 있는 스펙 입력 마법사(`frontend/src/app/spec/page.tsx`)로 이미 구현됨).
4. **마감일 자동 정리** (위 표 7번의 연장) — 대학이 늘어나면 이미 넣은 장학금들의 마감이 하나둘 지나갈 텐데, 주기적 재크롤링/정리 계획이 필요한지, 구조화된 deadline 컬럼으로 자동 필터링할지 방향 결정 필요. **(아직 미해결)**
5. ~~한밭대·배재대·목원대·우송대·한남대가 `frontend/src/lib/universities.ts` 대학 드롭다운에 없음~~ — ✅ **해결 확인(2026-08-02)**: 최근 커밋(`e42d0c9`)에서 5개 대학 전부 추가됨(코드 확인 완료).
6. **`data_baejae.sql`·`data_hanbat.sql`의 배치1 행(원래 크롤링 당시 입력분) 중 다수가 컬럼 개수 불일치** (2026-08-02, min_gpa_basis 컬럼 추가 작업 중 우연히 발견) — 두 파일 다 컬럼 헤더는 29개(당시 스키마 기준)를 선언하는데, 실제 각 행의 값 개수를 세어보니 배재대 21건 중 19건, 한밭대 20건 중 19건이 28개 값만 가지고 있음(1개씩 부족). **라이브 DB(Supabase)에는 이미 정상적으로 들어가 있어서 서비스에는 영향 없음** — 문제는 이 두 백업 파일을 그대로 재적재(reseed)하면 "INSERT has more target columns than expressions" 에러가 날 거라는 것. 정확히 어느 값이 어느 행에서 빠졌는지는 확인 안 함(라이브 DB와 대조해서 값을 채워 넣는 감사 작업 필요) — 재적재를 실제로 쓸 일이 생기기 전까지는 급하지 않아서 보류. **(아직 미해결)**

---

## 참고

관련 크롤링 규칙: [supabase/scholarship_dedup_list.md](scholarship_dedup_list.md), [supabase/README.md](README.md)
