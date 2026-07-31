import resend

from app.core.config import settings

resend.api_key = settings.resend_api_key


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
            ),
        }
    )
