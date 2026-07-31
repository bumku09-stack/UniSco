from sqlmodel import Field, SQLModel

from app.models.enums import DegreeLevel, EnrollmentStatus, Gender, MilitaryStatus, enum_column


class SavedSpec(SQLModel, table=True):
    """Persisted counterpart of UserSpec (app/models/user_spec.py) — one row
    per user. UserSpec stays as the shape /match's request body uses; this is
    what /users/me/spec reads and writes so a user's spec survives across
    logins instead of only living in the frontend's localStorage."""

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True, index=True)

    university: str
    college: str
    gpa: float
    age: int
    gender: Gender = Field(sa_type=enum_column(Gender))
    region: str
    military_status: MilitaryStatus = Field(sa_type=enum_column(MilitaryStatus))
    income_bracket: int
    has_disability: bool
    is_foreigner: bool

    enrollment_status: EnrollmentStatus = Field(sa_type=enum_column(EnrollmentStatus))
    grade: int | None = None
    degree_level: DegreeLevel | None = Field(default=None, sa_type=enum_column(DegreeLevel))
