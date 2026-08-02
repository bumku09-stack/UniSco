from enum import Enum

from sqlalchemy import Enum as SAEnum


def enum_column(enum_cls):
    """Store the enum's .value (lowercase) in Postgres instead of SQLAlchemy's
    default .name (uppercase) — keeps raw-SQL inserts consistent with the API's
    JSON casing and with supabase/README.md's column reference."""
    return SAEnum(enum_cls, values_callable=lambda e: [member.value for member in e])


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class MilitaryStatus(str, Enum):
    COMPLETED = "completed"  # 군필
    EXEMPTED = "exempted"  # 면제
    NOT_SERVED = "not_served"  # 미필


class ForeignerEligibility(str, Enum):
    KOREAN_ONLY = "korean_only"
    FOREIGNER_ONLY = "foreigner_only"


class GpaBasis(str, Enum):
    """min_gpa가 직전학기 성적 기준인지 전체 재학기간 누적(CGPA) 기준인지 — 대학마다,
    같은 대학 안에서도 장학금마다 둘 중 하나를 요구하는 경우가 섞여 있어서 분리함
    (2026-08-02, 우송대 재검증 중 발견 — matching_gaps.md 13번 참고).
    None(미지정)인 기존/신규 데이터는 matching.py에서 직전학기·전체누적 중 하나라도
    만족하면 통과시키는 관대한 기본값으로 처리함."""

    SEMESTER = "semester"  # 직전학기 성적 기준
    CUMULATIVE = "cumulative"  # 전체 재학기간 누적(CGPA) 기준


class EnrollmentStatus(str, Enum):
    UNDERGRAD_ENROLLED = "undergrad_enrolled"  # 학부재학
    UNDERGRAD_TRANSFER = "undergrad_transfer"  # 학부편입 — 매칭 시 취급은 core/matching.py 참고
    UNDERGRAD_LEAVE = "undergrad_leave"  # 학부휴학
    POST_UNDERGRAD = "post_undergrad"  # 학부이후과정 (대학원 등)


class DegreeLevel(str, Enum):
    MASTERS = "masters"  # 석사
    DOCTORAL = "doctoral"  # 박사
    INTEGRATED_MS_PHD = "integrated_ms_phd"  # 석박사통합


class CategoryL1(str, Enum):
    SCHOOL_INTERNAL = "school_internal"  # 교내장학금
    SCHOOL_EXTERNAL = "school_external"  # 교외장학금
    SUPPORT_FUND = "support_fund"  # 지원금


class CategoryL2(str, Enum):
    # school_internal(교내장학금) 하위
    ACADEMIC_MERIT = "academic_merit"  # 성적장학금
    WELFARE_LIVING = "welfare_living"  # 복지생활지원장학금
    SPECIAL_TARGET = "special_target"  # 특수대상장학금
    ACTIVITY_MERIT = "activity_merit"  # 활동공로장학금
    RESEARCH = "research"  # 연구장학금
    INTERNATIONAL_EXCHANGE = "international_exchange"  # 국제교류장학금
    DEPARTMENT_ALUMNI = "department_alumni"  # 학과동문회자체장학금
    # school_external(교외장학금) 하위
    NATIONAL_SCHOLARSHIP = "national_scholarship"  # 국가장학금
    LOCAL_GOV = "local_gov"  # 지자체장학금
    PRIVATE_FOUNDATION = "private_foundation"  # 민간재단기업장학금
    ASSOCIATION = "association"  # 협회학회장학금
    # support_fund(지원금) 하위
    YOUTH_LIVING_SUPPORT = "youth_living_support"  # 청년생활지원금
    ACTIVITY_PARTICIPATION_SUPPORT = "activity_participation_support"  # 활동참여지원금


# category_l2 값이 어느 category_l1에 속하는지 — DB에 이 관계를 강제하는 제약은 안 걸었고
# (SQLModel/Postgres에서 "enum 값이 다른 컬럼 값에 따라 제한"은 CHECK 제약이 따로 필요해서
# 지금 단계엔 과함), 이 매핑은 프론트 드롭다운이랑 문서용 참고 자료로만 씀.
CATEGORY_L2_BY_L1: dict[CategoryL1, list[CategoryL2]] = {
    CategoryL1.SCHOOL_INTERNAL: [
        CategoryL2.ACADEMIC_MERIT,
        CategoryL2.WELFARE_LIVING,
        CategoryL2.SPECIAL_TARGET,
        CategoryL2.ACTIVITY_MERIT,
        CategoryL2.RESEARCH,
        CategoryL2.INTERNATIONAL_EXCHANGE,
        CategoryL2.DEPARTMENT_ALUMNI,
    ],
    CategoryL1.SCHOOL_EXTERNAL: [
        CategoryL2.NATIONAL_SCHOLARSHIP,
        CategoryL2.LOCAL_GOV,
        CategoryL2.PRIVATE_FOUNDATION,
        CategoryL2.ASSOCIATION,
    ],
    CategoryL1.SUPPORT_FUND: [
        CategoryL2.YOUTH_LIVING_SUPPORT,
        CategoryL2.ACTIVITY_PARTICIPATION_SUPPORT,
    ],
}
