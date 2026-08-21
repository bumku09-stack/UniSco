import dns.exception
import dns.resolver
import resend
from resend.http_client_requests import RequestsClient

from app.core.config import settings

resend.api_key = settings.resend_api_key
# 기본값(30초)이 kakao.py의 카카오 API 호출(_TIMEOUT_SECONDS=10)보다 훨씬 길어서 20초로
# 줄임(2026-08-21) — Resend가 응답 없을 때 사용자가 에러를 보기까지 기다리는 최대 시간.
resend.default_http_client = RequestsClient(timeout=20)

# 도메인 오타 체크(2026-08-21 추가) — "메일함이 실제로 있는지"는 받는 메일서버만 알 수 있어서
# (반송은 비동기라 API 응답 시점엔 알 방법이 없음) 실시간으로 확인 불가능하지만, "도메인 자체가
# 아예 존재하는지"(예: gmial.com 같은 오타)는 DNS로 즉시 확인 가능함 — 흔한 오타를 가입 순간에
# 잡아줌. 짧은 타임아웃(3초)을 둬서 DNS가 느려도 회원가입 전체가 오래 걸리지 않게 함.
_DNS_TIMEOUT = 3.0


def email_domain_has_mail_server(email: str) -> bool:
    """이메일 도메인에 MX 레코드가 있는지(=메일을 받을 의도로 설정된 도메인인지) 확인함. DNS
    조회 자체가 실패/타임아웃하면(일시적 네트워크 문제 등) 판단 불가로 보고 True를 돌려줌 —
    확실히 메일 못 받는다고 확인된 경우(NXDOMAIN, MX 레코드 없음)에만 False.

    처음엔 "MX가 없으면 A 레코드라도 있는지"까지 확인하는 fallback을 뒀었는데(RFC 5321이
    허용하는 방식이라), 실제로 "gmial.com" 같은 흔한 오타 도메인이 메일은 절대 못 받으면서도
    웹 페이지용 A 레코드는 갖고 있어서(주차된 도메인 등) 오히려 오타를 못 잡는 결과가 나옴 —
    이 기능의 목적(오타 잡기)엔 A 레코드 fallback이 도움이 안 되고 방해만 돼서 뺐음."""
    domain = email.rsplit("@", 1)[-1]
    resolver = dns.resolver.Resolver()
    resolver.timeout = _DNS_TIMEOUT
    resolver.lifetime = _DNS_TIMEOUT
    try:
        resolver.resolve(domain, "MX")
        return True
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        return False
    except dns.exception.DNSException:
        return True


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
