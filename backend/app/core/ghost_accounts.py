import asyncio
from datetime import UTC, datetime, timedelta

from sqlmodel import Session, select

from app.db.session import engine
from app.models import EmailVerification, PendingSignup, User

# 원래는 오타/존재하지 않는 이메일로 가입 시도한 계정이 is_verified=False 상태로 아이디/
# 이메일을 영구히 점유하는 문제를 완화하려고 만든 시간 기반 청소부였음. 근데 같은 날
# PendingSignup 도입(migration_2026-08-21d) — 인증 코드 확인 전엔 User를 아예 안 만드는
# 방식 — 으로 문제를 애초에 발생 안 하게 만들어서, 이제 이 청소부가 지울 대상(is_verified=
# False인 User)이 정상 흐름에서는 거의 안 생김. 그래도 지우지 않고 안전망으로 남겨둠 — 혹시
# 나중에 다른 소셜 로그인을 비동기 인증 방식으로 추가하거나, 코드에 버그가 생겨 미인증 User가
# 만들어지는 경우를 대비함(있으면 청소, 없으면 그냥 빈 손으로 끝남 — 해는 없음).
#
# 인증 코드 자체의 유효시간(CODE_TTL, api/auth.py)은 5분 — 이 값(GHOST_ACCOUNT_TTL)은 반드시
# CODE_TTL보다 길게 잡을 것. 짧게 잡으면 코드는 아직 유효한데 계정이 먼저 삭제되는 모순이
# 생김(정상 사용자가 메일 늦게 확인했을 뿐인데 "계정을 찾을 수 없습니다"를 보게 됨).
#
# 3분 → 30분을 거쳐 최종 1일로 결정(2026-08-21) — GitLab이 이 값을 7일로 널널하게 잡은 것과
# 같은 이유: "오타 메일이라 영원히 안 오는 것"과 "정상 메일인데 사람이 하루 딴짓하다 늦게
# 확인하는 것"을 구분할 방법이 시스템 입장에선 없어서, 진짜 정상 사용자가 실수로 계정을
# 잃지 않도록 충분히 여유를 둠. 이 값을 늘렸으니 확인 주기(_CHECK_INTERVAL_SECONDS)도 1분처럼
# 촘촘할 필요가 없어짐 — 1일짜리 기준에 몇 분 오차는 무의미해서 DB 부담을 줄이는 쪽으로 늘림.
GHOST_ACCOUNT_TTL = timedelta(days=1)
_CHECK_INTERVAL_SECONDS = 30 * 60  # 30분마다 확인

# PendingSignup(2026-08-21 도입) — 인증 코드 확인 전까지 임시로 보관하는 테이블이라 다른 사람을
# 막지는 않지만, 오타/방치된 시도가 계속 쌓이기만 하고 아무도 안 지우면 DB에 쓰레기가 무한정
# 늘어남. code의 expires_at(재발송하면 갱신됨, api/auth.py의 resend_code 참고)을 기준으로,
# 만료되고도 한참(1시간) 지나면 완전히 방치된 걸로 보고 지움 — 1시간이라는 여유는 "누가 지금
# 이 코드로 막 인증 시도하는 중일 수도 있으니 만료 직후 바로는 건들지 말자"는 안전 버퍼일 뿐,
# 실제 유효시간(5분)에 비하면 넉넉함.
PENDING_SIGNUP_TTL_BUFFER = timedelta(hours=1)


def delete_expired_pending_signups() -> int:
    """만료되고도 PENDING_SIGNUP_TTL_BUFFER만큼 더 지나도록 방치된 가입 시도를 지움."""
    cutoff = datetime.now(UTC).replace(tzinfo=None) - PENDING_SIGNUP_TTL_BUFFER
    with Session(engine) as session:
        stale = session.exec(select(PendingSignup).where(PendingSignup.expires_at < cutoff)).all()
        for row in stale:
            session.delete(row)
        session.commit()
        return len(stale)


def delete_expired_ghost_accounts() -> int:
    """GHOST_ACCOUNT_TTL이 지나도 인증 안 된 계정을 전부 지움. EmailVerification이 User를
    참조하는 외래키에 CASCADE가 없어서(supabase/schema.sql 참고) User를 지우기 전에 관련
    EmailVerification 행부터 먼저 지워야 함 — 순서를 반대로 하면 FK 제약 위반으로 실패함."""
    cutoff = datetime.now(UTC).replace(tzinfo=None) - GHOST_ACCOUNT_TTL
    with Session(engine) as session:
        ghosts = session.exec(
            select(User).where(User.is_verified == False, User.created_at < cutoff)  # noqa: E712
        ).all()
        for user in ghosts:
            for code in session.exec(
                select(EmailVerification).where(EmailVerification.user_id == user.id)
            ).all():
                session.delete(code)
            session.delete(user)
        session.commit()
        return len(ghosts)


async def run_ghost_account_cleanup_loop() -> None:
    """앱이 켜져 있는 동안 매 _CHECK_INTERVAL_SECONDS마다 반복 실행(app/main.py의 lifespan에서
    시작함). DB 작업은 동기 함수라 asyncio.to_thread로 돌려서 이벤트 루프를 안 막음."""
    while True:
        try:
            deleted_users = await asyncio.to_thread(delete_expired_ghost_accounts)
            if deleted_users:
                print(f"[ghost_accounts] 방치된 미인증 계정 {deleted_users}건 삭제", flush=True)
            deleted_pending = await asyncio.to_thread(delete_expired_pending_signups)
            if deleted_pending:
                print(f"[ghost_accounts] 방치된 가입 시도 {deleted_pending}건 삭제", flush=True)
        except Exception as e:  # noqa: BLE001 — 백그라운드 루프가 죽으면 안 되므로 계속 진행
            print(f"[ghost_accounts] cleanup failed: {e!r}", flush=True)
        await asyncio.sleep(_CHECK_INTERVAL_SECONDS)
