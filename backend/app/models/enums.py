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
    # 2026-08-15 추가 — "학군사관후보생(ROTC) 대상" 조건인 장학금(id=63,212)이 있는데
    # 기존 3종 어디로도 표현이 안 됐음(ROTC 후보생은 임관 전이라 사실상 미필이지만, 미필
    # 학생 전체가 아니라 그중 ROTC 과정 중인 사람만 콕 집어 대상으로 하는 장학금이라
    # not_served로는 못 거름 — 군필이면 애초에 ROTC 후보생 신분이 성립 안 하므로 의미 없음).
    # frontend/src/lib/spec.ts의 병역 선택란에도 추가할 것.
    ROTC_CANDIDATE = "rotc_candidate"  # 학군사관후보생(ROTC)
    # 2026-08-21 추가 — 여성 등 기존 4종(군필/면제/미필/ROTC) 어디에도 자기 상황을 대입하기
    # 애매하다고 느끼는 사용자를 위한 명시적 선택지(SpecialStatus의 NOT_APPLICABLE과 같은
    # 패턴). "미필"로 대충 채우게 하지 않고 실제로 구분되는 값으로 저장 — required_military_status
    # 조건이 있는 장학금(예: "제대군인만")은 여전히 정상적으로 걸러짐(이 값은 그 어떤
    # required_military_status와도 안 같으므로).
    NOT_APPLICABLE = "not_applicable"  # 해당사항 없음


class DischargeType(str, Enum):
    """전역 구분 — 2026-08-15 추가(id=652 "제대군인대부지원", "10년 이상 장기복무 제대군인
    대상"에서 발견). military_status=completed(군필)일 때만 의미 있는 세부 구분이라 별도
    필드로 뺌(enrollment_status가 post_undergrad일 때만 의미 있는 degree_level과 동일한
    패턴) — military_status 자체에 합치면 "군필"이 두 갈래로 쪼개져서 기존 군필 단일값
    데이터(수백 건)를 전부 재분류해야 하는 불필요한 마이그레이션이 생김.
    frontend/src/lib/spec.ts의 병역 선택란에서 "군필" 고르면 이어서 나타나는 선택지."""

    ENLISTED = "enlisted"  # 병사 전역
    OFFICER_OR_NCO = "officer_or_nco"  # 장교/부사관 전역


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


class AdmissionTrack(str, Enum):
    """입학전형 유형 (2026-08-12 추가). `major`(전공)와는 완전히 다른 축 — "무슨 학과인지"가
    아니라 "어떻게 입학했는지"라서, 관련 학과 학생이어도 해당 전형으로 입학한 게 아니면
    조건을 못 채우고(반대로 그 전형으로 입학한 학생이 항상 관련 학과인 것도 아님, 예:
    우송대는 체육 관련 학과 자체가 없어서 major로는 표현 불가능했음). 이 필드가 생기기
    전에는 "체육특기자 전형 입학생 대상"류 조건을 `major`에 억지로 우회 매핑했다가, 국어국문
    학과 학생에게 체육특기자 장학금이 노출되는 사고로 이어짐(실사용자 UX 리서치에서 발견).

    지금까지 실제 DB에서 확인된 유형은 체육특기자 전형뿐이라 그것만 전용 값으로 두고,
    나머지(예능특기자 전형, 농어촌전형, 정원외특별전형 등— 실재하는 개념이지만 아직 이
    프로젝트 데이터에서 확인된 사례가 없음)는 `OTHER_SPECIALTY`로 뭉뚱그려 둠. 확인된 사례가
    2~3건 쌓이면 그때 전용 값으로 분리할 것(SpecialStatus가 커온 방식과 동일).
    `Scholarship.admission_track`이 None이면 전형 무관(제한 없음), 학생이 이 필드를 아직
    선택하지 않았으면(SavedSpec에 None) 매칭 시 `GENERAL`로 취급함 — 실제로 대다수 학생이
    일반전형이라(과소매칭 방지), "모르니 다 보여줌"이 아니라 "일반전형으로 간주"가 맞는
    기본값. core/matching.py의 admission_track_matches() 참고."""

    GENERAL = "general"  # 일반전형 (수시/정시 등 일반 입학) — 기본값
    ATHLETIC_SPECIALTY = "athletic_specialty"  # 체육특기자 전형
    OTHER_SPECIALTY = "other_specialty"  # 기타 특기자/특별전형 (예능특기·농어촌·정원외 등)


class LanguageTestType(str, Enum):
    """어학점수 조건 (matching_gaps.md 10번, 2026-08-02 구현). frontend/src/lib/spec.ts의
    LANGUAGE_TESTS와 값을 정확히 맞춰야 함 — 프론트가 이 문자열 그대로 보냄."""

    TOEIC = "TOEIC"
    TOEIC_SPEAKING = "TOEIC Speaking"  # 2026-08-21 추가
    TOEFL = "TOEFL"
    TOEFL_PBT = "TOEFL(PBT)"  # 2026-08-21 추가
    IELTS = "IELTS"
    TEPS = "TEPS"  # 2026-08-21 추가(뉴텝스, 600점 만점)
    TOPIK = "TOPIK"
    JLPT = "JLPT"  # 2026-08-21 추가(180점 만점, 급수 무관 공통)
    HSK = "HSK"  # 2026-08-21 추가(3~6급 기준 300점 만점)
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
    # 2026-08-22 추가 — SpecialStatus.NOT_APPLICABLE과 같은 패턴. 장애인 패널은 열었지만 실제로는
    # 해당 안 되는 학생을 위한 확정 선택지 — 이 값이 골라져 있으면 has_disability와 무관하게
    # 장애 조건 있는 장학금은 무조건 제외됨(core/matching.py의 disability_matches() 참고).
    # scholarship.required_disability_type(Postgres 네이티브 enum 컬럼)에는 절대 안 쓰이므로
    # 그 컬럼 타입(disabilitytype) 자체에는 이 값 추가 안 함 — SavedSpec.disability_type은
    # TEXT[]라 Python enum 값만 맞으면 되고 DB 마이그레이션이 필요 없음.
    NOT_APPLICABLE = "not_applicable"


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
    # 2026-08-10 추가 — 원래 "확인 불가" 랭킹 전용 태그였다가 여기로 승격함. "의사상자 등
    # 예우 및 지원에 관한 법률"(보건복지부 소관) 상의 의사상자로 인정된 사람의 유족·가족 —
    # national_merit(국가유공자, 국가보훈부 소관)와는 근거 법률이 달라 그쪽으로 합치면 안 됨.
    # national_merit과 똑같이 명확하게 정의된 법적 지위라 사용자가 직접 선택 가능한 항목으로
    # 두는 게 맞음(matching_gaps.md 20번, 2026-08-06에 "확인 불가"로 처음 추가됐던 것을
    # 재검토해서 승격). frontend/src/lib/spec.ts의 SPECIAL_STATUS_OPTIONS에도 추가할 것.
    RIGHTEOUS_PERSON_FAMILY_CONDITION = "righteous_person_family_condition"  # 의사상자 유족·가족
    # 2026-08-15 추가 — religious_or_career_intent_condition(확인 불가) 21건을 전수 재검토하다
    # 발견: 그중 8건은 "부모가 목회자 또는 선교사"라는, national_merit과 똑같이 학생이 예/
    # 아니오로 답할 수 있는 명확한 사실이었음(parent_university_staff/alumni 승격과 동일한
    # 이유). 나머지 13건은 학생 본인의 상태·지망(군종사관후보생, 신학대학원생+교회사역중,
    # 목회자/선교사 "지망" 등)이거나 추천서·신앙에세이처럼 정말 확인 불가한 절차 요건이라
    # 그대로 둠 — 이 태그로 옮긴 8건만 required_special_status에서
    # religious_or_career_intent_condition을 빼고 이걸로 교체함
    # (fix_promote_parent_clergy_2026-08-15.py 참고).
    PARENT_CLERGY_OR_MISSIONARY = "parent_clergy_or_missionary"  # 부모가 목회자·선교사
    # 2026-08-03 추가 — 배재대 희망복지장학금·대전대 장학사정관장학금 같은 복합조건
    # 장학금을 재분류하면서 새로 필요해진 값들
    BASIC_LIVELIHOOD_RECIPIENT = "basic_livelihood_recipient"  # 기초생활수급자
    NEAR_POOR = "near_poor"  # 차상위계층
    SEVERE_ILLNESS_OR_INJURY = "severe_illness_or_injury"  # 중증질병 및 상해
    JOB_LOSS_OR_DISASTER = "job_loss_or_disaster"  # 실직가정·재난 및 재해
    FINANCIAL_EMERGENCY = "financial_emergency"  # 긴급가계곤란
    # 2026-08-12 추가 — 경쟁 서비스(이루리) 회원가입 폼 검토 중 발견. 학생 본인이 "농어촌(읍·면)
    # 출신"이라는 명확한 자기신고 가능 사실이라 선택 가능 항목으로 바로 추가함(확인 불가로
    # 거칠 필요 없음). "농업인 자녀"(부모 직업)와는 다른 개념이니 섞지 말 것 — 그건
    # parent_occupation_condition(확인 불가) 영역.
    RURAL_STUDENT = "rural_student"  # 농어촌(읍·면) 출신 학생
    # 2026-08-12 추가 — 34건의 parent_occupation_condition(확인 불가) 태그를 전수 재검토하다
    # 발견: 그중 10건은 "아무 직업"이 아니라 정확히 "본인이 재학 중인 그 대학의 교직원/동문
    # 자녀"라는, eligible_university와 엮이는 훨씬 구체적이고 검증 가능한 조건이었음(예:
    # "배재학당 소속 교직원의 자녀"). 이건 학생이 "우리 학교 교직원/동문 자녀인가요"에 예/
    # 아니오로 답할 수 있는 성격이라 확인 불가로 둘 이유가 없음. staff/alumni를 분리한 이유는
    # 실제 데이터에 "교직원만 해당"과 "동문만 해당"이 조건이 다른 채로 섞여 있어서(둘 다
    # 해당하는 경우는 required_special_status에 둘 다 넣으면 됨).
    PARENT_UNIVERSITY_STAFF = "parent_university_staff"  # 부모가 재학 대학(원) 교직원
    PARENT_UNIVERSITY_ALUMNI = "parent_university_alumni"  # 부모가 재학 대학(원) 동문(졸업생)
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

    # 2026-08-04 추가 — "확인 불가" 조건 태그(matching_gaps.md 5·6·7·14후속·15·16·17번).
    # 매칭 필드가 없어서 걸러줄 수 없는 조건들이라 전원 노출(과다노출) 정책은 그대로 유지하되,
    # core/matching.py의 랭킹 계산에서만 순위를 밀리게 하는 용도. **사용자가 절대 선택할 수
    # 없음 — frontend/src/lib/spec.ts의 SPECIAL_STATUS_OPTIONS에는 추가하지 않음**(크롤링
    # 데이터에만 태그). is_eligible()의 특수상황 체크에서는 이 태그들을 제외하고 넘겨서, 노출
    # 여부에는 전혀 영향 안 주도록 함 — UNVERIFIABLE_CONDITIONS 상수와 그 사용처 참고.
    # (14번 "시/군/구 세부 거주지"는 2026-08-05 district/parent_district 매칭으로 실제
    # 해결돼서 태그 자체를 없앰 — region_matches() 참고, 운영 DB에도 0건이었음.)
    PARENT_OCCUPATION_CONDITION = "parent_occupation_condition"  # 부모의 특정 직업/소속 조건
    RELIGIOUS_OR_CAREER_INTENT_CONDITION = "religious_or_career_intent_condition"  # 종교기관 소속·직분·진로지향 조건
    # 출신 학교 소재지 기준 조건. 2026-08-06 범위 확장 — "현재 거주지가 아니라 출신지"라는
    # 점이 핵심이라, 특정 개별 학교(예: "북평고 졸업생만") 한정 조건이나 향우회 등 "타지
    # 거주해도 되는 출신지 기반" 조건(예: "영암 출신 향우자녀")도 같은 이유(현재 거주지
    # 매칭으로는 표현 불가)로 이 태그를 재사용함 — 전부 새 태그 없이 여기로 묶어서 처리.
    # 2026-08-10 재검토: 이 태그로 묶인 7건을 실제로 확인해보니 지역(예: 폐광지역 7개 시/군
    # 소재 고교 졸업)으로 표현 가능한 건 2건뿐이고, 나머지는 특정 개별 학교 한정(고교 목록
    # 자체가 없음)·향우회 가입+추천서 필요·농어촌특별전형 여부(거주지가 아니라 입시전형
    # 종류) 등 지역 필드 하나로는 못 푸는 서로 다른 종류라 hometown_region 필드를 새로 만들어도
    # 대부분 안 풀림 — 그래서 필드 추가 없이 "확인 불가"로 유지하기로 함.
    HOMETOWN_SCHOOL_REGION_CONDITION = "hometown_school_region_condition"  # 출신 학교/출신지 기준 조건(비거주 허용)
    SUNEUNG_SCORE_CONDITION = "suneung_score_condition"  # 수능성적 기반 조건
    SCHOOL_RECORD_CONDITION = "school_record_condition"  # 내신/입학성적 조건
    CREDIT_REQUIREMENT_CONDITION = "credit_requirement_condition"  # 이수학점 조건
    EXTRACURRICULAR_PROGRAM_CONDITION = "extracurricular_program_condition"  # 학교 자체 비교과 프로그램 이수 조건


# is_eligible()에서 걸러줄 수 없는(=매칭 필드가 없는) 조건 태그 — special_status_matches()에
# 넘기기 전에 이 집합을 제외해야 함(안 그러면 학생이 다른 특수상황을 골랐을 때 이 태그가
# 붙은 장학금이 실수로 숨겨짐 — 노출 정책 회귀 방지). core/matching.py에서 씀.
UNVERIFIABLE_CONDITIONS: frozenset[SpecialStatus] = frozenset(
    {
        SpecialStatus.PARENT_OCCUPATION_CONDITION,
        SpecialStatus.RELIGIOUS_OR_CAREER_INTENT_CONDITION,
        SpecialStatus.HOMETOWN_SCHOOL_REGION_CONDITION,
        SpecialStatus.SUNEUNG_SCORE_CONDITION,
        SpecialStatus.SCHOOL_RECORD_CONDITION,
        SpecialStatus.CREDIT_REQUIREMENT_CONDITION,
        SpecialStatus.EXTRACURRICULAR_PROGRAM_CONDITION,
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
