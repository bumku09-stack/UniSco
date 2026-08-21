import secrets
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.core.email import (
    email_domain_has_mail_server,
    send_password_reset_code,
    send_verification_code,
)
from app.core.kakao import KakaoAuthError, exchange_code_for_token, fetch_kakao_user
from app.core.security import (
    InvalidTokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.session import get_session
from app.models import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    KakaoLoginRequest,
    LoginRequest,
    PasswordReset,
    PendingSignup,
    RefreshRequest,
    ResendCodeRequest,
    ResetPasswordRequest,
    SavedSpec,
    SignupRequest,
    SignupResponse,
    TokenResponse,
    User,
    UsernameAvailabilityResponse,
    VerifyCodeRequest,
)

router = APIRouter(prefix="/auth")

CODE_TTL = timedelta(minutes=5)
MAX_ATTEMPTS = 5


def _generate_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def _find_user_by_identifier(session: Session, identifier: str) -> User | None:
    return session.exec(
        select(User).where((User.username == identifier) | (User.email == identifier))
    ).first()


def _send_code_or_502(email: str, code: str, context: str, send_fn=send_verification_code) -> None:
    """인증 코드 발송, 실패하면 502로 변환. signup/resend-code/forgot-password가 이 로직을
    공유함 — context는 로그에 남는 호출 위치 구분용, send_fn은 실제 발송 함수(용도별로
    이메일 문구가 달라서 core/email.py의 함수를 다르게 넘김)."""
    try:
        send_fn(email, code)
    except Exception as e:
        print(f"[auth/{context}] {send_fn.__name__} failed for {email}: {e!r}", flush=True)
        raise HTTPException(
            status_code=502, detail="인증 메일 발송에 실패했습니다. 잠시 후 다시 시도해주세요."
        ) from e


# 원래 EmailVerification/PasswordReset 둘 다 이 타입 별칭을 공유했는데(2026-08-11 리팩터링),
# 2026-08-21에 회원가입 인증 흐름을 PendingSignup 기반으로 바꾸면서 EmailVerification은 더
# 이상 안 씀(아래 signup/verify_code/resend_code 참고) — PasswordReset(비밀번호 재설정,
# forgot-password/reset-password)만 남음. 지금은 PasswordReset 하나뿐이라 Union일 필요는
# 없지만, 나중에 비슷한 OTP 테이블이 또 생기면 다시 Union으로 늘리면 됨.
_OtpModel = PasswordReset

# resend-code/forgot-password는 로그인 없이(아이디만 알면) 누구나 호출 가능해서, 막아두지
# 않으면 특정 계정 메일함으로 재발송/재설정 메일을 무한정 스팸으로 보낼 수 있음(2026-08-11,
# 배포 전 점검 중 발견 — rate limit이 아예 없었음). 이 계정한테 가장 최근 코드를 보낸 지
# COOLDOWN 안이면 새로 안 보내고 429로 막음 — signup은 대상에서 뺌(이메일이 이미
# User.email unique 제약으로 막혀있어서, 같은 주소로 다시 가입 시도해봤자 409로 막히고
# 메일 자체가 안 나감 — signup 자체는 한 주소당 최초 1통 이상 나갈 방법이 없어서 이 문제에
# 해당 안 함).
CODE_REQUEST_COOLDOWN = timedelta(seconds=60)


def _check_not_rate_limited(session: Session, model: type[_OtpModel], user_id: int) -> None:
    latest = session.exec(
        select(model).where(model.user_id == user_id).order_by(model.id.desc())
    ).first()
    if latest is None:
        return
    created_at = latest.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=UTC)
    elapsed = datetime.now(UTC) - created_at
    if elapsed < CODE_REQUEST_COOLDOWN:
        wait = int((CODE_REQUEST_COOLDOWN - elapsed).total_seconds())
        raise HTTPException(
            status_code=429, detail=f"너무 자주 요청했습니다. {wait}초 후 다시 시도해주세요."
        )


def _issue_code(session: Session, model: type[_OtpModel], user_id: int, code: str) -> None:
    """기존에 안 쓴 코드가 있으면 무효화하고 새 코드를 저장함 — 반드시 이메일 발송이
    이미 성공한 뒤에만 호출할 것(발송 실패 시 아무 행도 안 생기게 하려고 순서를 각
    라우트에서 관리함, signup의 "메일 먼저" 원칙과 동일)."""
    old_codes = session.exec(
        select(model).where(model.user_id == user_id, model.is_used == False)  # noqa: E712
    ).all()
    for old in old_codes:
        old.is_used = True
        session.add(old)
    session.add(model(user_id=user_id, code=code, expires_at=datetime.now(UTC) + CODE_TTL))
    session.commit()


def _consume_code(
    session: Session, model: type[_OtpModel], user_id: int, code: str, label: str
) -> _OtpModel:
    """OTP 코드 하나를 검증하고 소비(is_used=True) 처리함 — 통과하면 그 행을 반환하니
    호출부가 이어서 실제 효과(계정 인증/비밀번호 변경)를 적용하고 커밋할 것(여기서는 커밋
    안 함, 검증 실패 케이스만 여기서 바로 커밋 후 예외를 던짐). label은 에러 메시지에 쓰이는
    명사("인증 코드"/"재설정 코드")."""
    row = session.exec(
        select(model)
        .where(model.user_id == user_id, model.is_used == False)  # noqa: E712
        .order_by(model.id.desc())
    ).first()
    if row is None:
        raise HTTPException(status_code=400, detail=f"{label}가 없습니다. 재발송해주세요.")

    now = datetime.now(UTC)
    expires_at = row.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if now > expires_at:
        row.is_used = True
        session.add(row)
        session.commit()
        raise HTTPException(status_code=400, detail=f"{label}가 만료되었습니다. 재발송해주세요.")

    if row.attempts >= MAX_ATTEMPTS:
        row.is_used = True
        session.add(row)
        session.commit()
        raise HTTPException(status_code=429, detail="시도 횟수를 초과했습니다. 재발송해주세요.")

    if row.code != code:
        row.attempts += 1
        session.add(row)
        session.commit()
        raise HTTPException(status_code=400, detail=f"{label}가 일치하지 않습니다.")

    row.is_used = True
    return row


@router.get("/check-username", response_model=UsernameAvailabilityResponse)
def check_username(
    username: str = Query(min_length=5, max_length=32), session: Session = Depends(get_session)
):
    """회원가입 폼에서 아이디 입력 즉시 중복 여부만 확인하는 용도 — 별도 인증/rate limit
    없음(이메일을 새로 발송하는 resend-code/forgot-password와 달리 스팸 비용이 없고, 어차피
    signup 자체가 409로 같은 정보를 이미 노출함)."""
    exists = session.exec(select(User).where(User.username == username)).first() is not None
    return UsernameAvailabilityResponse(available=not exists)


def _find_pending_signup_by_identifier(session: Session, identifier: str) -> PendingSignup | None:
    """PendingSignup은 User와 달리 username/email에 유니크 제약이 없어서(아직 확정된 계정이
    아니므로 여러 개 겹쳐도 무해함, models/user.py 참고) 같은 아이디/이메일로 여러 번 시도한
    기록이 남아있을 수 있음 — 그중 제일 최근 시도(=지금 완료하려는 그 시도)를 돌려줌."""
    return session.exec(
        select(PendingSignup)
        .where((PendingSignup.username == identifier) | (PendingSignup.email == identifier))
        .order_by(PendingSignup.id.desc())
    ).first()


@router.post("/signup", response_model=SignupResponse)
def signup(body: SignupRequest, session: Session = Depends(get_session)):
    # 인증 코드를 확인하기 전까지는 User를 아예 안 만듦(2026-08-21 변경) — 예전엔 여기서 바로
    # User를 만들어서, 오타/존재하지 않는 이메일로 시도한 계정이 인증 안 된 채로 아이디/이메일을
    # 영구히 점유해버리는 문제가 있었음. 이제는 PendingSignup에 임시로만 보관하고, 실제로
    # 코드를 맞게 입력한 순간(verify_code)에만 User가 생김 — 그러니 여기서 하는 중복 체크는
    # "이미 인증 완료된 진짜 계정"하고만 비교하면 됨(다른 사람의 PendingSignup은 신경 안 씀 —
    # 그 사람이 나중에 코드를 맞게 넣으면 verify_code에서 다시 한번 확인함, 아래 참고).
    if session.exec(select(User).where(User.username == body.username)).first():
        raise HTTPException(status_code=409, detail="이미 사용 중인 아이디입니다.")
    if session.exec(select(User).where(User.email == body.email)).first():
        raise HTTPException(status_code=409, detail="이미 사용 중인 이메일입니다.")
    if not email_domain_has_mail_server(body.email):
        raise HTTPException(
            status_code=422, detail="존재하지 않는 이메일 도메인이에요. 이메일 주소를 다시 확인해주세요."
        )

    code = _generate_code()
    _send_code_or_502(body.email, code, "signup")

    session.add(
        PendingSignup(
            username=body.username,
            email=body.email,
            hashed_password=hash_password(body.password),
            code=code,
            expires_at=datetime.now(UTC) + CODE_TTL,
        )
    )
    session.commit()

    return SignupResponse()


@router.post("/verify-code", response_model=SignupResponse)
def verify_code(body: VerifyCodeRequest, session: Session = Depends(get_session)):
    pending = _find_pending_signup_by_identifier(session, body.identifier)
    if pending is None:
        raise HTTPException(status_code=404, detail="가입 시도를 찾을 수 없습니다. 다시 가입해주세요.")

    now = datetime.now(UTC)
    expires_at = pending.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if now > expires_at:
        session.delete(pending)
        session.commit()
        raise HTTPException(status_code=400, detail="인증 코드가 만료되었습니다. 재발송해주세요.")

    if pending.attempts >= MAX_ATTEMPTS:
        session.delete(pending)
        session.commit()
        raise HTTPException(status_code=429, detail="시도 횟수를 초과했습니다. 재발송해주세요.")

    if pending.code != body.code:
        pending.attempts += 1
        session.add(pending)
        session.commit()
        raise HTTPException(status_code=400, detail="인증 코드가 일치하지 않습니다.")

    # 코드가 맞아서 이제 진짜 계정을 만듦 — 근데 이 PendingSignup을 만든 시점 이후로 같은
    # 아이디/이메일이 이미 다른 경로로(예: 동시에 시도한 다른 사람이 먼저 인증 완료) 정식
    # 계정이 됐을 수 있음(극히 드문 경우). 마지막으로 한 번 더 확인해서 이 레이스 컨디션을
    # 막음 — User.username/email의 DB 유니크 제약이 최종 방어선이라 여기서 안 걸러져도 바로
    # 아래 session.add(user)에서 에러가 나긴 하지만, 그러면 500으로 보이니 미리 깔끔하게 409로.
    if session.exec(select(User).where(User.username == pending.username)).first():
        session.delete(pending)
        session.commit()
        raise HTTPException(
            status_code=409, detail="이미 사용 중인 아이디입니다. 다시 가입해주세요."
        )
    if session.exec(select(User).where(User.email == pending.email)).first():
        session.delete(pending)
        session.commit()
        raise HTTPException(
            status_code=409, detail="이미 사용 중인 이메일입니다. 다시 가입해주세요."
        )

    user = User(
        username=pending.username,
        email=pending.email,
        hashed_password=pending.hashed_password,
        is_verified=True,
    )
    session.add(user)
    session.delete(pending)
    session.commit()
    return SignupResponse(message="이메일 인증이 완료되었습니다.")


@router.post("/resend-code", response_model=SignupResponse)
def resend_code(body: ResendCodeRequest, session: Session = Depends(get_session)):
    pending = _find_pending_signup_by_identifier(session, body.identifier)
    if pending is None:
        raise HTTPException(status_code=404, detail="가입 시도를 찾을 수 없습니다. 다시 가입해주세요.")

    created_at = pending.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=UTC)
    elapsed = datetime.now(UTC) - created_at
    if elapsed < CODE_REQUEST_COOLDOWN:
        wait = int((CODE_REQUEST_COOLDOWN - elapsed).total_seconds())
        raise HTTPException(
            status_code=429, detail=f"너무 자주 요청했습니다. {wait}초 후 다시 시도해주세요."
        )

    code = _generate_code()
    _send_code_or_502(pending.email, code, "resend-code")
    pending.code = code
    pending.expires_at = datetime.now(UTC) + CODE_TTL
    pending.attempts = 0
    pending.created_at = datetime.now(UTC)  # 재발송 쿨다운 기준을 이 시점으로 갱신
    session.add(pending)
    session.commit()

    return SignupResponse()


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(body: ForgotPasswordRequest, session: Session = Depends(get_session)):
    user = _find_user_by_identifier(session, body.identifier)
    # email이 없는 계정(카카오 로그인으로 가입해서 이메일 동의를 안 받은 경우)은 코드를 보낼
    # 주소가 없음 — "계정을 찾을 수 없습니다"와 동일한 메시지로 처리해서 계정 존재 여부가
    # 새지 않게 함(다른 404 케이스와 동일한 원칙).
    if user is None or user.email is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    _check_not_rate_limited(session, PasswordReset, user.id)

    code = _generate_code()
    _send_code_or_502(user.email, code, "forgot-password", send_fn=send_password_reset_code)
    _issue_code(session, PasswordReset, user.id, code)

    return ForgotPasswordResponse()


@router.post("/reset-password", response_model=ForgotPasswordResponse)
def reset_password(body: ResetPasswordRequest, session: Session = Depends(get_session)):
    user = _find_user_by_identifier(session, body.identifier)
    if user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    reset = _consume_code(session, PasswordReset, user.id, body.code, "재설정 코드")

    user.hashed_password = hash_password(body.new_password)
    session.add(reset)
    session.add(user)
    session.commit()
    return ForgotPasswordResponse(
        message="비밀번호가 재설정되었습니다. 새 비밀번호로 로그인해주세요."
    )


def _build_token_response(session: Session, user: User) -> TokenResponse:
    saved_spec = session.exec(select(SavedSpec).where(SavedSpec.user_id == user.id)).first()
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        spec_completed=saved_spec is not None,
    )


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, session: Session = Depends(get_session)):
    invalid_credentials = HTTPException(
        status_code=401, detail="아이디 또는 비밀번호가 일치하지 않습니다."
    )

    user = session.exec(select(User).where(User.username == body.username)).first()
    # hashed_password가 None인 계정은 카카오 등 소셜 전용 계정 — verify_password()에 None을
    # 넘기면 bcrypt가 그대로 터지므로 여기서 먼저 안내 메시지로 막음(사용자 입장에서
    # "아이디/비밀번호가 틀렸다"보다 훨씬 명확한 안내).
    if user is not None and user.hashed_password is None:
        raise HTTPException(
            status_code=401,
            detail="이 계정은 카카오 로그인으로 가입됐습니다. 카카오 로그인을 이용해주세요.",
        )
    if user is None or not verify_password(body.password, user.hashed_password):
        raise invalid_credentials
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="이메일 인증이 완료되지 않았습니다.")

    return _build_token_response(session, user)


@router.post("/kakao", response_model=TokenResponse)
def kakao_login(body: KakaoLoginRequest, session: Session = Depends(get_session)):
    """카카오 OAuth2 인가 코드를 받아 로그인/가입을 한 번에 처리함(핸드셰이크는
    core/kakao.py, 계정 생성/연결 판단은 여기). 세 가지 경로:
    1. 이미 이 kakao_id로 가입된 계정이 있으면 그대로 로그인.
    2. 카카오가 검증된 이메일을 줬고 그 이메일로 이미(비밀번호로) 가입된 계정이 있으면
       kakao_id만 그 계정에 연결 — 비밀번호 로그인도 계속 가능, 두 방식 다 열어둠.
    3. 둘 다 아니면 새 계정 생성. username은 카카오가 nickname 중복 방지를 보장 안 해서
       kakao_id 기반으로 만듦(예: "kakao_123456789"), 비밀번호는 없음(None), 이메일 인증도
       카카오가 이미 신원을 확인한 셈이라 곧바로 is_verified=True.
    """
    try:
        kakao_access_token = exchange_code_for_token(body.code, body.redirect_uri)
        kakao_user = fetch_kakao_user(kakao_access_token)
    except KakaoAuthError as e:
        raise HTTPException(status_code=502, detail=f"카카오 로그인에 실패했습니다: {e}") from e

    user = session.exec(select(User).where(User.kakao_id == kakao_user.kakao_id)).first()

    if user is None and kakao_user.email is not None:
        existing = session.exec(select(User).where(User.email == kakao_user.email)).first()
        if existing is not None:
            existing.kakao_id = kakao_user.kakao_id
            session.add(existing)
            session.commit()
            session.refresh(existing)
            user = existing

    if user is None:
        user = User(
            username=f"kakao_{kakao_user.kakao_id}",
            email=kakao_user.email,
            hashed_password=None,
            is_verified=True,
            kakao_id=kakao_user.kakao_id,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

    return _build_token_response(session, user)


@router.post("/refresh", response_model=TokenResponse)
def refresh(body: RefreshRequest, session: Session = Depends(get_session)):
    try:
        user_id = decode_token(body.refresh_token, expected_type="refresh")
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=401, detail="유효하지 않거나 만료된 리프레시 토큰입니다."
        ) from e

    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )
