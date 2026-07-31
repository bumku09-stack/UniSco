from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.core.security import InvalidTokenError, decode_token
from app.db.session import get_session
from app.models import User

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
