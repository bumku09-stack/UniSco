from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from app.core.security import InvalidTokenError, decode_token
from app.db.session import get_session
from app.models import SavedSpec, User

_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    session: Session = Depends(get_session),
) -> User:
    """Every /users/me/* and /scholarships/recommendations route depends on
    this instead of taking a user_id param — the JWT's sub claim is the only
    source of "who am I", so there's no way to request another user's data."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")
    try:
        user_id = decode_token(credentials.credentials, expected_type="access")
    except InvalidTokenError as e:
        raise HTTPException(status_code=401, detail="유효하지 않거나 만료된 토큰입니다.") from e

    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
    return user


def find_saved_spec(session: Session, user_id: int) -> SavedSpec | None:
    return session.exec(select(SavedSpec).where(SavedSpec.user_id == user_id)).first()


def get_saved_spec(
    user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> SavedSpec:
    """스펙이 반드시 있어야 하는 라우트용(GET·PUT /users/me/spec,
    /scholarships/recommendations, /scholarships/{id}/similar) — 없으면 404.
    스펙이 없어도 되는 라우트(spec-status, POST /users/me/spec의 "이미 있나" 체크)는
    find_saved_spec을 직접 씀."""
    saved = find_saved_spec(session, user.id)
    if saved is None:
        raise HTTPException(
            status_code=404,
            detail="스펙이 설정되지 않았습니다. POST /users/me/spec으로 먼저 설정해주세요.",
        )
    return saved
