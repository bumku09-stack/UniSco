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
