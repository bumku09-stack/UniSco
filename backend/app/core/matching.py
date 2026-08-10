import datetime
import re

from app.models import (
    UNVERIFIABLE_CONDITIONS,
    EnrollmentStatus,
    ForeignerEligibility,
    GpaBasis,
    SavedSpec,
    Scholarship,
    SpecialStatus,
    UserSpec,
)


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
    "을지대학교": 4.5,
    "대전대학교": 4.5,
    "한국침례신학대학교": 4.5,
}
DEFAULT_GPA_SCALE = 4.5


def normalized_gpa(gpa: float, university: str) -> float:
    scale = UNIVERSITY_GPA_SCALE.get(university, DEFAULT_GPA_SCALE)
    return gpa * (4.5 / scale)


def gpa_matches(scholarship: Scholarship, spec: UserSpec) -> bool:
    """min_gpa_basis가 직전학기/전체누적 중 무엇을 요구하는지에 따라 그쪽 GPA만 비교함
    (2026-08-02 추가 — matching_gaps.md 13번, 우송대 재검증 중 발견). 아직 basis를
    분류 안 한(None) 장학금은 기존 크롤링 데이터 대부분이 여기 해당하는데, 직전학기·
    전체누적 둘 중 하나라도 기준을 만족하면 통과시키는 관대한 기본값으로 처리함 —
    실제로는 둘 중 하나 기준일 텐데 어느 쪽인지 몰라서 학생을 잘못 걸러내는 것보다
    낫다는 판단(과다매칭이 과소매칭보다 덜 해로움)."""
    if scholarship.min_gpa is None:
        return True
    threshold = scholarship.min_gpa
    if scholarship.min_gpa_basis == GpaBasis.SEMESTER:
        return normalized_gpa(spec.semester_gpa, spec.university) >= threshold
    if scholarship.min_gpa_basis == GpaBasis.CUMULATIVE:
        return normalized_gpa(spec.cumulative_gpa, spec.university) >= threshold
    if scholarship.min_gpa_basis == GpaBasis.BOTH:
        # 직전학기·전체누적 둘 다 개별적으로 기준을 만족해야 함 (2026-08-02 을지대
        # "차세대의료인장학금" 등에서 발견 — matching_gaps.md 13번 후속).
        return (
            normalized_gpa(spec.semester_gpa, spec.university) >= threshold
            and normalized_gpa(spec.cumulative_gpa, spec.university) >= threshold
        )
    return (
        normalized_gpa(spec.semester_gpa, spec.university) >= threshold
        or normalized_gpa(spec.cumulative_gpa, spec.university) >= threshold
    )


def language_test_matches(scholarship: Scholarship, spec: UserSpec) -> bool:
    """어학점수 조건 (matching_gaps.md 10번). 3페이지의 다른 "선택 입력" 항목들(소득분위·
    특수상황)과 같은 원칙으로 통일함(2026-08-04) — 학생이 어학점수를 아예 안 넣었으면
    "해당 없음"이 아니라 "아직 모름"으로 보고 걸러내지 않음(이전엔 스펙 3페이지가 선택
    입력이라는 설계 의도와 반대로, 안 넣으면 그 조건 걸린 장학금이 전부 숨겨지는 버그가
    있었음). 학생이 실제로 다른 시험 종류를 입력한 경우(예: 장학금은 TOEFL을 요구하는데
    학생은 TOEIC 점수를 넣은 경우)는 여전히 진짜 불일치라 그대로 제외함 — "안 넣음"과
    "다른 시험 넣음"을 구분하는 게 핵심."""
    if scholarship.language_test_type is None:
        return True
    if spec.language_test_type is None:
        return True
    if spec.language_test_type != scholarship.language_test_type:
        return False
    if spec.language_test_score is None:
        return False
    if scholarship.language_test_min_score is None:
        return True
    return spec.language_test_score >= scholarship.language_test_min_score


def disability_matches(scholarship: Scholarship, spec: UserSpec) -> bool:
    """장애인 조건 전체(본인 장애 여부 + 세부유형, matching_gaps.md 12번)를 한 번에 확인.
    requires_disability/required_disability_type 둘 다 안 걸려있으면 무조건 통과."""
    if not scholarship.requires_disability and scholarship.required_disability_type is None:
        return True
    if not spec.has_disability:
        return False
    if (
        scholarship.required_disability_type is not None
        and spec.disability_type != scholarship.required_disability_type
    ):
        return False
    return True


def special_status_matches(
    scholarship_special_status: list[SpecialStatus], spec_special_status: list[SpecialStatus]
) -> bool:
    """특수상황 (matching_gaps.md 9번) — 다른 필드들과 다른 예외 규칙(2026-08-02 사용자 확정):
    유저가 특수상황을 아예 선택 안 했으면(빈 리스트) "아직 대답 안 한 것"으로 보고, 특수상황
    조건이 걸려있는 장학금도 걸러내지 않고 그냥 다 보여줌. 유저가 1개 이상 선택했을 때만
    그 항목 기준으로 필터링 시작함. 특수상황 조건이 없는 일반 장학금은 이 로직과 무관하게
    항상 통과.

    scholarship_special_status는 리스트(2026-08-03 변경, 배재사랑장학금처럼 "새터민 또는
    다문화가정" 등 여러 특수상황이 OR로 묶인 장학금을 표현하기 위함) — 유저가 선택한 것들과
    하나라도 겹치면 통과."""
    if not scholarship_special_status:
        return True
    if not spec_special_status:
        return True
    return bool(set(scholarship_special_status) & set(spec_special_status))


def special_status_matches_strict(
    scholarship_special_status: list[SpecialStatus], spec_special_status: list[SpecialStatus]
) -> bool:
    """special_status_matches의 "유저가 아예 선택 안 하면 통과" 예외를 빼고, 유저가 실제로
    선택한 것과 겹치는지만 봄. 장애 조건과 OR로 묶일 때만 이 엄격 버전을 씀 — 안 그러면
    (has_disability=False처럼 이미 확실히 "아니오"인 필드가 있는데도) 특수상황 쪽 "빈 선택 =
    통과" 예외 때문에 OR 전체가 사실상 항상 True가 돼버려서 장애 조건이 무의미해짐."""
    if not scholarship_special_status:
        return True
    return bool(set(scholarship_special_status) & set(spec_special_status))


def _verifiable_special_status(scholarship: Scholarship) -> list[SpecialStatus]:
    """required_special_status에서 학생이 절대 고를 수 없는 "확인 불가" 태그
    (UNVERIFIABLE_CONDITIONS)를 뺀 나머지만 반환. 자격 거름(노출 여부) 판단은 항상 이것만
    써야 함 — 안 그러면 학생이 다른 특수상황을 골랐을 때 "확인 불가" 태그만 붙은 장학금이
    실수로 숨겨짐(노출 정책 회귀). "확인 불가" 태그 자체는 랭킹 계산(unverifiable_condition_count)
    에서만 씀."""
    return [s for s in scholarship.required_special_status if s not in UNVERIFIABLE_CONDITIONS]


def disability_or_special_status_matches(scholarship: Scholarship, spec: UserSpec) -> bool:
    """장애 조건과 특수상황 조건이 둘 다 걸려있는 장학금(예: 배재대 "배재사랑장학금" — 장애학생
    또는 다문화가정 학생 대상)은 각각 따로 AND로 걸면 틀림 — 실제로는 "둘 중 하나만 만족해도
    통과"하는 OR 조건이라, 이 경우만 예외적으로 OR로 처리함(2026-08-03, 사용자 확정). 둘 중
    하나만 걸려있으면(대부분의 장학금) 평소처럼 그 조건만 확인."""
    verifiable_special_status = _verifiable_special_status(scholarship)
    has_disability_condition = scholarship.requires_disability or (
        scholarship.required_disability_type is not None
    )
    has_special_status_condition = bool(verifiable_special_status)
    if has_disability_condition and has_special_status_condition:
        return disability_matches(scholarship, spec) or special_status_matches_strict(
            verifiable_special_status, spec.special_status
        )
    return disability_matches(scholarship, spec) and special_status_matches(
        verifiable_special_status, spec.special_status
    )


def major_matches(scholarship: Scholarship, spec: UserSpec) -> bool:
    """전공/학과 조건 (matching_gaps.md 2번, 2026-08-03 구현). 장학금 쪽 `major`는 크롤링
    원문 그대로라 콤마로 여러 학과가 나열된 경우가 있음(예: "융합디자인전공,회화전공,
    미술교육과") — 그 중 하나라도 유저 학과와 일치하면 통과.

    가운뎃점(·)은 콤마와 똑같이 구분자로 쓰일 때도 있지만(예: 서술형 "국어·수학·탐구"),
    "국어국문·창작학과"·"법·행정학부"처럼 학과/학부 이름 자체에 가운뎃점이 들어간 경우도
    많아서(`frontend/src/lib/universities.ts` 참고) 무조건 쪼개면 그 학과 학생이 자기
    이름과 정확히 일치하는 항목을 못 찾아 매칭에서 빠지는 문제가 있었음(2026-08-03 발견).
    그래서 콤마로 나눈 한 조각을 통째로도 후보에 넣고, 그 조각을 가운뎃점으로 다시 쪼갠
    부분들도 같이 후보에 넣어서 어느 쪽 해석이든 맞으면 통과시킴(과다매칭이 과소매칭보다
    덜 해로움 — gpa_matches와 동일한 원칙)."""
    if not scholarship.major:
        return True
    if not spec.department:
        return False
    candidates: set[str] = set()
    for chunk in scholarship.major.split(","):
        chunk = chunk.strip()
        candidates.add(chunk)
        if "·" in chunk:
            candidates.update(part.strip() for part in chunk.split("·"))
    return spec.department in candidates


def deadline_matches(scholarship: Scholarship, today: datetime.date | None = None) -> bool:
    """마감일 자동 정리 (matching_gaps.md 7번, 2026-08-03 구현). application_deadline이
    구조화된 값으로 채워진 장학금만 자동으로 걸러짐 — 대부분의 기존 데이터는 "매 학기 초
    공지"류 상시/반복 프로그램이라 NULL로 남아있고, 그런 건 지금처럼 계속 다 보임."""
    if scholarship.application_deadline is None:
        return True
    return scholarship.application_deadline >= (today or datetime.date.today())


_SIDO_NAMES = [
    "서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
    "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주",
]


def region_matches(scholarship: Scholarship, spec: UserSpec) -> bool:
    """거주지 조건 (matching_gaps.md 14번·19번, 2026-08-05). eligible_region 하나에 두 가지
    다른 정밀도가 섞여서 저장됨 — 시/도 단위(예: "충남", "대전·충남·충북·세종")와, 시/도로
    좁히면 과다매칭이라 그동안 못 채우고 있던 시/군/구 단위(예: "정읍시", 14번 갭 — "부 또는
    모 1인이 정읍시에 1년 이상 거주"). 어느 쪽이든 "eligible_region 문자열 안에 이 후보가
    부분 문자열로 들어있는지"만 보면 같은 방식으로 처리 가능해서(구/군 이름이 시/도
    shortName의 부분 문자열이 되는 경우는 없음), 후보 4개(본인 시/도, 본인 시/군/구, 부모
    시/도, 부모 시/군/구)를 전부 OR로 검사함 — 지자체 장학금 대부분이 "본인 또는 부모"
    조건이라(19번) 시/군/구 쪽도 부모 후보까지 봐야 정읍시민장학재단 같은 케이스가 제대로
    걸러짐. district/parent_district가 없으면(None) 그 후보는 그냥 건너뜀 — 다른 선택
    입력들과 마찬가지로 "몰라서 안 넣음"을 "해당 지역 아님"으로 단정하지 않음.

    2026-08-07 추가 — "중구" 충돌 버그 수정: "중구"처럼 여러 시/도에 동시에 있는 구/군
    이름은(서울·부산·대구·인천·대전·울산 전부 "중구"가 있음) 구/군 이름만 부분 문자열로
    비교하면 완전히 다른 도시 사용자에게도 걸림 — 실제 사고: 대전 중구 거주자한테
    "인천광역시 중구·미추홀구·연수구" 한정 장학금(eligible_region에 예외적으로 시/도 이름이
    같이 박혀 있던 케이스)이 노출됨. eligible_region 안에 시/도 이름이 하나라도 있으면,
    구/군 후보가 매칭되더라도 그 구/군에 대응하는 사용자 시/도(spec.region 또는
    spec.parent_region)가 그 시/도 이름과 같은지까지 추가로 확인함. eligible_region에
    시/도 이름이 없으면(기존 컨벤션 — 구/군 이름만 넣는 게 정상, 예: "정읍시") 이 추가
    확인 없이 기존 방식 그대로 동작 — 대다수 케이스는 영향 없음."""
    if scholarship.eligible_region is None:
        return True
    region = scholarship.eligible_region
    named_sido = [s for s in _SIDO_NAMES if s in region]

    def district_ok(sido: str | None) -> bool:
        if not named_sido:
            return True
        return bool(sido) and sido in named_sido

    # 빈 문자열("")은 세종처럼 하위 구/군이 없는 경우의 district 기본값인데, 빈 문자열은
    # 어떤 문자열에도 항상 부분 문자열로 포함되기 때문에(`"" in "충남"` == True) 그대로
    # 후보에 넣으면 지역 조건이 있는 장학금이 전부 통과해버리는 심각한 버그가 됨 — 빈
    # 문자열은 "값 없음"과 동일하게 취급해서 제외함.
    candidates = [
        (spec.region, True),
        (spec.district, district_ok(spec.region)),
        (spec.parent_region, True),
        (spec.parent_district, district_ok(spec.parent_region)),
    ]
    return any(c and ok and c in region for c, ok in candidates)


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
    if not region_matches(scholarship, spec):
        return False
    if (
        scholarship.required_military_status is not None
        and scholarship.required_military_status != spec.military_status
    ):
        return False
    if (
        scholarship.max_income_bracket is not None
        and spec.income_bracket is not None
        and spec.income_bracket > scholarship.max_income_bracket
    ):
        return False
    if not gpa_matches(scholarship, spec):
        return False
    if not disability_or_special_status_matches(scholarship, spec):
        return False
    if not language_test_matches(scholarship, spec):
        return False
    if not major_matches(scholarship, spec):
        return False
    if not deadline_matches(scholarship):
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


def confirmed_match_count(scholarship: Scholarship, spec: UserSpec) -> int:
    """이 학생 스펙으로 "진짜 확인된" 매칭 조건 개수 (2026-08-04, specificity_score를
    대체함 — 기존 버전은 "장학금이 조건을 얼마나 많이 걸었나"만 셌지 "나랑 얼마나 잘
    맞나"는 안 쟀음, 사용자 지적으로 재설계). 여기까지 오는 장학금은 이미 is_eligible을
    통과했으므로, 장학금이 조건을 걸어놓은 항목은 원칙적으로 전부 "확인된 매칭"임 —
    **단, 학생이 "모름/안 입력"을 고를 수 있는 선택 입력 3개(소득분위·어학점수·특수상황)는
    예외**: 그 조건은 leniency 규칙 덕분에 통과된 것뿐일 수 있어서, 학생이 실제로 값을
    입력했을 때만 센다. 새로 추가된 "확인 불가" 태그(UNVERIFIABLE_CONDITIONS)는 여기서
    아예 제외하고 unverifiable_condition_count()로만 감."""
    score = 0
    if scholarship.min_age is not None or scholarship.max_age is not None:
        score += 1
    if scholarship.required_gender is not None:
        score += 1
    if scholarship.eligible_region is not None:
        score += 1
    if scholarship.required_military_status is not None:
        score += 1
    if scholarship.max_income_bracket is not None and spec.income_bracket is not None:
        score += 1
    if scholarship.min_gpa is not None:
        score += 1
    if scholarship.requires_disability:
        score += 1
    if scholarship.required_disability_type is not None:
        score += 1
    if scholarship.foreigner_eligibility is not None:
        score += 1
    if scholarship.language_test_type is not None and spec.language_test_type is not None:
        score += 1
    if _verifiable_special_status(scholarship) and spec.special_status:
        score += 1
    if scholarship.major is not None:
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


def unverifiable_condition_count(scholarship: Scholarship, spec: UserSpec) -> int:
    """이 장학금에 "확인 안 되는" 조건이 몇 개 있는지 (2026-08-04 추가, 08-04 확장).
    두 가지를 합쳐서 셈:
    1. 목회자 자녀·부모 직업·시군구 세부거주·의사상자 유족 등 매칭 필드 자체가 없는 "확인
       불가" 태그(UNVERIFIABLE_CONDITIONS, 2026-08-06 기준 9개).
    2. **필드는 있지만 이 학생이 아직 안 답한 선택 입력 조건**(소득분위 모름/특수상황 안 고름/
       어학점수 안 넣음)이 이 장학금에 걸려있는 경우 — 처음엔 confirmed_match_count()에서
       "보너스 점수를 안 주는" 것까지만 했었는데, 그것만으론 부족했음(다른 조건이 잘 맞으면
       보너스 없이도 여전히 위로 뜸 — 예: "북한이탈주민 대상" 조건이 있어도 특수상황을
       안 고른 학생한텐 그냥 다른 조건들만으로 순위가 매겨져서 상단에 뜨는 문제가 실사용
       중 발견됨). 그래서 "확인 불가 태그"랑 똑같이 여기서도 감점 대상에 포함시킴 — 노출
       여부는 그대로 유지하고(과다노출 정책 불변) 순위만 밀림.

    학생이 실제로 답했는데 장학금 조건과 안 맞는 경우는 애초에 is_eligible()에서 걸러져서
    여기까지 안 옴 — 그러니 "학생이 답 안 해서 leniency로 통과된 것"만 정확히 골라내는 것."""
    count = len([s for s in scholarship.required_special_status if s in UNVERIFIABLE_CONDITIONS])
    if _verifiable_special_status(scholarship) and not spec.special_status:
        count += 1
    if scholarship.max_income_bracket is not None and spec.income_bracket is None:
        count += 1
    if scholarship.language_test_type is not None and spec.language_test_type is None:
        count += 1
    return count


def personal_fit_key(scholarship: Scholarship, spec: UserSpec) -> tuple[float, int]:
    """랭킹 정렬 키. (ratio, confirmed) 튜플을 둘 다 내림차순으로 정렬함.

    ratio = confirmed / (confirmed + unverifiable) — "확인 불가" 조건이 없는 장학금들은
    분모=분자라 전부 ratio 1.0으로 동률이 되고(is_eligible을 이미 통과했으니 그 장학금이
    건 조건은 다 확인된 것이므로), 그 안에서는 confirmed 값으로 순위가 갈림. "확인 불가"
    조건이 하나라도 있으면 분모만 커져서 ratio가 1.0 밑으로 내려가 자동으로 뒤로 밀림 —
    "확인된 것끼리는 개수로, 확인 안 되는 게 섞이면 무조건 그 아래로" 규칙을 하나의 정렬
    키로 표현한 것."""
    confirmed = confirmed_match_count(scholarship, spec)
    unverifiable = unverifiable_condition_count(scholarship, spec)
    total = confirmed + unverifiable
    ratio = confirmed / total if total > 0 else 1.0
    return (ratio, confirmed)


def match_scholarships(scholarships: list[Scholarship], spec: UserSpec) -> list[Scholarship]:
    eligible = [s for s in scholarships if is_eligible(s, spec)]
    eligible.sort(key=lambda s: personal_fit_key(s, spec), reverse=True)
    return eligible


_TOKEN_RE = re.compile(r"[\w가-힣]+")


def _tokenize(text: str | None) -> set[str]:
    return set(_TOKEN_RE.findall(text.lower())) if text else set()


def _wording_similarity(a: Scholarship, b: Scholarship) -> int:
    """이름+설명을 단순 토큰화해서 겹치는 단어 수를 셈 — 정교한 추천이 아니라, 같은 중분류/
    대분류가 하나도 없을 때 그나마 워딩이 비슷한 것부터 보여주기 위한 최후 fallback 정렬 기준."""
    tokens_a = _tokenize(a.name) | _tokenize(a.description)
    tokens_b = _tokenize(b.name) | _tokenize(b.description)
    return len(tokens_a & tokens_b)


def find_similar(
    target: Scholarship,
    eligible: list[Scholarship],
    limit: int = 3,
    exclude_id: int | None = None,
) -> list[Scholarship]:
    """상세페이지 "이런 장학금은 어때요?" 추천(2026-08-03 설계). 후보를 "내 조건에 맞는(이미
    match_scholarships를 통과한) 장학금"으로만 한정한 뒤, 같은 중분류(category_l2) 우선 →
    대분류(category_l1)로 확장 → 그래도 부족하면 나머지 전체에서 워딩(이름+설명 텍스트 겹침)이
    비슷한 순으로 채움. exclude_id는 A→B로 넘어왔을 때 B의 추천 목록에 A가 다시 뜨는 핑퐁을
    막기 위함(프론트가 ?from= 쿼리로 넘겨줌)."""
    others = [s for s in eligible if s.id != target.id and s.id != exclude_id]

    same_l2 = (
        [s for s in others if s.category_l2 == target.category_l2]
        if target.category_l2 is not None
        else []
    )
    same_l2_ids = {s.id for s in same_l2}
    same_l1 = (
        [s for s in others if s.category_l1 == target.category_l1 and s.id not in same_l2_ids]
        if target.category_l1 is not None
        else []
    )
    picked_ids = same_l2_ids | {s.id for s in same_l1}
    rest = sorted(
        (s for s in others if s.id not in picked_ids),
        key=lambda s: _wording_similarity(target, s),
        reverse=True,
    )

    return (same_l2 + same_l1 + rest)[:limit]
