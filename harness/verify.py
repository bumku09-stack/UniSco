"""Layer 1 — 자동 검증. **LLM 자기 검증이 아님.**

원칙 2 구현부: extract.py가 반환한 source_quote가 실제로 원문(추출된 텍스트) 안에 있는지
코드가 문자열로 대조한다. LLM에게 "이 값이 맞는지 확인해봐"라고 다시 묻지 않는다 — 모델이
값을 지어낼 때는 그 근거 문장까지 원문 그대로 지어내기 어렵고, 지어내더라도 원문에 없는
문장이라 여기서 바로 걸러진다(설계안 3.2절).

숫자 핵심 필드는 여기서 2중 추출 결과끼리도 추가로 대조한다(설계안 7.2절, 대상 필드 목록은
harness/config.py의 DUAL_EXTRACT_FIELDS).
"""
from __future__ import annotations

import re
import unicodedata

from rapidfuzz import fuzz

from harness import config
from harness.models import (
    LIST_VALUED_FIELDS,
    ExtractedScholarship,
    VerifiedField,
    VerifiedScholarship,
)

_WHITESPACE_RE = re.compile(r"\s+")
_PUNCT_RE = re.compile(r"[·,\.;:!?\"'()\[\]{}~\-]")


def _normalize(text: str) -> str:
    """공백 collapse + 일부 문장부호 제거 — "약간의 편집 거리(공백/문장부호 차이) 허용"의
    1단계. 이 정규화만으로 맞으면 "exact"로 취급함(진짜 편집 거리 허용이 아니라 표기 차이
    흡수일 뿐이라 신뢰도를 낮출 이유가 없음)."""
    text = unicodedata.normalize("NFKC", text)
    text = _PUNCT_RE.sub("", text)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text


def quote_exists_in_source(quote: str, source_text: str) -> tuple[bool, str]:
    """(발견 여부, "exact" | "fuzzy" | "not_found").

    1단계: 정규화 후 완전 포함 여부.
    2단계(config.QUOTE_FUZZY_MATCH_ENABLED일 때만): 그래도 없으면 rapidfuzz.partial_ratio로
    원문 어딘가에 이 인용문과 임계값(config.QUOTE_FUZZY_MIN_RATIO) 이상 비슷한 부분이 있는지
    확인 — 진짜 편집 거리 허용은 여기서만 일어남.
    """
    if not quote.strip():
        return False, "not_found"

    normalized_quote = _normalize(quote)
    normalized_source = _normalize(source_text)
    if normalized_quote in normalized_source:
        return True, "exact"

    if config.QUOTE_FUZZY_MATCH_ENABLED:
        score = fuzz.partial_ratio(normalized_quote, normalized_source)
        if score >= config.QUOTE_FUZZY_MIN_RATIO:
            return True, "fuzzy"

    return False, "not_found"


def _is_empty_value(name: str, value) -> bool:
    if name in LIST_VALUED_FIELDS:
        return not value
    return value is None or value == ""


def verify_field(name: str, value, source_quote: str, source_text: str) -> VerifiedField:
    """필드 하나를 검증. 상태는 세 가지뿐임: not_applicable(정상적으로 빈 값) / confirmed
    (인용이 원문에 있음) / needs_review(사람이 봐야 함, reason에 이유)."""
    empty = _is_empty_value(name, value)

    if empty and not source_quote.strip():
        return VerifiedField(name=name, value=value, source_quote=source_quote, status="not_applicable")

    if empty and source_quote.strip():
        # 값은 안 채웠는데 인용만 남은 특이 케이스 — 시스템 프롬프트 위반, 사람이 봐야 함.
        return VerifiedField(
            name=name,
            value=value,
            source_quote=source_quote,
            status="needs_review",
            reason="value_missing_but_quoted",
        )

    if not source_quote.strip():
        return VerifiedField(
            name=name, value=value, source_quote=source_quote, status="needs_review", reason="no_quote"
        )

    if name in LIST_VALUED_FIELDS:
        # 여러 특수상황이면 extraction_spec.md 지침대로 " / "로 이어붙인 인용 — 조각 하나라도
        # 원문에 없으면 전체를 재검토 대상으로 보냄.
        quotes = [q.strip() for q in source_quote.split("/") if q.strip()]
        if quotes and all(quote_exists_in_source(q, source_text)[0] for q in quotes):
            return VerifiedField(name=name, value=value, source_quote=source_quote, status="confirmed")
        return VerifiedField(
            name=name, value=value, source_quote=source_quote, status="needs_review", reason="quote_not_found"
        )

    found, _match_type = quote_exists_in_source(source_quote, source_text)
    if found:
        return VerifiedField(name=name, value=value, source_quote=source_quote, status="confirmed")
    return VerifiedField(
        name=name, value=value, source_quote=source_quote, status="needs_review", reason="quote_not_found"
    )


def _values_match(a, b) -> bool:
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(float(a) - float(b)) <= config.DUAL_EXTRACT_FLOAT_TOLERANCE
    return a == b


def verify_scholarship(
    primary: ExtractedScholarship,
    source_text: str,
    listing_title: str,
    secondary: ExtractedScholarship | None,
) -> VerifiedScholarship:
    """primary가 최종적으로 산출물에 쓰이는 값. secondary는 config.DUAL_EXTRACT_FIELDS에
    해당하는 필드만 대조용으로 씀(설계안 "숫자 핵심 필드는 독립적으로 2회 추출해 서로 대조")
    — secondary 쪽 다른 필드는 버려짐, 두 결과를 필드별로 병합하지 않음(그러면 어느 쪽이
    "정답"인지 다시 판단이 필요해져서 오히려 복잡해짐)."""
    fields: dict[str, VerifiedField] = {}
    for name, extracted in primary.fields.items():
        verified = verify_field(name, extracted.value, extracted.source_quote, source_text)

        if name in config.DUAL_EXTRACT_FIELDS and secondary is not None:
            other_value = secondary.get(name).value
            if not _values_match(verified.value, other_value):
                verified = VerifiedField(
                    name=name,
                    value=verified.value,
                    source_quote=verified.source_quote,
                    status="needs_review",
                    reason=f"dual_extract_mismatch(2차 추출값={other_value!r})",
                )

        fields[name] = verified

    return VerifiedScholarship(source_url=primary.source_url, listing_title=listing_title, fields=fields)
