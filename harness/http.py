"""공용 HTTP GET — collect_links.py와 run.py가 각자 따로 갖고 있던 요청 보일러플레이트를
한 곳으로 모음. 하네스는 requests만 쓰고(Playwright는 collect_links.py의 JS 렌더링
전용 경로에서만), 매 호출마다 같은 timeout/User-Agent를 반복하지 않게 함.
"""
from __future__ import annotations

import time

import requests

from harness import config

# 연결 타임아웃/일시적 연결 끊김은 재시도하면 성공하는 경우가 많음(2026-08-10, GitHub Actions
# 러너에서 plus.cnu.ac.kr 접속이 순간적으로 timeout=20으로 실패했지만 같은 URL을 그 직후
# 로컬에서 호출하면 1초 만에 정상 응답 — 사이트 문제가 아니라 일시적 네트워크 블립이었음).
# 이 함수가 목록 수집(collect_links.py)과 원문 확보(run.py) 양쪽의 공통 진입점이라 여기
# 한 곳만 고치면 됨. HTTP 에러 상태코드(404/500 등, raise_for_status가 던지는 것)는 재시도
# 대상이 아님 — 같은 URL을 다시 불러도 똑같이 실패할 뿐이므로 여기서 바로 전파함.
_MAX_RETRIES = 2


def get(url: str) -> requests.Response:
    for attempt in range(_MAX_RETRIES + 1):
        try:
            resp = requests.get(
                url,
                timeout=config.REQUEST_TIMEOUT_SECONDS,
                headers={"User-Agent": config.REQUEST_USER_AGENT},
            )
            resp.raise_for_status()
            return resp
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            if attempt == _MAX_RETRIES:
                raise
            time.sleep(3 * (attempt + 1))  # 3s, 6s
    raise AssertionError("unreachable")  # for 문이 항상 return/raise로 끝나 mypy 안심용


def get_text(url: str) -> str:
    """HTML/텍스트 응답. 여러 대학 게시판이 Content-Type 헤더에 charset을 안 넣어서(실제로
    UTF-8인데도) requests가 기본값인 ISO-8859-1로 잘못 디코딩하는 경우가 실제로 있어서
    (예: 충남대 plus.cnu.ac.kr, 2026-08-05 실측), resp.text 대신 apparent_encoding(바이트
    내용 자체를 sniffing)으로 강제해서 한글이 깨지지 않게 함 — 헤더가 맞는 사이트는
    apparent_encoding도 보통 같은 결과를 내서 무해함."""
    resp = get(url)
    resp.encoding = resp.apparent_encoding
    return resp.text
