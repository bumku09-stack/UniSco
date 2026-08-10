"""Layer 1 — 중복 스킵. **LLM이 관여하지 않음**(설계안 6장 "LLM으로 중복 판정" 채택 안 함).

이름+기관 문자열 유사도만으로 판단함. 파이프라인상 이 단계는 LLM 추출(4단계) *이전*이라
아직 "이름+기관"이 구조화되기 전임 — 그래서 게시글 제목(Listing.title)을 이름의, 소속 대학명을
기관의 대용으로 써서 기존 DB의 (name, provider)와 대조함. 게시글 제목이 장학금 정식 명칭과
정확히 같지 않을 수 있어 완벽하진 않지만, 비싼 LLM 호출 전에 명백한 재중복(예: 작년에 이미
입력해둔 "2026학년도 1학기 성적우수장학금" 공고가 올해도 그대로 다시 올라온 경우)만 걸러내는
용도로는 충분함 — 애매한 경우는 그냥 통과시켜서 LLM 추출까지 가게 두고, 사람이 리뷰 단계에서
데이터 자체를 보고 판단하면 됨(과다매칭이 과소매칭보다 낫다는 UniSco의 기존 원칙과 같은 방향).
"""
from __future__ import annotations

from rapidfuzz import fuzz

from harness import config
from harness.models import Listing


def _key(name: str, provider: str) -> str:
    return f"{name.strip()} {provider.strip()}".strip()


def is_duplicate(
    candidate_title: str, candidate_university: str, existing: list[tuple[str, str]]
) -> tuple[bool, str | None, float]:
    """(중복 여부, 가장 비슷했던 기존 항목의 name, 유사도 점수 0~100)."""
    candidate_key = _key(candidate_title, candidate_university)
    best_match: str | None = None
    best_score = 0.0
    for name, provider in existing:
        score = fuzz.token_sort_ratio(candidate_key, _key(name, provider))
        if score > best_score:
            best_score = score
            best_match = name
    return best_score >= config.DEDUP_SIMILARITY_THRESHOLD, best_match, best_score


def filter_new(
    listings: list[Listing], existing: list[tuple[str, str]]
) -> tuple[list[Listing], list[Listing]]:
    """(신규만, 스킵된 것들). 신규만 다음 단계(extract.py)로 넘어감."""
    new_listings: list[Listing] = []
    skipped: list[Listing] = []
    for listing in listings:
        dup, _match, _score = is_duplicate(listing.title, listing.university, existing)
        (skipped if dup else new_listings).append(listing)
    return new_listings, skipped
