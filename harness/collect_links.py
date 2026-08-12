"""Layer 1 — 목록 수집. **LLM이 전혀 관여하지 않음.**

설계안 3.1절 원칙 그대로: 총 게시물 수/총 페이지 수를 먼저 정규식으로 파싱하고, 1페이지부터
마지막 페이지까지 코드로 반복 순회하며 링크만 모은 다음, 수집된 링크 수를 파싱된 총 개수와
기계적으로 대조한다. "이 정도면 다 본 것 같다"는 판단을 내리는 주체가 없음 — 숫자가 안 맞으면
그냥 안 맞는 것이고, 재시도하거나 CollectionResult.ok=False로 명시적으로 실패를 드러낸다.
"""
from __future__ import annotations

import re
import time
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from harness import config, http
from harness.models import CollectionResult, Listing
from harness.sites import BoardConfig


_JS_FETCH_MAX_RETRIES = 2


def _fetch_js(url: str) -> str:
    # 설계안 3.1절 5번 — JS 렌더링에 의존하는 게시판은 Playwright로 렌더링 완료 후 HTML을 가져옴.
    from playwright.sync_api import Error as PlaywrightError
    from playwright.sync_api import sync_playwright

    # http.get()과 같은 이유로 재시도함(일시적 네트워크 블립, 2026-08-10) — 이 경로는
    # requests가 아니라 Playwright라 http.py의 재시도 로직을 못 씀, 여기 따로 둠.
    for attempt in range(_JS_FETCH_MAX_RETRIES + 1):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                try:
                    page = browser.new_page(user_agent=config.REQUEST_USER_AGENT)
                    page.goto(url, timeout=config.REQUEST_TIMEOUT_SECONDS * 1000)
                    page.wait_for_load_state("networkidle")
                    return page.content()
                finally:
                    browser.close()
        except PlaywrightError:
            if attempt == _JS_FETCH_MAX_RETRIES:
                raise
            time.sleep(3 * (attempt + 1))
    raise AssertionError("unreachable")


def fetch_page(url: str, board: BoardConfig) -> str:
    return _fetch_js(url) if board.requires_js else http.get_text(url)


def _parse_expected_count(html: str, board: BoardConfig) -> tuple[int | None, int | None]:
    """(총 게시물 수 또는 None, 총 페이지 수 또는 None). 총 페이지 수가 None이면 파싱 실패로 취급."""
    if board.total_pages_pattern:
        m = re.search(board.total_pages_pattern, html)
        if m:
            return None, int(m.group(m.lastindex))
    if board.total_count_pattern:
        m = re.search(board.total_count_pattern, html)
        if m:
            count = int(m.group(1))
            pages = max(1, -(-count // board.items_per_page))  # ceil division
            return count, pages
    return None, None


_JS_HREF_PLACEHOLDERS = {"#", "#view", "javascript:void(0)", "javascript:void(0);", ""}


def _extract_links(html: str, board: BoardConfig) -> list[tuple[str, str]]:
    """[(절대 URL, 게시글 제목)] — 제목은 dedup.py가 이름 대용으로 씀(harness/dedup.py 참고).

    일부 대학 게시판(전자정부프레임워크 스킨 등)은 제목 링크의 href가 "#"/"javascript:" 같은
    자리표시자고, 실제 게시글 ID는 다른 속성에만 있어서(예: onclick="fn_search_detail('B0001')",
    또는 data-id="553608") href만 봐서는 모든 행이 같은 URL로 뭉개짐(2026-08-11, 한밭대·배재대·
    대전대에서 실제로 확인 — 각기 다른 속성을 쓰지만 같은 부류 문제). href가 못 쓸 값이고
    board.id_source_attr/view_url_template가 설정돼 있으면 그 속성값(필요하면 id_pattern으로
    정규식 추출)으로 URL을 직접 조립하는 걸로 대체함 — 기존 대학(href가 정상인 경우)은 이
    분기를 안 타므로 동작이 그대로임."""
    soup = BeautifulSoup(html, "lxml")
    results: list[tuple[str, str]] = []
    for a in soup.select(board.link_selector):
        title = a.get_text(strip=True)
        href = a.get("href")
        if href and href.strip() not in _JS_HREF_PLACEHOLDERS and not href.lower().startswith("javascript:"):
            url = urljoin(board.link_base_url, href) if board.link_base_url else href
        elif board.id_source_attr and board.view_url_template:
            raw = (a.get(board.id_source_attr) or "").strip()
            if board.id_pattern:
                m = re.search(board.id_pattern, raw)
                if not m:
                    continue
                item_id = m.group(1)
            elif raw:
                item_id = raw
            else:
                continue
            url = board.view_url_template.format(id=item_id)
        else:
            continue
        results.append((url, title))
    return results


def collect_board_links(board: BoardConfig) -> CollectionResult:
    """게시판 하나를 끝까지 순회. 원칙 1의 핵심 구현부."""
    last_listings: list[Listing] = []
    last_expected: int | None = None
    last_actual = 0

    max_attempts = config.LINK_COLLECTION_MAX_RETRIES + 1
    for attempt in range(1, max_attempts + 1):
        first_url = board.list_url_template.format(page=board.first_page_index)
        first_html = fetch_page(first_url, board)
        expected_count, total_pages = _parse_expected_count(first_html, board)

        if total_pages is None:
            # 재시도해도 안 바뀔 문제(정규식이 그 사이트 문구와 안 맞음) — 바로 실패 처리.
            return CollectionResult(
                university=board.university,
                board_name=board.board_name,
                listings=[],
                expected_count=None,
                actual_count=0,
                ok=False,
                note=(
                    "총 게시물 수/총 페이지 수 파싱 실패 — sites.py의 total_count_pattern/"
                    "total_pages_pattern이 실제 페이지 문구와 맞는지 확인할 것."
                ),
            )

        seen: set[str] = set()
        listings: list[Listing] = []
        for page_num in range(board.first_page_index, board.first_page_index + total_pages):
            if page_num != board.first_page_index:
                time.sleep(config.REQUEST_DELAY_SECONDS)  # 같은 호스트로 몰아치지 않게(config.py 참고)
            html = (
                first_html
                if page_num == board.first_page_index
                else fetch_page(board.list_url_template.format(page=page_num), board)
            )
            for url, title in _extract_links(html, board):
                if url in seen:
                    continue
                seen.add(url)
                listings.append(
                    Listing(
                        url=url,
                        title=title,
                        university=board.university,
                        department=board.department,
                        board_name=board.board_name,
                    )
                )

        last_listings, last_expected, last_actual = listings, expected_count, len(listings)

        # 원칙 1: "다 봤는지" 판단은 이 등호 비교가 전부임 — LLM에게 물어보지 않음.
        if expected_count is None or last_actual == expected_count:
            return CollectionResult(
                university=board.university,
                board_name=board.board_name,
                listings=listings,
                expected_count=expected_count,
                actual_count=last_actual,
                ok=True,
            )

        if attempt < max_attempts:
            time.sleep(2)
            continue

    return CollectionResult(
        university=board.university,
        board_name=board.board_name,
        listings=last_listings,
        expected_count=last_expected,
        actual_count=last_actual,
        ok=False,
        note=(
            f"{config.LINK_COLLECTION_MAX_RETRIES}회 재시도해도 수집된 링크 수({last_actual})가 "
            f"게시판 표시 총 개수({last_expected})와 안 맞음 — 사람이 확인 필요."
        ),
    )


def collect_all(boards: list[BoardConfig]) -> list[CollectionResult]:
    return [collect_board_links(b) for b in boards]
