"""공용 HTTP GET — collect_links.py와 run.py가 각자 따로 갖고 있던 요청 보일러플레이트를
한 곳으로 모음. 하네스는 requests만 쓰고(Playwright는 collect_links.py의 JS 렌더링
전용 경로에서만), 매 호출마다 같은 timeout/User-Agent를 반복하지 않게 함.
"""
from __future__ import annotations

import requests

from harness import config


def get(url: str) -> requests.Response:
    resp = requests.get(
        url,
        timeout=config.REQUEST_TIMEOUT_SECONDS,
        headers={"User-Agent": config.REQUEST_USER_AGENT},
    )
    resp.raise_for_status()
    return resp


def get_text(url: str) -> str:
    """HTML/텍스트 응답. 여러 대학 게시판이 Content-Type 헤더에 charset을 안 넣어서(실제로
    UTF-8인데도) requests가 기본값인 ISO-8859-1로 잘못 디코딩하는 경우가 실제로 있어서
    (예: 충남대 plus.cnu.ac.kr, 2026-08-05 실측), resp.text 대신 apparent_encoding(바이트
    내용 자체를 sniffing)으로 강제해서 한글이 깨지지 않게 함 — 헤더가 맞는 사이트는
    apparent_encoding도 보통 같은 결과를 내서 무해함."""
    resp = get(url)
    resp.encoding = resp.apparent_encoding
    return resp.text
