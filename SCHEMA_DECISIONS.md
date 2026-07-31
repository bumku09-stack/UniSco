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

관련 문서: [supabase/matching_gaps.md](supabase/matching_gaps.md) (매칭 로직 미지원 자격조건 목록), [supabase/README.md](supabase/README.md)

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
