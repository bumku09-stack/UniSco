from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db.session import get_session
from app.models import ForeignerEligibility, Scholarship, UserSpec

router = APIRouter()


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
    if scholarship.min_gpa is not None and spec.gpa < scholarship.min_gpa:
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


def _specificity_score(scholarship: Scholarship) -> int:
    """How many eligibility criteria this scholarship actually sets, among
    the ones a passed-in UserSpec could be filtered on. Every scholarship
    reaching this point already passed _is_eligible, so a higher score means
    it's narrowly targeted at this exact spec (e.g. a specific university +
    college + income bracket) rather than open to almost everyone — ranked
    first because it's the more specific, less competitive match."""
    score = 0
    if scholarship.min_age is not None or scholarship.max_age is not None:
        score += 1
    if scholarship.required_gender is not None:
        score += 1
    if scholarship.eligible_region is not None:
        score += 1
    if scholarship.required_military_status is not None:
        score += 1
    if scholarship.max_income_bracket is not None:
        score += 1
    if scholarship.min_gpa is not None:
        score += 1
    if scholarship.requires_disability:
        score += 1
    if scholarship.foreigner_eligibility is not None:
        score += 1
    if scholarship.eligible_university is not None:
        score += 1
    if scholarship.eligible_college is not None:
        score += 1
    if scholarship.required_enrollment_status is not None:
        score += 1
    if scholarship.min_grade is not None or scholarship.max_grade is not None:
        score += 1
    if scholarship.required_degree_level is not None:
        score += 1
    return score


@router.post("/match", response_model=list[Scholarship])
def match_scholarships(spec: UserSpec, session: Session = Depends(get_session)):
    scholarships = session.exec(select(Scholarship)).all()
    eligible = [s for s in scholarships if _is_eligible(s, spec)]
    eligible.sort(key=_specificity_score, reverse=True)
    return eligible
