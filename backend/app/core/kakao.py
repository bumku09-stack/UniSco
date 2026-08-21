"""카카오 로그인(OAuth2 Authorization Code Flow)에 필요한 카카오 REST API 호출 2개만
감싼 얇은 모듈 — 인증 코드 → 카카오 access token 교환, 그 토큰으로 유저 정보 조회.
계정 생성/연결 같은 우리 쪽 비즈니스 로직은 여기 안 넣고 api/auth.py에 둠(이 모듈은
"카카오랑 대화하는 법"만 앎).
"""
from __future__ import annotations

from dataclasses import dataclass

import requests

from app.core.config import settings

_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"
_TIMEOUT_SECONDS = 10


class KakaoAuthError(Exception):
    """코드 교환/유저 정보 조회가 실패했을 때 — 원인 메시지를 그대로 들고 있다가
    api/auth.py에서 502로 변환."""


def _raise_with_kakao_detail(e: requests.RequestException, context: str) -> None:
    """requests.HTTPError는 res.raise_for_status()가 상태 코드만 메시지에 담고 응답 본문은
    버림 — 근데 카카오는 4xx 응답 본문에 {"error": "...", "error_description": "..."}로
    실제 원인(예: redirect_uri 불일치, invalid client secret)을 알려주므로, 그걸 안 읽으면
    "400 Client Error"까지만 보이고 왜 그런지는 매번 카카오 문서 뒤져야 함(2026-08-13,
    배포 후 첫 로그인 시도에서 원인 없는 400만 보여서 디버깅 어려웠던 것 계기로 추가)."""
    detail = str(e)
    response = getattr(e, "response", None)
    if response is not None:
        try:
            body = response.json()
            detail = body.get("error_description") or body.get("error") or response.text
        except ValueError:
            detail = response.text or detail
    raise KakaoAuthError(f"{context}: {detail}") from e


@dataclass
class KakaoUser:
    kakao_id: str
    # 카카오가 이메일을 아예 안 줬으면 None(동의항목 미허용 등). 카카오는 이메일을 줄 때만
    # is_email_verified를 같이 주는데, 우리 쪽에서 그 값을 신뢰해서 기존 계정과 자동으로
    # 연결하는 데 쓰므로(api/auth.py 참고) 검증 안 된 이메일은 email 자체를 None으로 버림 —
    # 계정 탈취 방지(검증 안 된 이메일로 남의 계정에 연결되면 안 됨).
    email: str | None


def exchange_code_for_token(code: str, redirect_uri: str) -> str:
    """인가 코드를 카카오 access token으로 교환. redirect_uri는 프론트가 인가 요청 때 실제로
    쓴 값을 그대로 받아야 함(api/models/auth.py의 KakaoLoginRequest.redirect_uri 참고) —
    배포 도메인이 여러 개라 백엔드 쪽 고정값 하나로는 못 맞출 수 있어서 고정 설정값 대신
    호출부에서 넘겨받음. client_secret은 카카오 앱에서 그 기능을 켰을 때만 필요 — 안 켰으면
    settings.kakao_client_secret이 빈 문자열이라 그 필드 자체를 요청에서 뺌(빈 문자열을
    그대로 보내면 카카오가 "Client Secret이 유효하지 않다"고 거부함)."""
    payload = {
        "grant_type": "authorization_code",
        "client_id": settings.kakao_client_id,
        "redirect_uri": redirect_uri,
        "code": code,
    }
    if settings.kakao_client_secret:
        payload["client_secret"] = settings.kakao_client_secret

    try:
        res = requests.post(_TOKEN_URL, data=payload, timeout=_TIMEOUT_SECONDS)
        res.raise_for_status()
        token_data = res.json()
    except requests.RequestException as e:
        _raise_with_kakao_detail(e, "카카오 토큰 교환 실패")
    except ValueError as e:
        # 상태코드는 2xx인데 본문이 JSON이 아닌 경우(카카오 쪽 장애/프록시 응답 등, 2026-08-15
        # 배포 전 점검에서 방어 추가) — raise_for_status()를 통과했으니 RequestException으로는
        # 안 잡힘. 흔한 케이스는 아니지만 그대로 두면 여기서 처리 안 된 예외로 502 대신
        # 500이 나감.
        raise KakaoAuthError(f"카카오 토큰 교환 실패: 응답을 JSON으로 해석할 수 없음 ({e})") from e

    access_token = token_data.get("access_token")
    if not access_token:
        raise KakaoAuthError("카카오 응답에 access_token이 없습니다.")
    return access_token


def fetch_kakao_user(kakao_access_token: str) -> KakaoUser:
    try:
        res = requests.get(
            _USER_INFO_URL,
            headers={"Authorization": f"Bearer {kakao_access_token}"},
            timeout=_TIMEOUT_SECONDS,
        )
        res.raise_for_status()
        data = res.json()
    except requests.RequestException as e:
        _raise_with_kakao_detail(e, "카카오 유저 정보 조회 실패")
    except ValueError as e:
        raise KakaoAuthError(
            f"카카오 유저 정보 조회 실패: 응답을 JSON으로 해석할 수 없음 ({e})"
        ) from e

    kakao_id = data.get("id")
    if kakao_id is None:
        raise KakaoAuthError("카카오 응답에 id가 없습니다.")

    account = data.get("kakao_account") or {}
    email = account.get("email") if account.get("is_email_verified") else None

    return KakaoUser(kakao_id=str(kakao_id), email=email)
