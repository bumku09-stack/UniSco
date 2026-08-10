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
    BOTH = "both"  # 직전학기·전체누적 둘 다 동시 충족 필요 (2026-08-02 을지대 크롤링 중 발견,
    # matching_gaps.md 13번 후속 — 기존엔 "둘 중 하나" 케이스만 있었는데 "둘 다" 요구하는
    # 장학금이 나와서 추가함)


class EnrollmentStatus(str, Enum):
    UNDERGRAD_ENROLLED = "undergrad_enrolled"  # 학부재학
    UNDERGRAD_TRANSFER = "undergrad_transfer"  # 학부편입 — 매칭 시 취급은 core/matching.py 참고
    UNDERGRAD_LEAVE = "undergrad_leave"  # 학부휴학
    POST_UNDERGRAD = "post_undergrad"  # 학부이후과정 (대학원 등)


class DegreeLevel(str, Enum):
    MASTERS = "masters"  # 석사
    DOCTORAL = "doctoral"  # 박사
    INTEGRATED_MS_PHD = "integrated_ms_phd"  # 석박사통합


class LanguageTestType(str, Enum):
    """어학점수 조건 (matching_gaps.md 10번, 2026-08-02 구현). frontend/src/lib/spec.ts의
    LANGUAGE_TESTS와 값을 정확히 맞춰야 함 — 프론트가 이 문자열 그대로 보냄."""

    TOEIC = "TOEIC"
    TOEFL = "TOEFL"
    IELTS = "IELTS"
    TOPIK = "TOPIK"
    OTHER = "기타"


class DisabilityType(str, Enum):
    """장애인 세부 유형 (matching_gaps.md 12번, 2026-08-02 구현) — Scholarships.com의
    "Physical Disabilities" 카테고리 7종을 그대로 채택. frontend/src/lib/spec.ts의
    DISABILITY_TYPES와 값을 정확히 맞춰야 함."""

    PHYSICAL_IMPAIRMENT = "physical_impairment"  # 신체적 장애
    LEARNING_DISABILITY = "learning_disability"  # 학습장애
    MEDICAL_DISABILITY = "medical_disability"  # 의료적 장애(질환)
    MENTAL_IMPAIRMENT = "mental_impairment"  # 정신적 장애
    MUSCULAR_DYSTROPHY = "muscular_dystrophy"  # 근이영양증
    DEVELOPMENTAL_IMPAIRMENT = "developmental_impairment"  # 발달장애
    DISABLED_PARENT = "disabled_parent"  # 장애가 있는 부모(자녀 대상) — 본인 장애 아님, 주의


class SpecialStatus(str, Enum):
    """특수상황 신분 (matching_gaps.md 9번, 2026-08-02 구현). frontend/src/lib/spec.ts의
    SPECIAL_STATUS_OPTIONS와 값을 정확히 맞춰야 함. 매칭 로직이 다른 필드들과 다름 —
    core/matching.py의 special_status_matches() 참고(유저가 아예 선택 안 하면 걸러내지 않음).
    `Scholarship.required_special_status`는 리스트(다중)임 — 배재사랑장학금처럼
    "A 또는 B 대상"으로 여러 특수상황이 OR로 묶인 장학금을 표현하기 위함
    (2026-08-03 추가, 아래 5개 값도 이때 함께 추가됨)."""

    NORTH_KOREAN_DEFECTOR = "north_korean_defector"  # 북한이탈주민
    MULTICULTURAL_FAMILY = "multicultural_family"  # 다문화가정
    CHILD_CARE_FACILITY = "child_care_facility"  # 아동양육시설 생활자·퇴소자
    STUDENT_COUNCIL_OFFICER = "student_council_officer"  # 학생회장(임원)
    SINGLE_PARENT_FAMILY = "single_parent_family"  # 한부모가정
    GRANDPARENT_FAMILY = "grandparent_family"  # 조손가정
    # 2026-08-06 기준 완화 — 원래 "3자녀 이상"으로 잡았었는데, 외부 장학금 3차 배치에서
    # "2자녀 이상"을 다자녀로 인정하는 지자체 장학금이 다수(인천·울산연구원·만세보령·김해시 등)
    # 발견되어 기준을 2자녀 이상으로 낮춤. 기존에 3자녀 이상 기준으로 이 태그가 붙은 데이터는
    # 여전히 유효(3자녀는 2자녀 이상의 부분집합). frontend/src/lib/spec.ts의 라벨도
    # "다자녀가정(2자녀 이상)"으로 맞춰서 사용자에게 정확한 기준을 안내함.
    MULTI_CHILD_FAMILY = "multi_child_family"  # 다자녀가정(2자녀 이상)
    NATIONAL_MERIT = "national_merit"  # 국가보훈대상자
    # 2026-08-03 추가 — 배재대 희망복지장학금·대전대 장학사정관장학금 같은 복합조건
    # 장학금을 재분류하면서 새로 필요해진 값들
    BASIC_LIVELIHOOD_RECIPIENT = "basic_livelihood_recipient"  # 기초생활수급자
    NEAR_POOR = "near_poor"  # 차상위계층
    SEVERE_ILLNESS_OR_INJURY = "severe_illness_or_injury"  # 중증질병 및 상해
    JOB_LOSS_OR_DISASTER = "job_loss_or_disaster"  # 실직가정·재난 및 재해
    FINANCIAL_EMERGENCY = "financial_emergency"  # 긴급가계곤란
    # 2026-08-07 추가 — "해당사항 없음". 지금까지 특수상황 칸을 하나도 안 누른 학생은 "아직
    # 대답 안 함"으로 취급돼서(special_status_matches()의 leniency) 특수상황 조건이 걸린
    # 장학금도 계속 노출됐는데, "나는 이 중 어디에도 해당 안 함"을 확정하고 싶은 학생에게는
    # 방법이 없었음(사용자 지적). 이 값을 유저가 명시적으로 고르면 특수상황이 하나도 없다는
    # 뜻이라 — Scholarship.required_special_status에는 이 값이 절대 안 붙으므로(크롤링
    # 데이터에 이 값을 태그할 일이 없음) special_status_matches()의 교집합 검사에서 자연히
    # 항상 겹치지 않아 특수상황이 걸린 장학금은 걸러지고, 특수상황 조건이 없는 일반 장학금은
    # 그대로 다 보임 — matching.py 로직 변경 없이 이 값 하나 추가만으로 의도대로 동작함.
    # frontend/src/lib/spec.ts의 SPECIAL_STATUS_OPTIONS에 "해당사항 없음"으로 노출되고,
    # 다른 항목과는 상호배타적으로 골라지도록 프론트에서 처리함(다른 항목 고르면 이건 풀림,
    # 이걸 고르면 다른 항목들이 풀림).
    NOT_APPLICABLE = "not_applicable"  # 해당사항 없음

    # 2026-08-04 추가 — "확인 불가" 조건 태그(matching_gaps.md 5·6·7·14·14후속·15·16·17번).
    # 매칭 필드가 없어서 걸러줄 수 없는 조건들이라 전원 노출(과다노출) 정책은 그대로 유지하되,
    # core/matching.py의 랭킹 계산에서만 순위를 밀리게 하는 용도. **사용자가 절대 선택할 수
    # 없음 — frontend/src/lib/spec.ts의 SPECIAL_STATUS_OPTIONS에는 추가하지 않음**(크롤링
    # 데이터에만 태그). is_eligible()의 특수상황 체크에서는 이 8개를 제외하고 넘겨서, 노출
    # 여부에는 전혀 영향 안 주도록 함 — UNVERIFIABLE_CONDITIONS 상수와 그 사용처 참고.
    PARENT_OCCUPATION_CONDITION = "parent_occupation_condition"  # 부모의 특정 직업/소속 조건
    RELIGIOUS_OR_CAREER_INTENT_CONDITION = "religious_or_career_intent_condition"  # 종교기관 소속·직분·진로지향 조건
    SUB_REGION_RESIDENCE_CONDITION = "sub_region_residence_condition"  # 시/군/구 세부 거주지 조건
    # 출신 학교 소재지 기준 조건. 2026-08-06 범위 확장 — "현재 거주지가 아니라 출신지"라는
    # 점이 핵심이라, 특정 개별 학교(예: "북평고 졸업생만") 한정 조건이나 향우회 등 "타지
    # 거주해도 되는 출신지 기반" 조건(예: "영암 출신 향우자녀")도 같은 이유(현재 거주지
    # 매칭으로는 표현 불가)로 이 태그를 재사용함 — 전부 새 태그 없이 여기로 묶어서 처리.
    HOMETOWN_SCHOOL_REGION_CONDITION = "hometown_school_region_condition"  # 출신 학교/출신지 기준 조건(비거주 허용)
    SUNEUNG_SCORE_CONDITION = "suneung_score_condition"  # 수능성적 기반 조건
    SCHOOL_RECORD_CONDITION = "school_record_condition"  # 내신/입학성적 조건
    CREDIT_REQUIREMENT_CONDITION = "credit_requirement_condition"  # 이수학점 조건
    EXTRACURRICULAR_PROGRAM_CONDITION = "extracurricular_program_condition"  # 학교 자체 비교과 프로그램 이수 조건
    # 2026-08-06 추가 — 외부 장학금 3차 배치(지자체 재단 25곳) 조사 중 청송군·공주시·제주도
    # 3개 기관에서 독립적으로 발견된 조건. "의사상자 등 예우 및 지원에 관한 법률"(보건복지부
    # 소관) 상의 의사상자로 인정된 사람의 유족·가족 — national_merit(국가유공자, 국가보훈부
    # 소관)와는 근거 법률 자체가 달라 그쪽으로 분류하면 안 됨. matching_gaps.md 20번 참고.
    RIGHTEOUS_PERSON_FAMILY_CONDITION = "righteous_person_family_condition"  # 의사상자 유족·가족 조건


# is_eligible()에서 걸러줄 수 없는(=매칭 필드가 없는) 조건 태그 — special_status_matches()에
# 넘기기 전에 이 집합을 제외해야 함(안 그러면 학생이 다른 특수상황을 골랐을 때 이 태그가
# 붙은 장학금이 실수로 숨겨짐 — 노출 정책 회귀 방지). core/matching.py에서 씀.
UNVERIFIABLE_CONDITIONS: frozenset[SpecialStatus] = frozenset(
    {
        SpecialStatus.PARENT_OCCUPATION_CONDITION,
        SpecialStatus.RELIGIOUS_OR_CAREER_INTENT_CONDITION,
        SpecialStatus.SUB_REGION_RESIDENCE_CONDITION,
        SpecialStatus.HOMETOWN_SCHOOL_REGION_CONDITION,
        SpecialStatus.SUNEUNG_SCORE_CONDITION,
        SpecialStatus.SCHOOL_RECORD_CONDITION,
        SpecialStatus.CREDIT_REQUIREMENT_CONDITION,
        SpecialStatus.EXTRACURRICULAR_PROGRAM_CONDITION,
        SpecialStatus.RIGHTEOUS_PERSON_FAMILY_CONDITION,
    }
)


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
