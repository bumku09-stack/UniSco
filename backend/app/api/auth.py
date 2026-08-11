import secrets
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.core.email import send_password_reset_code, send_verification_code
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
    EmailVerification,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    PasswordReset,
    RefreshRequest,
    ResendCodeRequest,
    ResetPasswordRequest,
    SavedSpec,
    SignupRequest,
    SignupResponse,
    TokenResponse,
    User,
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


@router.post("/signup", response_model=SignupResponse)
def signup(body: SignupRequest, session: Session = Depends(get_session)):
    if session.exec(select(User).where(User.username == body.username)).first():
        raise HTTPException(status_code=409, detail="이미 사용 중인 아이디입니다.")
    if session.exec(select(User).where(User.email == body.email)).first():
        raise HTTPException(status_code=409, detail="이미 사용 중인 이메일입니다.")

    # 메일 발송을 먼저 시도하고, 성공한 경우에만 계정을 만듦 — 순서를 반대로 하면
    # 발송 실패 시 인증 안 된 계정만 DB에 남아서 같은 아이디/이메일로 재가입도
    # 안 되고(409) 로그인도 안 되고(인증 미완료) 재발송도 또 같은 이유로 실패하는
    # 막다른 상태가 됨.
    code = _generate_code()
    _send_code_or_502(body.email, code, "signup")

    user = User(
        username=body.username, email=body.email, hashed_password=hash_password(body.password)
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    session.add(
        EmailVerification(user_id=user.id, code=code, expires_at=datetime.now(UTC) + CODE_TTL)
    )
    session.commit()

    return SignupResponse()


@router.post("/verify-code", response_model=SignupResponse)
def verify_code(body: VerifyCodeRequest, session: Session = Depends(get_session)):
    user = _find_user_by_identifier(session, body.identifier)
    if user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    if user.is_verified:
        raise HTTPException(status_code=400, detail="이미 인증된 계정입니다.")

    verification = session.exec(
        select(EmailVerification)
        .where(EmailVerification.user_id == user.id, EmailVerification.is_used == False)  # noqa: E712
        .order_by(EmailVerification.id.desc())
    ).first()
    if verification is None:
        raise HTTPException(status_code=400, detail="인증 코드가 없습니다. 재발송해주세요.")

    now = datetime.now(UTC)
    expires_at = verification.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if now > expires_at:
        verification.is_used = True
        session.add(verification)
        session.commit()
        raise HTTPException(status_code=400, detail="인증 코드가 만료되었습니다. 재발송해주세요.")

    if verification.attempts >= MAX_ATTEMPTS:
        verification.is_used = True
        session.add(verification)
        session.commit()
        raise HTTPException(status_code=429, detail="시도 횟수를 초과했습니다. 재발송해주세요.")

    if verification.code != body.code:
        verification.attempts += 1
        session.add(verification)
        session.commit()
        raise HTTPException(status_code=400, detail="인증 코드가 일치하지 않습니다.")

    verification.is_used = True
    user.is_verified = True
    session.add(verification)
    session.add(user)
    session.commit()
    return SignupResponse(message="이메일 인증이 완료되었습니다.")


@router.post("/resend-code", response_model=SignupResponse)
def resend_code(body: ResendCodeRequest, session: Session = Depends(get_session)):
    user = _find_user_by_identifier(session, body.identifier)
    if user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    if user.is_verified:
        raise HTTPException(status_code=400, detail="이미 인증된 계정입니다.")

    # 여기서도 발송을 먼저 시도함 — 실패했는데 기존 유효 코드까지 먼저 지워버리면
    # 재시도할 방법이 없어짐 (signup과 같은 이유).
    code = _generate_code()
    _send_code_or_502(user.email, code, "resend-code")

    # 기존에 안 쓴 코드가 남아있으면 무효화 — verify-code가 항상 "최신 코드"만
    # 보게 해서 예전 코드로 통과되는 일이 없게 함
    old_codes = session.exec(
        select(EmailVerification).where(
            EmailVerification.user_id == user.id, EmailVerification.is_used == False  # noqa: E712
        )
    ).all()
    for old in old_codes:
        old.is_used = True
        session.add(old)
    session.add(
        EmailVerification(user_id=user.id, code=code, expires_at=datetime.now(UTC) + CODE_TTL)
    )
    session.commit()

    return SignupResponse()


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(body: ForgotPasswordRequest, session: Session = Depends(get_session)):
    user = _find_user_by_identifier(session, body.identifier)
    if user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    code = _generate_code()
    _send_code_or_502(user.email, code, "forgot-password", send_fn=send_password_reset_code)

    # 기존에 안 쓴 코드가 남아있으면 무효화 — resend-code와 같은 이유(verify가 항상
    # "최신 코드"만 보게 함).
    old_codes = session.exec(
        select(PasswordReset).where(
            PasswordReset.user_id == user.id, PasswordReset.is_used == False  # noqa: E712
        )
    ).all()
    for old in old_codes:
        old.is_used = True
        session.add(old)
    session.add(PasswordReset(user_id=user.id, code=code, expires_at=datetime.now(UTC) + CODE_TTL))
    session.commit()

    return ForgotPasswordResponse()


@router.post("/reset-password", response_model=ForgotPasswordResponse)
def reset_password(body: ResetPasswordRequest, session: Session = Depends(get_session)):
    user = _find_user_by_identifier(session, body.identifier)
    if user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    reset = session.exec(
        select(PasswordReset)
        .where(PasswordReset.user_id == user.id, PasswordReset.is_used == False)  # noqa: E712
        .order_by(PasswordReset.id.desc())
    ).first()
    if reset is None:
        raise HTTPException(status_code=400, detail="재설정 코드가 없습니다. 다시 요청해주세요.")

    now = datetime.now(UTC)
    expires_at = reset.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if now > expires_at:
        reset.is_used = True
        session.add(reset)
        session.commit()
        raise HTTPException(
            status_code=400, detail="재설정 코드가 만료되었습니다. 다시 요청해주세요."
        )

    if reset.attempts >= MAX_ATTEMPTS:
        reset.is_used = True
        session.add(reset)
        session.commit()
        raise HTTPException(status_code=429, detail="시도 횟수를 초과했습니다. 다시 요청해주세요.")

    if reset.code != body.code:
        reset.attempts += 1
        session.add(reset)
        session.commit()
        raise HTTPException(status_code=400, detail="재설정 코드가 일치하지 않습니다.")

    reset.is_used = True
    user.hashed_password = hash_password(body.new_password)
    session.add(reset)
    session.add(user)
    session.commit()
    return ForgotPasswordResponse(
        message="비밀번호가 재설정되었습니다. 새 비밀번호로 로그인해주세요."
    )


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, session: Session = Depends(get_session)):
    invalid_credentials = HTTPException(
        status_code=401, detail="아이디 또는 비밀번호가 일치하지 않습니다."
    )

    user = session.exec(select(User).where(User.username == body.username)).first()
    if user is None or not verify_password(body.password, user.hashed_password):
        raise invalid_credentials
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="이메일 인증이 완료되지 않았습니다.")

    saved_spec = session.exec(select(SavedSpec).where(SavedSpec.user_id == user.id)).first()

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        spec_completed=saved_spec is not None,
    )


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
