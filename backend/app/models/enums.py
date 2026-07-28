from enum import Enum


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


class EnrollmentStatus(str, Enum):
    UNDERGRAD_ENROLLED = "undergrad_enrolled"  # 학부재학
    UNDERGRAD_LEAVE = "undergrad_leave"  # 학부휴학
    POST_UNDERGRAD = "post_undergrad"  # 학부이후과정 (대학원 등)


class DegreeLevel(str, Enum):
    MASTERS = "masters"  # 석사
    DOCTORAL = "doctoral"  # 박사
    INTEGRATED_MS_PHD = "integrated_ms_phd"  # 석박사통합
