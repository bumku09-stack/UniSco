from sqlmodel import SQLModel

from app.models.enums import Gender, MilitaryStatus


class UserSpec(SQLModel):
    """Matching request payload shape — not a DB table.

    v1 is one-time input (see PROJECT_BRIEF.md), so specs aren't persisted;
    this just defines what the frontend sends to the matching endpoint.
    """

    age: int
    gender: Gender
    region: str
    military_status: MilitaryStatus
    income_bracket: int
    gpa: float
    has_disability: bool
    is_foreigner: bool
