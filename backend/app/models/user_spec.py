from sqlmodel import SQLModel

from app.models.enums import (
    DegreeLevel,
    DisabilityType,
    EnrollmentStatus,
    Gender,
    LanguageTestType,
    MilitaryStatus,
    SpecialStatus,
)


class UserSpec(SQLModel):
    """/users/me/spec request/response body shape — not a DB table itself.

    SavedSpec (app/models/saved_spec.py) is the persisted per-user table with
    the same field shape; to_user_spec() in core/matching.py converts one to
    the other.
    """

    university: str  # 소속 대학 (예: 충남대학교, KAIST) — GPA 만점 기준을 정하는 데도 씀
    college: str  # 단과대 (예: 공과대학)
    department: str | None = None  # 학과 (예: 컴퓨터공학과) — 2026-08-03 추가, matching_gaps.md 2번
    semester_gpa: float  # 직전 학기 평점평균 (해당 대학 만점 기준 원점수, 정규화는 matching.py에서)
    cumulative_gpa: float  # 전체 재학기간 누적 평점평균(CGPA) — 마찬가지로 원점수
    age: int
    gender: Gender
    region: str
    # 2026-08-05 추가 (matching_gaps.md 14번) — 시/도(region)만으론 "정읍시 거주자만" 같은
    # 시/군/구 단위 지자체 장학금을 못 걸러서 추가함. 프론트에서 이미 물어보던 값인데 그동안
    # 서버로 안 보내고 버리고 있었음(frontend/src/lib/spec.ts 참고). 세종처럼 하위 구/군이
    # 없는 시/도는 빈 문자열/None일 수 있음.
    district: str | None = None
    # 2026-08-05 추가 (matching_gaps.md 19번) — "본인 또는 부모 중 1인이 OO에 거주" 조건을
    # 표현하기 위한 선택 입력. None="입력 안 함/모름" — 이때는 매칭에 아예 안 쓰이고 기존처럼
    # region(본인 거주지)만으로 판단함. core/matching.py의 region_matches() 참고.
    parent_region: str | None = None
    parent_district: str | None = None  # 2026-08-05 추가 (matching_gaps.md 14번 후속) — 부모 쪽 시/군/구 단위
    military_status: MilitaryStatus
    income_bracket: int | None = None  # None="모름" — 소득분위 조건이 있는 장학금도 안 거름
    has_disability: bool
    is_foreigner: bool

    enrollment_status: EnrollmentStatus
    grade: int | None = None  # enrollment_status가 학부재학/학부휴학일 때만 사용
    degree_level: DegreeLevel | None = None  # enrollment_status가 학부이후과정일 때만 사용

    # 2026-08-02 추가 (matching_gaps.md 9·10·12번, 전부 선택 입력).
    language_test_type: LanguageTestType | None = None
    language_test_score: float | None = None  # language_test_type이 있을 때만 의미
    disability_type: DisabilityType | None = None  # has_disability=True일 때만 의미
    # 특수상황은 다중 선택 — 아예 비어있으면(선택 안 함) matching.py에서 특수상황 조건이
    # 있는 장학금도 걸러내지 않는 예외 처리가 됨(special_status_matches() 참고).
    special_status: list[SpecialStatus] = []


class SpecStatusResponse(SQLModel):
    spec_completed: bool
