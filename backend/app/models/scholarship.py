from sqlmodel import Field, SQLModel

from app.models.enums import ForeignerEligibility, Gender, MilitaryStatus


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
    required_gender: Gender | None = None
    eligible_region: str | None = None
    required_military_status: MilitaryStatus | None = None
    max_income_bracket: int | None = None  # 소득분위 N 이하
    min_gpa: float | None = None  # 4.5 만점 기준
    requires_disability: bool | None = None  # None=무관, True=장애인 한정
    foreigner_eligibility: ForeignerEligibility | None = None  # None=내국인/외국인 무관
