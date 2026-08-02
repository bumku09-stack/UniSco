from sqlmodel import Field, SQLModel

from app.models.enums import (
    CategoryL1,
    CategoryL2,
    DegreeLevel,
    EnrollmentStatus,
    ForeignerEligibility,
    Gender,
    GpaBasis,
    MilitaryStatus,
    enum_column,
)


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
    required_gender: Gender | None = Field(default=None, sa_type=enum_column(Gender))
    eligible_region: str | None = None
    required_military_status: MilitaryStatus | None = Field(
        default=None, sa_type=enum_column(MilitaryStatus)
    )
    max_income_bracket: int | None = None  # 소득분위 N 이하
    min_gpa: float | None = None  # 4.5 만점 기준
    min_gpa_basis: GpaBasis | None = Field(
        default=None, sa_type=enum_column(GpaBasis)
    )  # 이 min_gpa가 직전학기/전체누적 중 어느 기준인지. None=미지정(둘 중 하나만 만족해도 통과)
    requires_disability: bool | None = None  # None=무관, True=장애인 한정
    foreigner_eligibility: ForeignerEligibility | None = Field(
        default=None, sa_type=enum_column(ForeignerEligibility)
    )  # None=내국인/외국인 무관

    # Free-text eligibility detail that doesn't fit a clean enum/range — added
    # after reviewing real scraped data, which needed these as separate columns
    # rather than crammed into `description`.
    grade_level: str | None = None  # (레거시, 구조화 전 원문) 학년 조건 텍스트
    major: str | None = None  # 전공 조건 — 아직 매칭에 안 씀, 학과 단위 정밀매칭은 다음 단계
    affiliated_institution: str | None = None  # (레거시, 구조화 전 원문) 소속 대학/학과 텍스트
    min_credits: str | None = None  # 이수학점 조건 (형식이 제각각이라 텍스트)
    admission_score_condition: str | None = None  # 내신/입학성적 조건
    headcount: str | None = None  # 선발 인원
    application_period: str | None = None  # 신청 기간

    # 구조화된 자격조건 (정밀 매칭용). None=제한 없음, 기존 규칙과 동일.
    eligible_university: str | None = None  # 짧은 태그 (예: "충남대학교", "KAIST")
    eligible_college: str | None = None  # 단과대 (예: "공과대학") — 소속 대학이 정해진 경우만 의미 있음
    required_enrollment_status: EnrollmentStatus | None = Field(
        default=None, sa_type=enum_column(EnrollmentStatus)
    )
    min_grade: int | None = None  # 학부 학년 하한 (재학상태가 학부 관련일 때만 의미)
    max_grade: int | None = None  # 학부 학년 상한
    required_degree_level: DegreeLevel | None = Field(
        default=None, sa_type=enum_column(DegreeLevel)
    )  # 재학상태가 학부이후과정일 때만 의미

    # 분류 체계 (자격조건 아님 — 매칭 필터링에 안 쓰고, 목록 표시/그룹핑용).
    # category_l2가 어느 category_l1에 속하는지는 app.models.enums.CATEGORY_L2_BY_L1 참고.
    category_l1: CategoryL1 | None = Field(default=None, sa_type=enum_column(CategoryL1))
    category_l2: CategoryL2 | None = Field(default=None, sa_type=enum_column(CategoryL2))
