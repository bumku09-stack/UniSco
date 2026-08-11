# 매칭 로직 — 해결된 항목 히스토리 (참고용)

이 파일은 `supabase/matching_gaps.md`(지금 논의/미해결 항목만 남기는 파일)에서 **완전히
해결된 항목을 옮겨놓은 히스토리**입니다. 실행되는 코드가 아니라 참고 문서 — 새 태그를
만들기 전에 "이미 비슷한 게 있나?" 확인할 때, 또는 어떤 필드가 왜 지금 이렇게 설계됐는지
찾아볼 때 씁니다.

**흐름**: 새로운 갭 발견 → `matching_gaps.md`에 기록 → 논의해서 방향 결정 → 실제로
구현/반영까지 끝나면 → 그 항목을 통째로 이 파일로 옮기고 `matching_gaps.md`에서는 지움.

마지막 업데이트: 2026-08-11 (자동검사 21개 항목 확대 + 전수 재검증 항목 추가).

---

## 확인된 사실 (backend/app/models/ 코드 기준, 2026-07-30)

`UserSpec`(사용자 입력값): `university`, `college`, `gpa`, `age`, `gender`, `region`, `military_status`, `income_bracket`, `has_disability`, `is_foreigner`, `enrollment_status`, `grade`, `degree_level`.

`scholarship` 테이블에서 실제로 매칭되는 필드(`backend/app/api/match.py`): `min_age`/`max_age`, `required_gender`, `eligible_region`, `required_military_status`, `max_income_bracket`, `min_gpa`, `requires_disability`, `foreigner_eligibility`, `eligible_university`, `eligible_college`, `required_enrollment_status`, `min_grade`/`max_grade`, `required_degree_level`.

## GPA 관련 참고 (혼동 방지용)

`min_gpa`(장학금 쪽 최소학점 조건)는 이미 컬럼도 있고 데이터도 채워지고 있음 — 크롤링 중 등급→GPA 환산 기준을 대학마다 한 번 확정해서 적용 중(예: 충남대 A0=4.0/4.5만점, KAIST는 4.3만점제 별도 환산표 사용).

`UserSpec.gpa`(사용자가 직접 입력하는 값)의 스케일도 ✅ 해결되어 있음 — `backend/app/core/matching.py`의 `normalized_gpa()`가 `UNIVERSITY_GPA_SCALE` 딕셔너리로 대학별 만점 기준을 4.5만점 기준으로 환산한 뒤 비교함(`gpa_matches()`에서 `spec.semester_gpa`/`spec.cumulative_gpa` 둘 다 이 함수를 거침). 대학 추가할 때마다 `UNIVERSITY_GPA_SCALE`도 같이 갱신할 것. **알려진 빈틈**: 서울대학교가 아직 이 딕셔너리에 없음(2026-08-07 id=1105 발견, 급하지 않아 `matching_gaps.md`에 별도로 열어둠).

## 완전히 해결된 조건 목록

| # | 조건 | scholarship 테이블 컬럼 | 해결 내용 |
|---|---|---|---|
| 1 | 소속 대학 | `eligible_university` | ✅ 2026-07-29 — `eligible_university`/`eligible_college` + `UserSpec.university`/`college`로 매칭 |
| 2 | 전공/학과 | `major` | ✅ 2026-08-03 — `UserSpec.department`/`SavedSpec.department` + `major_matches()`로 매칭. 콤마로 여러 학과 나열 지원(하나만 일치해도 통과). 프론트는 대학→단과대→학과 3단 캐스케이딩 드롭다운. 9개 대학 전체 학과 목록 조사+사용자 재확인 완료 |
| 3 | 학년/과정(신입생·재학생, 학부·대학원) | `required_enrollment_status`/`required_degree_level` | ✅ 2026-07-29 — `EnrollmentStatus`/`DegreeLevel` enum + `min_grade`/`max_grade`. 잔여 한계 2건은 `matching_gaps.md` 참고 |
| 4 | 사용자 GPA 입력 스케일 검증 | (UserSpec.gpa 자체) | ✅ 위 GPA 참고 항목 |
| 7 | 마감일(구조화된 날짜) | `application_deadline` | ✅ 구조 완성(2026-08-03) — `deadline_matches()`로 마감 지나면 자동 제외. 신규 크롤링 건은 확정 마감일 있으면 채우는 게 원칙 |
| 9 | 특수상황 신분(다문화가정·아동양육시설 생활자/퇴소자·학생자치단체 임원 등) | `required_special_status` | ✅ 2026-08-03 — `SpecialStatus` enum + TEXT[] 다중선택. 매칭 로직은 다른 필드와 다름(아래 "특수상황 매칭 로직" 참고) |
| 10 | 외국어 시험 점수(TOPIK/IELTS/TOEIC 등) | `language_test_type`/`language_test_min_score` | ✅ 2026-08-03 — `LanguageTestType` enum + 점수 컬럼, 시험 종류까지 정확히 일치해야 함 |
| 11 | 학교 자체 비학점(비교과) 프로그램 이수 조건 | 없음 | ✅ 필터링 대상 아님으로 확정(2026-08-01, 사용자 결정) + 랭킹 페널티(`extracurricular_program_condition`, 운영 DB 8건) |
| 12 | 장애인 세부 유형 | `required_disability_type` | ✅ 2026-08-03 — `DisabilityType` enum(7종) + `disability_type_matches()` |
| 13 | GPA "직전학기" vs "전체(누적)" 기준 구분 | `min_gpa_basis` | ✅ 2026-08-02 컬럼 추가, 2026-08-03 "둘 다 동시 충족" 변형까지 `GpaBasis.BOTH`로 커버 |
| 14 | 지자체 장학금의 거주지 세부단위(시/군/구) | `eligible_region` | ✅ 2026-08-05 — `district`/`parent_district` 추가, `region_matches()`가 4개 후보 OR 검사 |
| 19 | "본인 또는 부모 중 1인이 OO에 거주" | `eligible_region` | ✅ 2026-08-05 — `parent_region` 추가, `region_matches()`가 본인/부모 거주지 OR 매칭 |

### 9·10·12번(어학점수/장애인유형/특수상황) + 9번 OR복합조건 — ✅ 2026-08-03 전체 구현 완료

세 항목 모두 `SavedSpec`/`Scholarship`에 컬럼 추가 완료, `core/matching.py`의 `language_test_matches()`/`disability_type_matches()`/`special_status_matches()`로 매칭됨. 장애인 세부유형은 Scholarships.com "Physical Disabilities" 7종 채택(`physical_impairment`/`learning_disability`/`medical_disability`/`mental_impairment`/`muscular_dystrophy`/`developmental_impairment`/`disabled_parent` — 마지막 값은 본인이 아니라 부모 장애 케이스). 특수상황은 다중선택(`north_korean_defector`/`multicultural_family`/`child_care_facility`/`student_council_officer`/`single_parent_family`/`grandparent_family`/`multi_child_family`/`national_merit`).

**OR로 묶인 복합조건 장학금**(배재사랑·희망복지·장학사정관·봉사공로, 2026-08-03): `required_special_status`를 단일값→리스트로 바꿔서 4건 재분류. 장애+특수상황이 함께 걸린 배재사랑장학금은 `is_eligible()`에서 둘을 OR로 처리(leniency 예외 없는 `special_status_matches_strict()` 사용). 장학사정관·봉사공로는 일부 세부조건(부모 장애, 활동이력처럼 담을 필드 자체가 없는 것)이 구조화 안 되고 `description` 텍스트로만 남음.

(부모 장애 UI 미해결 갭은 `matching_gaps.md`로 이동)

### 특수상황 매칭 로직 (2026-08-02, 사용자 확정 — 다른 필드들과 다른 예외 규칙)

다른 필드(성별·나이·GPA 등)는 전부 "장학금에 조건이 있으면, 유저가 그 조건에 안 맞을 때 제외" 방식임. **특수상황은 이거랑 다르게, "유저가 특수상황을 아예 선택 안 했으면 애초에 걸러내지 않는다"는 예외 규칙**을 사용자가 명시적으로 요구함:

- **유저가 특수상황을 하나도 선택 안 함** → 특수상황 조건이 걸려있는 장학금도 걸러내지 않고 그냥 다 보여줌 (마치 특수상황 필드 자체가 없는 것처럼 동작).
- **유저가 특수상황을 1개 이상 선택함** → 그때부터 특수상황 조건이 걸려있는 장학금만 필터링 시작: 유저가 선택한 항목과 장학금이 요구하는 항목이 일치하면 보여주고, 안 맞으면 제외. **특수상황 조건이 아예 없는 일반 장학금은 이 필터링과 무관하게 계속 다 보임.**

**이유(사용자 설명)**: 특수상황은 선택 항목(옵션)이라 안 누른 학생이 많을 텐데, "안 눌렀다"는 게 "나는 특수상황 대상자가 아니다"를 확정하는 게 아님 — 그냥 아직 대답 안 한 것뿐. 그런데 표준 방식대로 처리하면, 실제로는 다문화가정인 학생이 그 항목을 안 눌렀다는 이유만으로 다문화가정 전용 장학금이 안 보이게 될 수 있음 — 그건 잘못된 결과. 그래서 "선택 안 함 = 모르는 것 = 걸러내지 않음", "선택함 = 그 항목 기준으로만 좁힘"으로 설계함.

실제 구현(`backend/app/core/matching.py`) — `required_special_status`가 리스트라 "장학금 쪽 여러 특수상황 중 하나 + 유저 쪽 여러 특수상황 중 하나"가 겹치는지 보는 형태:
```python
def special_status_matches(scholarship_special_status: list[SpecialStatus], spec_special_status: list[SpecialStatus]) -> bool:
    if not scholarship_special_status:
        return True  # 특수상황 조건 없는 일반 장학금 — 항상 통과
    if not spec_special_status:
        return True  # 유저가 특수상황 아예 안 눌렀음 — 그래도 걸러내지 않음
    return bool(set(scholarship_special_status) & set(spec_special_status))  # 하나라도 겹치면 통과
```
`is_eligible()`에는 이 표준 버전 대신, 장애 조건과 OR로 묶일 때만 "안 누르면 통과" 예외가 없는 `special_status_matches_strict()`를 씀(위 "9·10·12번" 참고) — 안 그러면 `has_disability=False`처럼 이미 확실한 "아니오" 답이 있어도 특수상황 쪽 예외 때문에 OR 전체가 사실상 항상 True가 돼버림.

**참고(2026-08-07, 특수상황 다중선택 관련 후속)**: "다문화가정 이면서 동시에 저소득이어야 함" 같은 **AND** 조건은 이 매칭 로직으로 표현이 안 됨(위 로직은 OR 전용) — `matching_gaps.md`에 미해결 항목으로 열어둠(`special_status_match_all` 플래그 추가 방향으로 논의 중). 또한 특수상황을 아무것도 선택 안 한 학생을 위한 **"해당사항 없음"** 옵션도 2026-08-07 추가됨 — `SpecialStatus.NOT_APPLICABLE`을 선택하면 실제로 어떤 장학금의 `required_special_status`에도 절대 걸리지 않는 값이라(매칭 로직 변경 없이) 특수상황 게이트가 있는 장학금이 자연스럽게 전부 제외됨.

### 2번 후속: 학과(department) 데이터 — ✅ 2026-08-03 완료

`frontend/src/lib/universities.ts`의 `CollegeInfo.departments`로 대학→단과대→학과 3단 구조 구현, `/spec`·`/mypage` 둘 다 연결 완료, 백엔드 매칭(`major_matches()`)도 동작함. 9개 대학(을지대 제외) 전체 학과 목록을 병렬 조사 + 사용자 직접 재확인까지 마쳐서 확정함(자동 조사와 실제 화면이 다를 때는 사용자가 직접 대학 공식 페이지를 열어 확인한 결과가 최종 기준). 학과가 없는 게 맞는 조직(배재대 주시경교양대학/아펜젤러공유대학, 목원대 스톡스대학, 충남대 법학전문대학원·의학전문대학원 등 교양/융합/단일과정)은 빈 배열 유지가 정상.

### 3번 후속(일부): 법학전문대학원(로스�uk) 계열 — ✅ 부분 해결 (2026-07-31)

`universities.ts`에 `법학전문대학원`/`의학전문대학원` 추가, 로스쿨 장학금 4건은 `eligible_college`로 좁혀서 처리. `required_degree_level`은 JD/MD-PhD 전용 값이 없어 근사 처리(`eligible_college`로 이미 좁혀지므로 결과적으로 문제없음) — 정식 enum 값 추가는 호성과 논의 필요(급하지 않음).

(나머지 3번 후속 2건 — 학부/대학원 동시 대상 표현 불가, 대학원생 휴학 상태 표현 불가 — 는 `matching_gaps.md`로 이동)

### 13번: GPA "직전학기" vs "전체(누적)" 구분 — ✅ 2026-08-02 구현, 2026-08-03 "둘 다" 변형까지 완료

`scholarship.min_gpa_basis`(`GpaBasis` enum)로 `semester`/`cumulative`/`both`/NULL(미지정, 관대한 기본값) 4가지를 구분함. `UserSpec`/`SavedSpec`도 `semester_gpa`/`cumulative_gpa` 두 칸으로 나눠서 받음. 을지대 "차세대의료인장학금"(id 316, 둘 다 동시 충족)이 `both` 값의 계기가 됨.

### 14번: 지자체 장학금의 거주지 세부단위(시/군/구) 매칭 — ✅ 2026-08-05 해결

`region`은 `regionShortName()`을 거치며 구/군 정보가 사라져 시/도 단위(예: "울산")로만 저장됐음 — 시/군/구 단위로 좁혀진 지자체 장학금을 그대로 매칭하면 과다매칭 위험이 있어 그동안 `eligible_region`을 비워두는 임시방침(과다노출)으로 버텨왔음.

**해결**: `SavedSpec`/`UserSpec`에 `district`(본인)·`parent_district`(부모) 추가. `region_matches()`가 본인 시/도·본인 시/군/구·부모 시/도·부모 시/군/구 4개 후보를 OR로 검사(부분 문자열 매칭). **구현 중 발견한 버그**: 빈 문자열(세종처럼 하위 구/군이 없는 경우 기본값)을 후보에 그대로 넣으면 파이썬의 `"" in "아무거나"`가 항상 True라서 지역 필터링이 통째로 무력화되는 심각한 버그였음 — 빈 문자열은 후보에서 제외하도록 방어 코드 추가, synthetic 테스트로 회귀 확인함.

366건 전체를 재검색해서 정읍시민장학재단·화성시인재육성재단 소상공인 장학금 2건의 `eligible_region`을 "정읍시"/"화성시"로 채움. 프론트는 `/spec`·`/mypage` 둘 다 부모 거주지역 UI를 본인과 동일한 시/도+구/군 캐스케이딩 드롭다운으로 구현. 기존 랭킹 전용 태그 `sub_region_residence_condition`(18번)은 이제 자격 필터링 자체가 되므로 용도 소멸.

**2026-08-07 후속 버그 수정**: "중구"처럼 여러 시/도(서울·부산·대구·인천·대전·울산)에 동시에 있는 구/군 이름은 시/도 확인 없이 부분 문자열로만 비교하면 완전히 다른 도시 사용자에게도 걸림(실사용자가 직접 발견 — 대전 중구 거주자한테 "인천광역시 중구" 한정 장학금이 뜸). `region_matches()`를 수정 — eligible_region 안에 시/도 이름이 박혀 있으면, 구/군 후보가 매칭되더라도 사용자의 시/도가 그 시/도와 일치하는지까지 추가로 확인하도록 변경. 기존 컨벤션(시/도 이름 없는 bare 구/군 이름, 예: "정읍시")은 영향 없음 — unit 테스트 8건 + 실제 `/match` API 4건으로 회귀 확인함.

### 18번: 매칭적합도순 재설계 + "확인 불가 조건" 랭킹 페널티 — ✅ 2026-08-04 완료

기존 랭킹(`specificity_score()`)이 "학생과 얼마나 잘 맞나"가 아니라 "장학금이 조건을 얼마나 많이 걸었나"로 순위를 매기고 있던 문제(사용자 지적)를 고침.

**랭킹 공식 교체** (`backend/app/core/matching.py`): `confirmed_match_count()`로 교체 — 나이/성별/거주지/병역/GPA/장애/외국인여부/전공/대학/단과대/재학상태/학년/학위과정 13개는 항상 세지만, 소득분위·어학점수·특수상황 3개는 학생이 실제로 값을 입력했을 때만 셈. 새 정렬 키 `personal_fit_key()` = `(ratio, confirmed)` 내림차순, `ratio = confirmed / (confirmed + unverifiable)`.

**"확인 불가" 태그 8개 추가** (`SpecialStatus` enum, 기존 `required_special_status` 컬럼 재사용, 학생은 절대 선택 불가 — 크롤링 데이터 전용): `parent_occupation_condition`·`religious_or_career_intent_condition`·`sub_region_residence_condition`·`hometown_school_region_condition`·`suneung_score_condition`·`school_record_condition`·`credit_requirement_condition`·`extracurricular_program_condition`. 노출 정책(과다노출)은 안 바뀌고 순위만 밀림.

**데이터(2026-08-04 기준)**: 운영 DB 366건 중 82건 태그 완료(credit 24·suneung 18·parent_occupation 16·religious 14·extracurricular 8·school_record 7·hometown_school_region 1·sub_region 0). 이후 3차 배치(2026-08-07)에서 `righteous_person_family_condition`(20번) 태그도 추가됨.

**어학점수 버그**: `language_test_matches()`가 "안 넣음"과 "다른 시험 넣음"을 구분 못 하고 둘 다 탈락시키던 버그도 같이 수정(안 넣으면 이제 정상 통과).

**같은 날 후속 수정**: `unverifiable_condition_count()`가 처음엔 `spec`을 안 받아서, 학생이 특수상황을 안 골랐는데 그 조건 걸린 장학금이 감점 없이 상단에 뜨는 회귀가 있었음(북한이탈주민 장학금이 계속 상위 노출되는 걸 사용자가 발견) — `spec`도 받게 고쳐서 소득분위/특수상황/어학점수 미입력 시에도 8개 확인불가 태그와 동일하게 감점 대상에 포함시킴.

### 19번: "본인 또는 부모 거주지" OR 조건 — ✅ 2026-08-05 발견 및 해결

지자체 장학금은 "본인 또는 부모 중 1인이 OO에 거주"처럼 부모 주소지 기준으로도 자격이 되는 OR 조건인 경우가 대부분인데, 기존 로직은 `spec.region`(본인 거주지)만 봐서 부모님만 해당 지역에 사는 학생이 과소매칭되는 문제가 있었음.

**해결**: `SavedSpec`/`UserSpec`에 `parent_region`(선택 입력) 추가, `region_matches()`만 "본인 거주지 OR 부모 거주지"로 확장. `parent_region` 안 넣으면 기존과 동일하게 본인 거주지만 판단 — 랭킹 페널티 대상 아님.

시/도 단위로 지역 조건 걸린 스콜라십 전체(346건)에 일괄 적용. 상세는 `SCHEMA_DECISIONS.md` 2026-08-05 항목 참고.

### 소득기준 "중위소득 N% 이하" → 학자금지원구간 변환 — ✅ 2026-08-06~07 해결

3차 배치 25개 기관 조사 중 상당수(전남·영암군·영광군·제주도 등)가 소득 조건을 "학자금지원구간"이 아니라 "중위소득 N% 이하"로 표기하는 걸 발견. 한국장학재단이 공식 발표하는 구간별 중위소득% 경계값을 확인해서 변환표를 만들고(2026년 기준: 1구간≤30%, 2≤50%, 3≤70%, 4≤90%, 5≤100%, 6≤130%, 7≤150%, 8≤200%, 9≤300%, 10=초과), 3차 배치(227건)에 적용해서 `max_income_bracket`을 채움(보수적으로 반올림 내림 처리 — 과다매칭 방지). 경계값을 확실히 못 찾는 경우는 지금처럼 빈칸 유지.

### 그 외 해결된 사항

- **새 필드 추가 시 프론트엔드도 같이 손봐야 함** — ✅ 해결(2026-07-29, 대학/단과대/학년/재학상태 드롭다운 있는 스펙 입력 마법사(`frontend/src/app/spec/page.tsx`)로 이미 구현됨).
- **한밭대·배재대·목원대·우송대·한남대가 대학 드롭다운에 없음** — ✅ 해결 확인(2026-08-02): 커밋 `e42d0c9`에서 5개 대학 전부 추가됨.

### 2026-08-07 전수 재검증 1단계 — ✅ 완료

662건 전체를 12개 청크로 나눠 병렬 조사 에이전트 12개가 각자 담당분을 description 재추출 + 필요시 `application_url` 원문 대조. 약 150개 장학금에서 문제 발견. "확신도 높음 + 기존 컬럼 값만 채우면 되는" 64건을 `supabase/tools/fix_batch_2026-08-07.py`로 일괄 반영(headcount 5건/min_credits 8건/min_grade·max_grade 8건/application_deadline 7건/특수상황 태그 9건/major 4건/degree_level 단일값 한계 완화 4건 등). `/match` API로 샘플 검증 완료.

**1단계 반영 직후 실사용자가 직접 발견한 추가 버그 2건 — 즉시 수정 완료**:
1. **id=666 KT디지털인재 장학생** — `major`가 NULL이라 ICT 무관 전공자에게도 노출되던 것을 수정(컴퓨터공학과/소프트웨어학과/인공지능학과/데이터사이언스학과/정보통신공학과/전자공학과로 채움).
2. **"구/군 이름 충돌" 로직 버그** — 위 14번 섹션의 "2026-08-07 후속 버그 수정" 참고.

이번 재검증에서 만들어진 감사 도구(계속 재사용): `supabase/tools/description_gap_check.py`(판정 규칙 공용 함수), `supabase/tools/audit_description_gaps.py`(규칙 기반 스캔), `supabase/tools/batch_validation.py`(새 배치 하드 게이트), 로컬 전용 슬래시 커맨드 `/검증해`·`/돌아봐`.

## description에 섞여 들어간 내부 메모 정리 + 그 김에 발견한 구조화 필드 공백 9건 (2026-08-10)

**문제**: `description`(사용자한테 그대로 보이는 상세 설명)에 "min_gpa로 표현 불가", "구조화된
필드로 매칭 불가", "matching_gaps.md 9번 참고" 같은 저희끼리 쓰는 내부 개발 메모가 그대로
섞여 노출되고 있었음(662건 중 30건). 별도로 "2026-08-02 재검증(2018학년도 정시모집요강
공식 자료로 확인): " 같은 날짜 찍힌 검증 로그 프리픽스도 섞여 있었음(29건, 주로 한남대
배치). 두 문제 합쳐 유니크 52건 — 그중 47건은 실제 조건 설명은 그대로 두고 내부 메모/로그
문구만 잘라내는 방식으로 `supabase/tools/fix_description_notes_2026-08-10.py`로 dry-run→
승인→반영 완료. 나머지 5건은 메모 자체가 "이 장학금이 지금도 실제로 존재하는지 확신 못 함"
이라는 내용이라 텍스트만 지우면 안 되고 원문 재확인이 먼저 필요 — `matching_gaps.md`
"존재 자체가 불확실한 한남대 장학금 5건"으로 이동.

**사용자 질문("빈칸들 다 채워넣은거야?")에서 파생된 후속 작업**: 텍스트만 지운 47건을
`description_gap_check.py`의 `find_gaps()`로 다시 돌려서 구조화 필드 공백이 있는지 확인함.
24건에서 걸렸는데 대부분(15건)은 이미 알려진 스키마 한계(시험 종류가 여러 개라 단일 필드로
OR 표현 불가, GPA 등급별 차등 지급이라 "합격 커트라인" 개념 자체가 아님 등)라 추측으로 안
채움(CLAUDE.local.md 원칙: "확신 안 서면 빈칸 < 틀린 값"). 원문에 값이 명확히 있는데 진짜
빈칸이었던 9건만 `supabase/tools/fix_structured_gaps_2026-08-10.py`로 반영:
- id=166 영어성적우수장학금: `language_test_type`='TOEIC', `language_test_min_score`=900
- id=232 기초생활수급자·차상위계층장학금(한남대): `required_special_status`에
  `basic_livelihood_recipient`/`near_poor` 추가
- id=244/245/251 (한남대 미술·모의UN·문학 우수자장학금): `headcount`에 원문의 등수별
  선발인원 그대로 채움
- id=253 인천 청년 해외배낭연수 장학생: `application_period`에 남아있던 "확인 필요"
  플레이스홀더 문구를 정리된 문장으로 교체
- id=266 장학사정관장학금(대전대): `required_special_status`에 `disabled_parent` 추가
  (원문의 "희망장학금(부모 중 장애등급 1~3급)" 항목이 누락돼 있었음)
- id=302 학업성적우수장학금(을지대): `min_gpa`=2.0, `min_credits`='12학점'
- id=309 중증장애인자녀장학금(을지대): `required_special_status`에 `disabled_parent` 추가

---

## 전공 "제외" 조건 + 특수상황 "AND" 조건 (2026-08-10)

**전공 제외 조건**: `Scholarship`에 `excluded_major: str | None` 컬럼 추가(기존 `major`와 동일한
콤마/가운뎃점 구분 컨벤션). `major_matches()`(`backend/app/core/matching.py`)에서 이 필드를
최우선으로 체크 — 학생 학과가 `excluded_major` 목록에 있으면 `major` 포함 목록 체크와 무관하게
무조건 탈락. id=257(대전대 특별장학금, "한의예과·군사학과 제외")·id=1134(계통대학교장학금,
"신학과 제외")에 적용 완료.

**특수상황 AND 조건**: 원래 계획했던 `special_status_match_all: bool` 단순 On/Off 스위치 방식은
실제 사례(id=1019)를 다시 보니 틀린 설계였음 — "다문화가정 이면서 (기초수급자 또는 차상위)"는
전체를 AND로 보면 "기초수급자이면서 동시에 차상위"를 요구하는 꼴이 돼서 아무도 못 걸림(두 상태는
동시에 있을 수 없음). 그래서 설계를 바꿔서 `required_special_status_all: list[SpecialStatus]`
(전부 다 있어야 함, AND) 컬럼을 기존 `required_special_status`(하나만 있어도 됨, OR)와
별개로 신규 추가. `special_status_all_matches()` 함수로 독립적으로 체크하고, 기존 장애 조건과의
OR 분기(`disability_matches() or special_status_matches_strict()`)와는 별도로 항상 추가
AND 조건으로 적용. 재검증 결과 원래 "3건(id=1019/1046/1052)"이라던 것도 실제로는:
- id=1019(영암군 다문화가정학생장학금): `required_special_status_all=[multicultural_family]`,
  `required_special_status=[basic_livelihood_recipient, near_poor]`로 정확히 표현됨.
- id=1052(북한이탈주민 장학생, 인천): 원문 "북한이탈주민가정의 자녀로 가정형편(기초수급/
  차상위/장애인등록 중 1개 이상)"도 같은 AND+OR 구조라 동일하게 적용
  (`required_special_status_all=[north_korean_defector]`,
  `required_special_status=[basic_livelihood_recipient, near_poor, single_parent_family]`,
  `requires_disability=True`로 "장애인등록" 옵션은 기존 장애-특수상황 OR 분기가 자동으로 흡수).
- id=1046(인천 희망드림장학금)은 원문에 "(OR조건)"이라고 명시돼 있어 애초에 AND 대상이
  아니었음 — 대신 소득분위·특수상황·장애가 3개의 다른 매칭 메커니즘에 걸쳐 OR로 묶여야 하는
  전혀 새로운 유형의 한계를 발견함, `matching_gaps.md`에 새 항목으로 기록.

**id=964 음성군 해외장학생 삭제**: "Times Higher Education 세계 100대 대학 재학생 또는
입학예정자(해외 대학 한정)"만 대상 — 국내 대학생 대상 서비스 취지와 안 맞아 사용자 최종
확인 후 `DELETE FROM scholarship WHERE id=964` 실행 완료.

**코드/데이터 검증**: `major_matches()`/`special_status_all_matches()`를 DB 레코드로 직접
단위 테스트(한의예과/간호학과 스펙으로 id=257, 다문화가정 조합별 스펙으로 id=1019/1052) —
전부 의도대로 동작 확인. 기존 OR 방식 장학금(배재사랑장학금 등)도 `required_special_status_all`
기본값(빈 리스트)이라 기존 동작 그대로 유지되는 것까지 회귀 확인.

## 자동검사 21개 항목으로 확대 + 전체 662건 재검증 (2026-08-11)

### 배경 — "확실치 않음, 필요시 재확인" 금지 원칙 확정

세션 시작에 사용자가 "확실치 않으면 나중에 재확인" 이라는 중간 상태를 없애기로 확정
(`data_collection_guide.md` 절대규칙 4번 강화) — 애매하면 그 자리에서 더 찾아보고, 조사를
끝낼 땐 반드시 "확정값" 아니면 "충분히 찾아봤는데 원문에 없다고 확인된 빈칸" 둘 중 하나여야
함. 문장을 뜯을 때도 "이건 무슨 조건이지?"를 스스로 물으며 확인하도록 규칙 3번도 강화(같은
날). 이걸 실제로 적용해본 게 이번 섹션 전체.

### `description_gap_check.py` 10개 → 21개 체크리스트 항목으로 확대

기존엔 major/min_gpa/max_income_bracket/disability/foreigner_eligibility/language_test_type/
enrollment_or_degree/amount/headcount/period_or_deadline 10개만 자동검사했음 —
특수상황/전공제외/석박사구분/거주지/성별/병역/나이/이수학점/입학성적 8개는 자동검사가
아예 없었음. 이번에 21개(체크리스트 전체) 커버하도록 `FIELD_GAP_RULES`를 확장하고,
"차상위"/"기초생활수급자" 같은 특수상황성 키워드가 엉뚱하게 `max_income_bracket` 규칙에
걸려있던 매핑 오류도 같이 고침(→ `special_status` 규칙으로 이동). `batch_validation.py`가
이 파일을 그대로 상속하므로 새 배치는 자동으로 21개 항목 다 검사받음.

### 662건 전체 재스캔 → 항목별로 하나씩 원문 대조 → 실제 반영

늘어난 검사로 662건을 다시 스캔해서 총 178건(항목별 중복 포함)이 걸림 — 건수 많은 순서대로
하나씩 사람이 원문 대조(각 필드마다 "실제 조건 있는데 빠짐" vs "구조적으로 표현 불가라
정당하게 빈칸"을 구분). 실제 반영된 것:

- `min_credits`(이수학점): 38건 전부 실제 조건 있음 → 전부 채움(오탐 0건)
- `min_gpa`(성적): 29건 중 16건 채움. 13건은 정당한 빈칸(등수/석차 조건, 백분위·자체지수
  기준이라 4.5만점 환산 불가, 향상폭 조건, GPA 구간별 차등지급이라 단일 커트라인 없음 등)
- `amount`(지급금액): 28건 중 9건 채움(범위는 낮은 쪽 숫자로, "등록금 전액+부수적 소액"
  구조는 부수적 소액만 넣으면 오히려 작아 보이므로 안 채움). 19건은 다중 트랙이라 안 채움
- `required_special_status`(특수상황): 26건 중 5건 반영(필수조건 4건 + 아래 신규 "제외"
  기능 1건). 21건은 "우선순위/가산점"이라 필수조건 아님, 또는 이미 `max_income_bracket`으로
  커버됨 — required_special_status에 넣으면 오히려 필터가 더 좁아지는 경우들
- 나머지 카테고리(선발인원/입학성적/소득분위/장애/외국인/나이/전공제외/신청기간): 25개 칸,
  21개 레코드 반영. `language_test_type`(11건, 시험종류가 여러 개라 단일 필드로 OR 표현
  불가)과 `degree_level`(5건, 전부 "석사/박사/석박사통합 다 됨"이라 오히려 빈칸이 정답)은
  전부 정당한 빈칸으로 확인, 0건 반영

**부수적으로 발견한 버그 2건**:
1. **id=266/309 "부모님 장애" 조건이 엉뚱한 칸에**: `required_special_status`에
   `DisabilityType` 전용 값인 `disabled_parent`가 잘못 들어가 있어서(SpecialStatus 열거형에
   없는 값이라 절대 매칭 안 됨) `requires_disability`+`required_disability_type`으로 옮김.
2. **id=1058 청소년육성기금(제주)**: "장애인 가족의 자녀" 조건도 같은 방식(`disabled_parent`)
   으로 정확히 표현하도록 채움.
3. **admission_score_condition(입학성적) 필드 오용 7건**(21, 22, 75, 76, 173, 522, 688):
   "내신/입학성적"(입학 당시 조건) 전용 칸에 **재학 중 성적 유지 조건**이 잘못 들어가 있던
   것 발견(사용자가 "성취장학금" 상세페이지에서 지적) — `min_gpa`로 이미 정확히 변환된 4건은
   중복이라 지움, 나머지 3건(4.5만점 환산 불가)도 잘못된 이름표라 지움(원문 정보는
   description에 이미 있어서 정보 손실 없음).

### 특수상황 "제외" 조건 신설 — `excluded_special_status`

id=952 "청년밥상"(우양재단)에서 "2026년부터 자립준비청년·북한이탈주민은 지원 대상에서
제외(과거엔 우대 대상)"라는, 지금까지 없던 **배제 방향** 조건을 발견(`required_special_status`는
"포함"만 표현 가능). `excluded_major`와 동일한 컨벤션으로 `Scholarship.excluded_special_status:
list[SpecialStatus]` 신규 컬럼 추가 + `backend/app/core/matching.py`에
`excluded_special_status_matches()` 함수 추가(학생이 그 태그를 선택했으면 탈락, 안 선택했거나
아예 특수상황을 안 골랐으면 통과 — 단위 테스트로 3가지 경우 다 확인). id=952에 적용 완료.

### 내부 메모/원시 데이터 잔존 재정리 (2026-08-10 작업에서 빠진 것들)

- **내부 조사 메모 24건 추가 삭제**: 관정재단 학부·대학원장학생(⚠️충남대/KAIST 참여 확인...
  나머지 9개 대학 미확인) 포함, 2026-08-10 정리 때 빠졌던 것들. "존재 불확실 한남대 5건"도
  description의 내부 메모는 삭제(존재 여부 자체는 여전히 미해결, `matching_gaps.md` 참고).
- **"해당 없음" 플레이스홀더 104건 → NULL**: `min_credits`/`admission_score_condition`에
  "해당 없음"이라는 문자열이 실제 값처럼 들어있어서 상세페이지에 "이수학점 · 해당 없음"
  같은 무의미한 줄이 뜨던 문제. `description_gap_check.py`의 플레이스홀더 목록에도
  "해당 없음"/"제한 없음" 추가해서 앞으로 자동으로 잡히게 함.
- **description "[지원금액] X / [비고] Y" 원시 형태 73건 → 자연스러운 문장으로**: 가장 초기
  CNU 배치(id 1~71 등)가 스프레드시트 칸 이름이 그대로 남은 상태였음(사용자가 id=63
  "학군사관후보생 해외연수 장학금"에서 발견). 정보는 그대로 두고 문장만 자연스럽게 정리,
  순수 내부 메모(예: "표에 포함할지는 호성과 상의 필요")는 같이 삭제. **재발 방지**:
  `description_gap_check.py`에 `find_bracket_label_leak()` 신규 — description이 대괄호+한글
  단어로 시작하면 걸리도록 해서, `batch_validation.py` 하드게이트에도 자동 편입.

### 프론트엔드 — 상세페이지 지원조건 표시 개선

- **"자격조건"+"참고조건" 두 섹션 → "지원조건" 하나로 통일**: "참고조건"이라는 이름이 덜
  중요한 정보처럼 보인다는 지적 반영.
- **`major`(전공) 표시 버그 수정**: 실제로는 `major_matches()`가 필터링에 쓰고 있는데
  프론트 `eligibilityParts()`에는 빠져있어서 "필터 미반영" 쪽에 잘못 표시되고 있었음 — 정식
  필터링 목록으로 이동.
- **점 색깔 구분(파란/노란) 추가**: 시스템이 실제로 거르는 조건(파란 점)과, 학생 프로필에
  입력칸 자체가 없어 시스템이 확인 못 하는 조건(이수학점·입학성적, 노란 점)을 구분.
  로그인 여부와 무관하게 항상 같은 규칙 — 매칭 로직이 이미 "안 맞으면 애초에 안 보여준다"를
  보장하므로 별도 학생별 비교 로직 불필요(사용자 아이디어).
- **"확인 불가" 특수상황 태그의 원본 값 노출 버그 수정**: `parent_occupation_condition`
  같은, 학생이 선택할 수 없는 태그가 상세페이지에 영어 원본 그대로("parent_occupation_
  condition") 노출되고 있었음 — 한글 라벨 7개 추가 + 이 태그들은 노란 점으로 분리(학생이
  확인할 방법이 없는 조건이라는 걸 색깔로도 표시).
- **장학금 소개 가독성 개선**: description이 줄바꿈 없이 한 문단으로 이어붙어 있어서 문장
  경계(마침표+공백)마다 자동으로 줄을 나눠 표시하도록 변경("2.5/4.5" 같은 소수점은 안 쪼개짐
  확인).

관련 커밋: `feat/similar-recommendations-and-income-bracket` 브랜치, PR #9
(https://github.com/hoseongdev/UniSco/pull/9) 이어서 진행 중.

## 참고

미해결/논의 필요 항목은 [supabase/matching_gaps.md](matching_gaps.md) 참고.
관련 크롤링 규칙: [supabase/scholarship_dedup_list.md](scholarship_dedup_list.md), [supabase/README.md](README.md), [supabase/data_collection_guide.md](data_collection_guide.md)
