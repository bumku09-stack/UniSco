from app.models import EnrollmentStatus, ForeignerEligibility, SavedSpec, Scholarship, UserSpec


def to_user_spec(saved: SavedSpec) -> UserSpec:
    # SavedSpec's fields are UserSpec's fields plus id/user_id — same shape by design
    # (SavedSpec is UserSpec's persisted counterpart, see app/models/saved_spec.py).
    return UserSpec(**saved.model_dump(exclude={"id", "user_id"}))


# min_gpa is always stored on a 4.5 scale (see supabase/README.md). Schools
# grade on different scales (KAIST is 4.3) — must mirror
# frontend/src/lib/universities.ts's gpaScale so a user's self-reported GPA
# compares correctly against that normalized 4.5-scale threshold.
UNIVERSITY_GPA_SCALE = {
    "충남대학교": 4.5,
    "KAIST": 4.3,
    "한밭대학교": 4.5,
    "배재대학교": 4.5,
    "목원대학교": 4.5,
    "우송대학교": 4.5,
    "한남대학교": 4.5,
}
DEFAULT_GPA_SCALE = 4.5


def normalized_gpa(spec: UserSpec) -> float:
    scale = UNIVERSITY_GPA_SCALE.get(spec.university, DEFAULT_GPA_SCALE)
    return spec.gpa * (4.5 / scale)


def enrollment_status_matches(
    required: EnrollmentStatus | None, spec_status: EnrollmentStatus
) -> bool:
    """Existing scholarships were tagged undergrad_enrolled before
    undergrad_transfer existed as a value, meaning "재학생" scholarships mean
    "currently actively enrolled" rather than "not a transfer admit" — so a
    transfer student satisfies an undergrad_enrolled requirement too.
    Freshman-only scholarships stay correctly excluded via min_grade/max_grade
    (transfer students never carry grade=1) rather than through this check."""
    if required is None:
        return True
    if required == EnrollmentStatus.UNDERGRAD_ENROLLED:
        return spec_status in (
            EnrollmentStatus.UNDERGRAD_ENROLLED,
            EnrollmentStatus.UNDERGRAD_TRANSFER,
        )
    return required == spec_status


def is_eligible(scholarship: Scholarship, spec: UserSpec) -> bool:
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
    if scholarship.min_gpa is not None and normalized_gpa(spec) < scholarship.min_gpa:
        return False
    if scholarship.requires_disability and not spec.has_disability:
        return False
    if (
        scholarship.foreigner_eligibility == ForeignerEligibility.FOREIGNER_ONLY
        and not spec.is_foreigner
    ):
        return False
    if scholarship.foreigner_eligibility == ForeignerEligibility.KOREAN_ONLY and spec.is_foreigner:
        return False
    if (
        scholarship.eligible_university is not None
        and scholarship.eligible_university != spec.university
    ):
        return False
    if scholarship.eligible_college is not None and scholarship.eligible_college != spec.college:
        return False
    if not enrollment_status_matches(
        scholarship.required_enrollment_status, spec.enrollment_status
    ):
        return False
    if scholarship.min_grade is not None and (
        spec.grade is None or spec.grade < scholarship.min_grade
    ):
        return False
    if scholarship.max_grade is not None and (
        spec.grade is None or spec.grade > scholarship.max_grade
    ):
        return False
    if (
        scholarship.required_degree_level is not None
        and scholarship.required_degree_level != spec.degree_level
    ):
        return False
    return True


def specificity_score(scholarship: Scholarship) -> int:
    """How many eligibility criteria this scholarship actually sets, among
    the ones a passed-in UserSpec could be filtered on. Every scholarship
    reaching this point already passed is_eligible, so a higher score means
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


def match_scholarships(scholarships: list[Scholarship], spec: UserSpec) -> list[Scholarship]:
    eligible = [s for s in scholarships if is_eligible(s, spec)]
    eligible.sort(key=specificity_score, reverse=True)
    return eligible
