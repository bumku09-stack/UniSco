from datetime import date

from sqlmodel import SQLModel

from app.models.enums import (
    AdmissionTrack,
    DegreeLevel,
    DisabilityType,
    DischargeType,
    EnrollmentStatus,
    Gender,
    LanguageTestType,
    MilitaryStatus,
    SpecialStatus,
)


class LanguageTestEntry(SQLModel):
    """어학점수 한 줄(종류+점수) — 2026-08-21 추가. UserSpec.language_tests가 이걸 리스트로
    가짐(토익+토플+JLPT처럼 여러 시험 동시 보유 가능하게 하기 위함, 사용자 요청). type이
    LanguageTestType 정식 값이 아니면 요청 자체가 422로 거부됨(프론트가 항상 정해진 값만
    보내므로 실사용 중엔 안 걸림 — enums.py의 LanguageTestType 참고)."""

    type: LanguageTestType
    score: float


class UserSpec(SQLModel):
    """/users/me/spec request/response body shape, and also POST /match's
    request body (게스트 즉석 매칭, 2026-08-10 재도입) — not a DB table itself.

    SavedSpec (app/models/saved_spec.py) is the persisted per-user table with
    the same field shape; to_user_spec() in core/matching.py converts one to
    the other.
    """

    # 2026-08-21 추가 — 매칭 조건으로는 안 쓰이고, "OOO님을 위한 장학금" 같은 개인화 표시용으로만
    # 저장함. None=아직 안 입력한 레거시 스펙(이 필드 추가 전 저장된 것).
    display_name: str | None = None
    # 2026-08-21 추가 — age(아래)를 대체하는 실제 입력 필드. age는 매칭에 계속 쓰이므로 필드
    # 자체는 남겨두고, 프론트가 이 값으로부터 만 나이를 계산해서 age를 채워 보냄
    # (frontend/src/lib/spec.ts의 specFormToUserSpec 참고) — 매칭 로직(core/matching.py)은
    # age만 보므로 전혀 안 건드림.
    birth_date: date | None = None
    university: str  # 소속 대학 (예: 충남대학교, KAIST) — GPA 만점 기준을 정하는 데도 씀
    college: str  # 단과대 (예: 공과대학)
    department: str | None = None  # 학과 (예: 컴퓨터공학과) — 2026-08-03 추가, matching_gaps.md 2번
    semester_gpa: float  # 직전 학기 평점평균 (해당 대학 만점 기준 원점수, 정규화는 matching.py에서)
    cumulative_gpa: float  # 전체 재학기간 누적 평점평균(CGPA) — 마찬가지로 원점수
    # 2026-08-12 추가 — GPA와 동일한 방식(학생 자기입력)으로 이수학점 조건도 실제 매칭에
    # 쓰기 위해 추가. None="입력 안 함/모름" — 이수학점 조건이 있는 장학금도 안 거름(GPA와
    # 달리 이 필드는 선택 입력, credits_matches() 참고).
    credits_last_semester: int | None = None
    age: int
    gender: Gender
    region: str
    # 2026-08-05 추가 (matching_gaps.md 14번) — 시/도(region)만으론 "정읍시 거주자만" 같은
    # 시/군/구 단위 지자체 장학금을 못 걸러서 추가함. 프론트에서 이미 물어보던 값인데 그동안
    # 서버로 안 보내고 버리고 있었음(frontend/src/lib/spec.ts 참고). 세종처럼 하위 구/군이
    # 없는 시/도는 빈 문자열/None일 수 있음.
    district: str | None = None
    # 2026-08-21 추가 — 주소 검색(AddressSearchField)으로 받은 전체 도로명주소. 매칭엔 안 쓰고
    # 표시/재입력 시 복원용(마이페이지에서 다시 열었을 때 검색해서 넣은 주소가 그대로 보이게).
    address: str | None = None
    # 2026-08-05 추가 (matching_gaps.md 19번) — "본인 또는 부모 중 1인이 OO에 거주" 조건을
    # 표현하기 위한 선택 입력. None="입력 안 함/모름" — 이때는 매칭에 아예 안 쓰이고 기존처럼
    # region(본인 거주지)만으로 판단함. core/matching.py의 region_matches() 참고.
    parent_region: str | None = None
    parent_district: str | None = None  # 2026-08-05 추가 (matching_gaps.md 14번 후속) — 부모 쪽 시/군/구 단위
    parent_address: str | None = None  # 2026-08-21 추가 — address와 동일한 이유, 부모님 쪽.
    # 2026-08-21 — 필수에서 선택 입력으로 변경(다른 선택 입력들과 같은 leniency 원칙 적용).
    # None="모름/미답변" — 이 조건이 걸린 장학금도 안 거름(core/matching.py의 is_eligible/
    # discharge_type_matches 참고). 프론트에서 병역 5종 중 이미 고른 걸 다시 누르면 선택
    # 해제되면서 이 값이 None으로 돌아감.
    military_status: MilitaryStatus | None = None
    # 2026-08-15 추가 — military_status가 completed(군필)일 때만 의미 있는 세부 구분(id=652
    # "10년 이상 장기복무 제대군인 대상" 발견 계기). None="입력 안 함/해당 없음"(군필 아니면
    # 항상 None) — 이 조건이 걸린 장학금도 안 거름(다른 선택 입력들과 같은 leniency 원칙).
    discharge_type: DischargeType | None = None
    income_bracket: int | None = None  # None="모름" — 소득분위 조건이 있는 장학금도 안 거름
    # 2026-08-22 — 병역과 같은 이유로 필수에서 선택 입력으로 변경. None="모름/안 건드림"
    # (leniency). True인데 disability_type에 NOT_APPLICABLE이 있으면 확정된 "아니오"로 취급
    # (core/matching.py의 disability_matches() 참고).
    has_disability: bool | None = None
    is_foreigner: bool

    enrollment_status: EnrollmentStatus
    grade: int | None = None  # enrollment_status가 학부재학/학부휴학일 때만 사용
    degree_level: DegreeLevel | None = None  # enrollment_status가 학부이후과정일 때만 사용
    # 2026-08-12 추가 — "무슨 학과인지"(department)와 별개인 "어떻게 입학했는지" 축. 프론트
    # 폼에서 기본값 "일반전형"으로 항상 채워서 보내지만, 혹시 None으로 오면(레거시 유저 등)
    # matching.py에서 GENERAL로 간주함(AdmissionTrack 참고, 대다수가 일반전형이라 과소매칭
    # 방지가 목적).
    admission_track: AdmissionTrack | None = None

    # 2026-08-02 추가 (matching_gaps.md 9·10·12번, 선택 입력).
    # 2026-08-21 — 시험 하나만 넣던 걸 여러 개 넣을 수 있게 변경(LanguageTestEntry 참고).
    # 빈 리스트=아직 하나도 안 넣음 — core/matching.py의 language_test_matches() 참고.
    language_tests: list[LanguageTestEntry] = []
    # 2026-08-21 — 단일 값에서 특수상황과 같은 복수선택으로 변경. has_disability=True일 때만
    # 의미 있고, 비어있으면(선택 안 함) 특수상황과 동일한 leniency 원칙 적용(장애 유형 조건이
    # 있는 장학금도 안 거름 — core/matching.py의 disability_matches() 참고).
    disability_type: list[DisabilityType] = []
    # 특수상황은 다중 선택 — 아예 비어있으면(선택 안 함) matching.py에서 특수상황 조건이
    # 있는 장학금도 걸러내지 않는 예외 처리가 됨(special_status_matches() 참고).
    special_status: list[SpecialStatus] = []


class SpecStatusResponse(SQLModel):
    spec_completed: bool
