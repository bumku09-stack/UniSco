from sqlmodel import SQLModel

from app.models.enums import DegreeLevel, EnrollmentStatus, Gender, MilitaryStatus


class UserSpec(SQLModel):
    """Matching request payload shape — not a DB table (for now).

    Frontend currently persists this client-side (localStorage) since there's
    no real login yet — see frontend/src/app/login. Once auth exists this
    should move to a real per-user table instead.
    """

    university: str  # 소속 대학 (예: 충남대학교, KAIST) — GPA 만점 기준을 정하는 데도 씀
    college: str  # 단과대 (예: 공과대학)
    gpa: float
    age: int
    gender: Gender
    region: str
    military_status: MilitaryStatus
    income_bracket: int
    has_disability: bool
    is_foreigner: bool

    enrollment_status: EnrollmentStatus
    grade: int | None = None  # enrollment_status가 학부재학/학부휴학일 때만 사용
    degree_level: DegreeLevel | None = None  # enrollment_status가 학부이후과정일 때만 사용
