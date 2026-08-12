"""파이프라인 각 단계를 오가는 데이터 구조.

여기 정의된 dataclass들이 harness/의 모든 모듈이 공유하는 "계약"임 — collect_links.py가
Listing을 만들고, extract.py가 ExtractedScholarship을 만들고, verify.py가 그걸
VerifiedScholarship으로 바꾸고, build_pr.py가 그걸 읽어서 SQL/마크다운을 만듦.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# backend/app/models/scholarship.py의 Scholarship 컬럼과 정확히 일치해야 함(id 제외).
# 새 필드를 여기 추가하고 싶으면 먼저 backend 쪽 모델/DB 컬럼부터 추가할 것 — 하네스가
# 스키마를 앞서가면 안 됨(설계안 "새 필드 추가 금지" 원칙).
SCHOLARSHIP_FIELD_NAMES: tuple[str, ...] = (
    "name",
    "provider",
    "description",
    "amount",
    "application_url",
    "min_age",
    "max_age",
    "required_gender",
    "eligible_region",
    "required_military_status",
    "max_income_bracket",
    "min_gpa",
    "min_gpa_basis",
    "requires_disability",
    "required_disability_type",
    "foreigner_eligibility",
    "language_test_type",
    "language_test_min_score",
    "required_special_status",
    "required_special_status_all",
    "excluded_special_status",
    "application_deadline",
    "grade_level",
    "major",
    "excluded_major",
    "admission_track",
    "affiliated_institution",
    "min_credits",
    "admission_score_condition",
    "headcount",
    "application_period",
    "eligible_university",
    "eligible_college",
    "required_enrollment_status",
    "min_grade",
    "max_grade",
    "required_degree_level",
    "category_l1",
    "category_l2",
)

# 값을 안 채워도(=원문 근거 없음) 정상인 필드 — 리스트 필드들은 "빈 리스트=조건 없음"이
# 정상값이라 not_applicable 판정 시 빈 문자열이 아니라 빈 리스트가 "값 없음"의 기준이 됨.
LIST_VALUED_FIELDS: frozenset[str] = frozenset(
    {"required_special_status", "required_special_status_all", "excluded_special_status"}
)


@dataclass
class Listing:
    """collect_links.py가 게시판에서 모은 공고 하나."""

    url: str
    title: str
    university: str
    department: str | None = None  # None이면 대학 공통 게시판
    board_name: str = ""


@dataclass
class CollectionResult:
    """게시판 하나를 순회한 결과 — "다 봤는지"를 코드가 판단한 증거를 담음."""

    university: str
    board_name: str
    listings: list[Listing]
    expected_count: int | None  # 게시판이 표시한 총 게시물 수 (파싱 실패 시 None)
    actual_count: int
    ok: bool  # expected_count == actual_count (파싱 자체가 안 됐으면 False)
    note: str = ""


@dataclass
class ExtractedField:
    """LLM이 반환한 필드 하나 — 값과 그 근거가 된 원문 인용을 항상 같이 들고 있음."""

    value: Any
    source_quote: str


@dataclass
class ExtractedScholarship:
    """extract.py의 단일 호출 결과 (문서 1건 = 이 객체 1개, 상태 없음)."""

    source_url: str
    fields: dict[str, ExtractedField]

    def get(self, name: str) -> ExtractedField:
        return self.fields[name]


@dataclass
class VerifiedField:
    """verify.py가 ExtractedField를 기계적으로 검증한 결과."""

    name: str
    value: Any
    source_quote: str
    status: str  # "confirmed" | "needs_review" | "not_applicable"
    reason: str = ""
    # not_applicable: 값이 없고 인용도 없음(원문에 근거 없어서 정상적으로 비운 케이스) — 플래그 아님.
    # confirmed: 인용문이 원문에 실제로 존재함(정확 일치 또는 퍼지 매치).
    # needs_review: 값은 있는데 인용이 없거나(no_quote), 인용이 원문에 없거나(quote_not_found),
    #               2중 추출 결과가 서로 다름(dual_extract_mismatch).


@dataclass
class VerifiedScholarship:
    """build_pr.py가 SQL/리뷰 마크다운을 만드는 데 쓰는 최종 산출물."""

    source_url: str
    listing_title: str
    fields: dict[str, VerifiedField]

    @property
    def flagged_fields(self) -> list[VerifiedField]:
        return [f for f in self.fields.values() if f.status == "needs_review"]

    @property
    def has_flags(self) -> bool:
        return len(self.flagged_fields) > 0

    def value(self, name: str) -> Any:
        return self.fields[name].value
