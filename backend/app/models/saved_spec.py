from datetime import date

from sqlalchemy import ARRAY, Column, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from app.models.enums import (
    AdmissionTrack,
    DegreeLevel,
    DisabilityType,
    DischargeType,
    EnrollmentStatus,
    Gender,
    MilitaryStatus,
    SpecialStatus,
    enum_column,
)
from app.models.user_spec import LanguageTestEntry


class SavedSpec(SQLModel, table=True):
    """Persisted counterpart of UserSpec (app/models/user_spec.py) — one row
    per user. This is what /users/me/spec reads and writes so a user's spec
    survives across logins."""

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True, index=True)

    display_name: str | None = None  # 2026-08-21 추가 — UserSpec 참고.
    birth_date: date | None = None  # 2026-08-21 추가 — UserSpec 참고.
    university: str
    college: str
    department: str | None = None  # 2026-08-03 추가, matching_gaps.md 2번
    semester_gpa: float
    cumulative_gpa: float
    # 2026-08-12 추가 — UserSpec 참고.
    credits_last_semester: int | None = None
    age: int
    gender: Gender = Field(sa_type=enum_column(Gender))
    region: str
    district: str | None = None  # 2026-08-05 추가, matching_gaps.md 14번
    address: str | None = None  # 2026-08-21 추가 — UserSpec 참고.
    parent_region: str | None = None  # 2026-08-05 추가, matching_gaps.md 19번
    parent_district: str | None = None  # 2026-08-05 추가, matching_gaps.md 14번 후속
    parent_address: str | None = None  # 2026-08-21 추가 — UserSpec 참고.
    # 2026-08-21 — 필수 -> 선택 입력으로 변경. UserSpec 참고.
    military_status: MilitaryStatus | None = Field(default=None, sa_type=enum_column(MilitaryStatus))
    # 2026-08-15 추가 — UserSpec 참고. military_status가 completed일 때만 의미 있음.
    discharge_type: DischargeType | None = Field(default=None, sa_type=enum_column(DischargeType))
    # 2026-08-03: 필수 -> 선택으로 변경 — 자기 소득분위를 모르는 사용자가 많아서 "모름"으로
    # 넘어갈 수 있게 함. None이면 소득분위 조건이 있는 장학금도 안 거르고 다 보여줌
    # (core/matching.py의 is_eligible() 참고, special_status의 "선택 안 함=모름=안 거름"
    # 원칙과 동일).
    income_bracket: int | None = None
    has_disability: bool | None = None  # 2026-08-22 — 필수 -> 선택 입력으로 변경. UserSpec 참고.
    is_foreigner: bool

    enrollment_status: EnrollmentStatus = Field(sa_type=enum_column(EnrollmentStatus))
    grade: int | None = None
    degree_level: DegreeLevel | None = Field(default=None, sa_type=enum_column(DegreeLevel))
    # 2026-08-12 추가 — UserSpec 참고. None이면 매칭 시 GENERAL로 간주(admission_track_matches()).
    admission_track: AdmissionTrack | None = Field(
        default=None, sa_type=enum_column(AdmissionTrack)
    )

    # 2026-08-02 추가 (matching_gaps.md 9·10·12번). 2026-08-21 — 시험 하나만(language_test_type/
    # language_test_score) 저장하던 걸 여러 개 넣을 수 있게 JSONB 배열로 변경 — UserSpec의
    # LanguageTestEntry 참고. TEXT[]로는 종류+점수 쌍(object)을 표현할 수 없어서 JSONB로 저장.
    language_tests: list[LanguageTestEntry] = Field(
        default_factory=list, sa_column=Column(JSONB, nullable=False, server_default="[]")
    )
    # 2026-08-21 — 단일 값에서 특수상황과 같은 복수선택으로 변경. Postgres TEXT[]로 저장
    # (ARRAY(Enum)은 SQLAlchemy/asyncpg 조합에서 다루기 까다로워서, 문자열 배열로 저장하고
    # 값 자체는 DisabilityType.value와 항상 일치하도록 애플리케이션 레벨에서만 검증함).
    disability_type: list[DisabilityType] = Field(
        default_factory=list, sa_column=Column(ARRAY(String), nullable=False, server_default="{}")
    )
    # 위와 동일한 이유로 TEXT[]로 저장 — SpecialStatus는 다중 선택이라 단일 enum 컬럼으로
    # 표현 안 됨.
    special_status: list[SpecialStatus] = Field(
        default_factory=list, sa_column=Column(ARRAY(String), nullable=False, server_default="{}")
    )
