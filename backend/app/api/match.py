from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db.session import get_session
from app.models import ForeignerEligibility, Scholarship, UserSpec

router = APIRouter()

# min_gpa is always stored on a 4.5 scale (see supabase/README.md). Schools
# grade on different scales (KAIST is 4.3) — must mirror
# frontend/src/lib/universities.ts's gpaScale so a user's self-reported GPA
# compares correctly against that normalized 4.5-scale threshold.
UNIVERSITY_GPA_SCALE = {
    "충남대학교": 4.5,
    "KAIST": 4.3,
}
DEFAULT_GPA_SCALE = 4.5


def _normalized_gpa(spec: UserSpec) -> float:
    scale = UNIVERSITY_GPA_SCALE.get(spec.university, DEFAULT_GPA_SCALE)
    return spec.gpa * (4.5 / scale)


def _is_eligible(scholarship: Scholarship, spec: UserSpec) -> bool:
    """A scholarship field left as None means no restriction for that
    criterion (see backend/app/models/scholarship.py) — only check fields
    that are actually set."""
    if scholarship.min_age is not None and spec.age < scholarship.min_age:
        return False
    if scholarship.max_age is not None and spec.age > scholarship.max_age:
        return False
    if scholarship.required_gender is not None and scholarship.required_gender != spec.gender:
        return False
    if scholarship.eligible_region is not None and spec.region not in scholarship.eligible_region:
        return False
    if (
        scholarship.required_military_status is not None
        and scholarship.required_military_status != spec.military_status
    ):
        return False
    if (
        scholarship.max_income_bracket is not None
        and spec.income_bracket > scholarship.max_income_bracket
    ):
        return False
    if scholarship.min_gpa is not None and _normalized_gpa(spec) < scholarship.min_gpa:
        return False
    if scholarship.requires_disability and not spec.has_disability:
        return False
    if scholarship.foreigner_eligibility == ForeignerEligibility.FOREIGNER_ONLY and not spec.is_foreigner:
        return False
    if scholarship.foreigner_eligibility == ForeignerEligibility.KOREAN_ONLY and spec.is_foreigner:
        return False
    if scholarship.eligible_university is not None and scholarship.eligible_university != spec.university:
        return False
    if scholarship.eligible_college is not None and scholarship.eligible_college != spec.college:
        return False
    if (
        scholarship.required_enrollment_status is not None
        and scholarship.required_enrollment_status != spec.enrollment_status
    ):
        return False
    if scholarship.min_grade is not None and (spec.grade is None or spec.grade < scholarship.min_grade):
        return False
    if scholarship.max_grade is not None and (spec.grade is None or spec.grade > scholarship.max_grade):
        return False
    if (
        scholarship.required_degree_level is not None
        and scholarship.required_degree_level != spec.degree_level
    ):
        return False
    return True


@router.post("/match", response_model=list[Scholarship])
def match_scholarships(spec: UserSpec, session: Session = Depends(get_session)):
    scholarships = session.exec(select(Scholarship)).all()
    return [s for s in scholarships if _is_eligible(s, spec)]
