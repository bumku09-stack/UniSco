# 매칭 로직 미지원 자격조건 목록 (호성 전달용)

이 파일은 실행되는 코드가 아니라, `scholarship` 테이블에는 크롤링으로 계속 데이터가 쌓이는데 백엔드 매칭 로직(`backend/app/models/user_spec.py`의 `UserSpec`)이 아직 걸러내지 못하는 자격조건을 놓치지 않고 기록해두는 목록입니다.

**규칙: 크롤링하다가 아래 표에 없는 새로운 미지원 조건이 나오면 이 파일에 바로 추가할 것.**

마지막 업데이트: 2026-07-26

---

## 확인된 사실 (backend/app/models/ 코드 기준)

`UserSpec`(사용자 입력값)은 8개 필드뿐: `age`, `gender`, `region`, `military_status`, `income_bracket`, `gpa`, `has_disability`, `is_foreigner`.

`scholarship` 테이블에서 이 8개와 실제로 매칭되는 필드: `min_age`/`max_age`, `required_gender`, `eligible_region`, `required_military_status`, `max_income_bracket`, `min_gpa`, `requires_disability`, `foreigner_eligibility`.

나머지 필드(`grade_level`, `major`, `affiliated_institution`, `min_credits`, `admission_score_condition`, `headcount`, `application_period`)는 **컬럼은 있지만 매칭 로직에서는 전혀 안 쓰임** — 크롤링할 때 값은 채워 넣고 있으나 실제 필터링에는 반영 안 됨.

## GPA 관련 참고 (혼동 방지용)

`min_gpa`(장학금 쪽 최소학점 조건)는 **이미 컬럼도 있고 데이터도 채워지고 있음** — 크롤링 중 등급→GPA 환산 기준을 대학마다 한 번 확정해서 적용 중(예: 충남대 A0=4.0/4.5만점, KAIST는 4.3만점제 별도 환산표 사용). 이건 갭이 아님.

진짜 갭은 **`UserSpec.gpa`(사용자가 직접 입력하는 값)의 스케일이 정의·검증되지 않는다는 것**: 4.5만점제 학교 학생과 KAIST처럼 4.3만점제 학교 학생이 서로 다른 기준으로 숫자를 넣어도 시스템이 구분 못 함 → 아래 표 4번.

## 매칭 안 되는 자격조건 목록

| # | 조건 | scholarship 테이블 컬럼 | 상태 |
|---|---|---|---|
| 1 | 소속 대학 | `affiliated_institution` | 컬럼 있음(텍스트), 매칭 로직 없음 — UserSpec에 대학 입력 자체가 없음 |
| 2 | 전공 | `major` | 컬럼 있음(텍스트), 매칭 로직 없음 |
| 3 | 학년/과정(신입생·재학생, 학부·대학원) | `grade_level` | 컬럼 있음(텍스트), 매칭 로직 없음 — **아래 "3번 상세" 참고, 필드 자체를 분리하는 게 확정 방향** |
| 4 | 사용자 GPA 입력 스케일 검증 | (UserSpec.gpa 자체) | 대응 컬럼/필드 없음 — 스케일 정보를 받을 방법이 없음 |
| 5 | 이수학점 | `min_credits` | 컬럼 있음(텍스트), 매칭 로직 없음 |
| 6 | 입학성적(수능/내신) 조건 | `admission_score_condition` | 컬럼 있음(텍스트), 매칭 로직 없음 |
| 7 | 마감일(구조화된 날짜) | `application_period`(텍스트만) | 구조화된 date 컬럼 자체가 없음 → DB에 넣은 뒤 마감이 지나도 자동으로 안 빠짐 |
| 8 | 선발인원 | `headcount` | 컬럼 있음(텍스트), 매칭/정렬에 활용 안 됨 |

### 3번 상세: `grade_level` 필드 분리 (확정 방향)

지금 `grade_level` 하나에 서로 다른 두 개념이 섞여 있음:
- **재학 상태**(입학·재학 시점 기준): 신입생 / 재학생 / 휴학생 / 졸업생
- **과정 단계**: 학부 / 석사 / 박사 (크롤링 데이터에 "석·박사통합과정"처럼 통합과정도 나옴)

→ 컬럼 하나를 **두 개의 enum 컬럼으로 분리**하는 걸 제안:

```python
class EnrollmentStatus(str, Enum):
    FRESHMAN = "freshman"              # 신입생
    ENROLLED = "enrolled"              # 재학생
    LEAVE_OF_ABSENCE = "leave_of_absence"  # 휴학생
    GRADUATED = "graduated"            # 졸업생

class DegreeLevel(str, Enum):
    UNDERGRADUATE = "undergraduate"    # 학부
    MASTERS = "masters"                # 석사
    DOCTORAL = "doctoral"              # 박사
    INTEGRATED_MS_PHD = "integrated_ms_phd"  # 석·박사통합과정
```

`scholarship` 테이블: `grade_level: str` → `required_enrollment_status: EnrollmentStatus | None`, `required_degree_level: DegreeLevel | None` (다른 조건들과 동일하게 None=제한 없음).

`UserSpec`: `enrollment_status`, `degree_level` 두 필드 신규 추가 필요 — 지금까지 크롤링 중 "재학생만/휴학생 불가" 같은 조건이 실제로 자주 나왔는데, 지금 구조로는 휴학생·졸업생 여부를 아예 구분할 방법이 없었음.

기존에 이미 넣은 117건은 `grade_level`에 텍스트로 "신입생"/"재학생" 등이 들어가 있어서, 컬럼 분리 시 재크롤링 없이 텍스트 파싱으로 대부분 백필 가능할 것으로 보임(휴학생/졸업생 조건은 원래 데이터에 거의 없었어서 대부분 "제한 없음"으로 채워질 것).

---

## 그 외 호성과 논의할 사항 (자격조건 매칭과는 별개)

1. **UserSpec이 아예 저장이 안 됨** — `user_spec.py` 주석에 "v1은 1회성 입력이라 저장 안 함"이라고 명시돼 있음. 대학/전공/학년/GPA스케일까지 UserSpec에 추가되면 입력 항목이 12개+로 늘어나는데, 로그인/프로필 저장 없이 매번 이 정도를 입력시키는 게 맞는지 결정 필요.
2. **DB에 중복 방지 제약이 없음** — 지금 중복 제거는 `scholarship_dedup_list.md`를 사람이 손으로 대조하는 방식뿐. 대학이 늘어날수록(한밭대·카이스트 이후 계속) 깨지기 쉬움 — `name+provider` 유니크 제약이나 INSERT 전 자동 중복검사를 백엔드에 둘지 논의.
3. **새 필드 추가 시 프론트엔드도 같이 손봐야 함** — 대학/전공/학년(신규 enum 2개)/GPA스케일을 UserSpec에 추가하면 프론트 입력 폼(드롭다운 등)도 새로 필요. 백엔드 스키마만의 문제가 아님.
4. **마감일 자동 정리** (위 표 7번의 연장) — 대학이 늘어나면 이미 넣은 장학금들의 마감이 하나둘 지나갈 텐데, 주기적 재크롤링/정리 계획이 필요한지, 구조화된 deadline 컬럼으로 자동 필터링할지 방향 결정 필요.

---

## 참고

관련 크롤링 규칙: [supabase/scholarship_dedup_list.md](scholarship_dedup_list.md), [supabase/README.md](README.md)
