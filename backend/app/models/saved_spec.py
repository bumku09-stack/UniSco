from sqlalchemy import ARRAY, Column, String
from sqlmodel import Field, SQLModel

from app.models.enums import (
    DegreeLevel,
    DisabilityType,
    EnrollmentStatus,
    Gender,
    LanguageTestType,
    MilitaryStatus,
    SpecialStatus,
    enum_column,
)


class SavedSpec(SQLModel, table=True):
    """Persisted counterpart of UserSpec (app/models/user_spec.py) — one row
    per user. This is what /users/me/spec reads and writes so a user's spec
    survives across logins."""

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True, index=True)

    university: str
    college: str
    department: str | None = None  # 2026-08-03 추가, matching_gaps.md 2번
    semester_gpa: float
    cumulative_gpa: float
    age: int
    gender: Gender = Field(sa_type=enum_column(Gender))
    region: str
    military_status: MilitaryStatus = Field(sa_type=enum_column(MilitaryStatus))
    # 2026-08-03: 필수 -> 선택으로 변경 — 자기 소득분위를 모르는 사용자가 많아서 "모름"으로
    # 넘어갈 수 있게 함. None이면 소득분위 조건이 있는 장학금도 안 거르고 다 보여줌
    # (core/matching.py의 is_eligible() 참고, special_status의 "선택 안 함=모름=안 거름"
    # 원칙과 동일).
    income_bracket: int | None = None
    has_disability: bool
    is_foreigner: bool

    enrollment_status: EnrollmentStatus = Field(sa_type=enum_column(EnrollmentStatus))
    grade: int | None = None
    degree_level: DegreeLevel | None = Field(default=None, sa_type=enum_column(DegreeLevel))

    # 2026-08-02 추가 (matching_gaps.md 9·10·12번).
    language_test_type: LanguageTestType | None = Field(
        default=None, sa_type=enum_column(LanguageTestType)
    )
    language_test_score: float | None = None
    disability_type: DisabilityType | None = Field(default=None, sa_type=enum_column(DisabilityType))
    # Postgres TEXT[]로 저장 — SpecialStatus는 다중 선택이라 단일 enum 컬럼으로 표현 안 됨.
    # (ARRAY(Enum)은 SQLAlchemy/asyncpg 조합에서 다루기 까다로워서, 문자열 배열로 저장하고
    # 값 자체는 SpecialStatus.value와 항상 일치하도록 애플리케이션 레벨에서만 검증함.)
    special_status: list[SpecialStatus] = Field(
        default_factory=list, sa_column=Column(ARRAY(String), nullable=False, server_default="{}")
    )
