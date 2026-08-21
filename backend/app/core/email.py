import resend
from resend.http_client_requests import RequestsClient

from app.core.config import settings

resend.api_key = settings.resend_api_key
# 기본값(30초)이 kakao.py의 카카오 API 호출(_TIMEOUT_SECONDS=10)보다 훨씬 길어서 20초로
# 줄임(2026-08-21) — Resend가 응답 없을 때 사용자가 에러를 보기까지 기다리는 최대 시간.
resend.default_http_client = RequestsClient(timeout=20)


# 2026-08-15 — SPF/DKIM/DMARC 다 정상인데도 스팸함으로 가는 문제 점검 중 추가. HTML만 있고
# text/plain 파트가 아예 없는 메일은 스팸 필터가 흔히 의심 신호로 봄(진짜 서비스 발신
# 메일은 거의 항상 멀티파트) — Resend가 "text" 키를 같이 주면 알아서 멀티파트로 보내줌.
_FOOTER_TEXT = "\n\n이 메일은 unisco.co.kr 계정 인증을 위해 발송되었습니다."
_FOOTER_HTML = (
    "<p style='color:#888;font-size:12px'>"
    "이 메일은 unisco.co.kr 계정 인증을 위해 발송되었습니다.</p>"
)


def send_verification_code(to_email: str, code: str) -> None:
    """Raises on failure — callers should let this bubble up as a 500 rather
    than silently telling the user a code was sent when it wasn't."""
    resend.Emails.send(
        {
            "from": settings.email_from,
            "to": to_email,
            "subject": "UniSco 이메일 인증 코드",
            "html": (
                f"<p>인증 코드: <strong style='font-size:20px'>{code}</strong></p>"
                "<p>5분 안에 입력해주세요. 요청하지 않으셨다면 이 메일을 무시하셔도 됩니다.</p>"
                f"{_FOOTER_HTML}"
            ),
            "text": (
                f"인증 코드: {code}\n\n"
                "5분 안에 입력해주세요. 요청하지 않으셨다면 이 메일을 무시하셔도 됩니다."
                f"{_FOOTER_TEXT}"
            ),
        }
    )


def send_password_reset_code(to_email: str, code: str) -> None:
    resend.Emails.send(
        {
            "from": settings.email_from,
            "to": to_email,
            "subject": "UniSco 비밀번호 재설정 코드",
            "html": (
                f"<p>비밀번호 재설정 코드: <strong style='font-size:20px'>{code}</strong></p>"
                "<p>5분 안에 입력해주세요. 요청하지 않으셨다면 이 메일을 무시하셔도 됩니다 — "
                "비밀번호는 바뀌지 않습니다.</p>"
                f"{_FOOTER_HTML}"
            ),
            "text": (
                f"비밀번호 재설정 코드: {code}\n\n"
                "5분 안에 입력해주세요. 요청하지 않으셨다면 이 메일을 무시하셔도 됩니다 — "
                "비밀번호는 바뀌지 않습니다."
                f"{_FOOTER_TEXT}"
            ),
        }
    )
