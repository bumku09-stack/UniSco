from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, SQLModel

from app.models.enums import ForeignerEligibility, Gender, MilitaryStatus


def _enum_column(enum_cls):
    """Store the enum's .value (lowercase) in Postgres instead of SQLAlchemy's
    default .name (uppercase) — keeps raw-SQL inserts consistent with the API's
    JSON casing and with supabase/README.md's column reference."""
    return SAEnum(enum_cls, values_callable=lambda e: [member.value for member in e])


class Scholarship(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    name: str
    provider: str | None = None
    description: str | None = None
    amount: int | None = None
    application_url: str | None = None

    # Eligibility conditions. A field left as None means "no restriction" for
    # that criterion — a scholarship open to everyone has every field below unset.
    min_age: int | None = None
    max_age: int | None = None
    required_gender: Gender | None = Field(default=None, sa_type=_enum_column(Gender))
    eligible_region: str | None = None
    required_military_status: MilitaryStatus | None = Field(
        default=None, sa_type=_enum_column(MilitaryStatus)
    )
    max_income_bracket: int | None = None  # 소득분위 N 이하
    min_gpa: float | None = None  # 4.5 만점 기준
    requires_disability: bool | None = None  # None=무관, True=장애인 한정
    foreigner_eligibility: ForeignerEligibility | None = Field(
        default=None, sa_type=_enum_column(ForeignerEligibility)
    )  # None=내국인/외국인 무관

    # Free-text eligibility detail that doesn't fit a clean enum/range — added
    # after reviewing real scraped data, which needed these as separate columns
    # rather than crammed into `description`.
    grade_level: str | None = None  # 학년 조건 (예: "신입생", "재학생")
    major: str | None = None  # 전공 조건
    affiliated_institution: str | None = None  # 소속 대학/기관 한정
    min_credits: str | None = None  # 이수학점 조건 (형식이 제각각이라 텍스트)
    admission_score_condition: str | None = None  # 내신/입학성적 조건
    headcount: str | None = None  # 선발 인원
    application_period: str | None = None  # 신청 기간
