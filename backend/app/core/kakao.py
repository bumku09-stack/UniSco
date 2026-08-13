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


@dataclass
class KakaoUser:
    kakao_id: str
    nickname: str | None
    # 카카오가 이메일을 아예 안 줬으면 None(동의항목 미허용 등). 카카오는 이메일을 줄 때만
    # is_email_verified를 같이 주는데, 우리 쪽에서 그 값을 신뢰해서 기존 계정과 자동으로
    # 연결하는 데 쓰므로(api/auth.py 참고) 검증 안 된 이메일은 email 자체를 None으로 버림 —
    # 계정 탈취 방지(검증 안 된 이메일로 남의 계정에 연결되면 안 됨).
    email: str | None


def exchange_code_for_token(code: str) -> str:
    """인가 코드를 카카오 access token으로 교환. client_secret은 카카오 앱에서 그 기능을
    켰을 때만 필요 — 안 켰으면 settings.kakao_client_secret이 빈 문자열이라 그 필드 자체를
    요청에서 뺌(빈 문자열을 그대로 보내면 카카오가 "Client Secret이 유효하지 않다"고
    거부함)."""
    payload = {
        "grant_type": "authorization_code",
        "client_id": settings.kakao_client_id,
        "redirect_uri": settings.kakao_redirect_uri,
        "code": code,
    }
    if settings.kakao_client_secret:
        payload["client_secret"] = settings.kakao_client_secret

    try:
        res = requests.post(_TOKEN_URL, data=payload, timeout=_TIMEOUT_SECONDS)
        res.raise_for_status()
    except requests.RequestException as e:
        raise KakaoAuthError(f"카카오 토큰 교환 실패: {e}") from e

    access_token = res.json().get("access_token")
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
    except requests.RequestException as e:
        raise KakaoAuthError(f"카카오 유저 정보 조회 실패: {e}") from e

    data = res.json()
    kakao_id = data.get("id")
    if kakao_id is None:
        raise KakaoAuthError("카카오 응답에 id가 없습니다.")

    account = data.get("kakao_account") or {}
    profile = account.get("profile") or {}
    email = account.get("email") if account.get("is_email_verified") else None

    return KakaoUser(kakao_id=str(kakao_id), nickname=profile.get("nickname"), email=email)
