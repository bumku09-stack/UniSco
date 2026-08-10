import datetime

from sqlalchemy import ARRAY, Column, String
from sqlmodel import Field, SQLModel

from app.models.enums import (
    CategoryL1,
    CategoryL2,
    DegreeLevel,
    DisabilityType,
    EnrollmentStatus,
    ForeignerEligibility,
    Gender,
    GpaBasis,
    LanguageTestType,
    MilitaryStatus,
    SpecialStatus,
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
    required_disability_type: DisabilityType | None = Field(
        default=None, sa_type=enum_column(DisabilityType)
    )  # requires_disability=True일 때만 의미. None=장애 유형 무관(장애인이면 다 해당)
    foreigner_eligibility: ForeignerEligibility | None = Field(
        default=None, sa_type=enum_column(ForeignerEligibility)
    )  # None=내국인/외국인 무관
    language_test_type: LanguageTestType | None = Field(
        default=None, sa_type=enum_column(LanguageTestType)
    )  # 2026-08-02 추가(matching_gaps.md 10번). None=어학점수 조건 없음
    language_test_min_score: float | None = None  # language_test_type이 있을 때만 의미
    # 2026-08-02 추가(matching_gaps.md 9번), 2026-08-03 단일값→리스트로 변경(배재사랑장학금
    # "장애학생 또는 다문화가정 학생" 같은 OR조건 표현 위함). 빈 리스트=특수상황 조건 없음.
    # 매칭 로직은 다른 필드들과 다름(core/matching.py의 special_status_matches() 참고,
    # 유저가 특수상황을 아예 선택 안 하면 이 조건이 있어도 걸러내지 않음). 이 장학금이
    # requires_disability/required_disability_type도 같이 갖고 있으면 "장애 조건 OR 특수상황
    # 조건"으로 취급함(core/matching.py의 is_eligible() 참고).
    required_special_status: list[SpecialStatus] = Field(
        default_factory=list, sa_column=Column(ARRAY(String), nullable=False, server_default="{}")
    )
    # 2026-08-10 추가(matching_gaps.md "특수상황 AND 조건"). required_special_status(하나만
    # 맞아도 통과, OR)와 별개로 "이건 전부 다 있어야 함" 목록. 빈 리스트=추가 AND 조건 없음
    # (기존과 동일). 예: 다문화가정학생장학금(영암군) "다문화가정 이면서 (기초수급자 또는
    # 차상위)"는 required_special_status_all=[multicultural_family],
    # required_special_status=[basic_livelihood_recipient, near_poor]로 표현.
    required_special_status_all: list[SpecialStatus] = Field(
        default_factory=list, sa_column=Column(ARRAY(String), nullable=False, server_default="{}")
    )
    # 2026-08-03 추가 — 구조화된 마감일(matching_gaps.md 7번). 대부분의 기존 데이터는
    # "매 학기 초 공지"류 상시/반복 프로그램이라 NULL로 남아있고(마감 자동판정 대상 아님),
    # 실제 확정 마감일이 있는 공고만 이 값을 채워서 자동으로 걸러지게 함(match_scholarships()
    # 참고). 신규 크롤링 시 확정 마감일을 알아내면 여기 채울 것 — 기존 366건 백필은 별도 작업.
    application_deadline: datetime.date | None = None

    # Free-text eligibility detail that doesn't fit a clean enum/range — added
    # after reviewing real scraped data, which needed these as separate columns
    # rather than crammed into `description`.
    grade_level: str | None = None  # (레거시, 구조화 전 원문) 학년 조건 텍스트
    # 2026-08-03: matching_gaps.md 2번 해결 — UserSpec.department와 매칭에 실제로 씀
    # (core/matching.py의 major_matches() 참고). 콤마로 여러 학과가 나열된 기존 데이터
    # (예: "융합디자인전공,회화전공,미술교육과")도 그대로 지원함 — 그 중 하나만 일치해도 통과.
    major: str | None = None
    # 2026-08-10 추가(matching_gaps.md "전공 제외 조건") — "이 학과만 빼고 나머지 전부 됨"
    # 조건 (major는 반대로 "이 학과만 됨"). major와 동일한 컨벤션(콤마 구분).
    # None=제외 학과 없음(기존과 동일). core/matching.py의 major_matches() 참고.
    excluded_major: str | None = None
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
