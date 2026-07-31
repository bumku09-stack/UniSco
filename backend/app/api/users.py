from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.core.matching import to_user_spec
from app.db.session import get_session
from app.models import SavedSpec, SpecStatusResponse, User, UserSpec

router = APIRouter(prefix="/users/me")


def _get_saved_spec(session: Session, user_id: int) -> SavedSpec | None:
    return session.exec(select(SavedSpec).where(SavedSpec.user_id == user_id)).first()


@router.get("/spec-status", response_model=SpecStatusResponse)
def spec_status(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return SpecStatusResponse(spec_completed=_get_saved_spec(session, user.id) is not None)


@router.post("/spec", response_model=UserSpec)
def create_spec(
    body: UserSpec, user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    if _get_saved_spec(session, user.id) is not None:
        raise HTTPException(
            status_code=409,
            detail="이미 스펙이 설정되어 있습니다. PUT /users/me/spec으로 수정해주세요.",
        )
    saved = SavedSpec(user_id=user.id, **body.model_dump())
    session.add(saved)
    session.commit()
    session.refresh(saved)
    return to_user_spec(saved)


@router.get("/spec", response_model=UserSpec)
def read_spec(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    saved = _get_saved_spec(session, user.id)
    if saved is None:
        raise HTTPException(status_code=404, detail="스펙이 설정되지 않았습니다.")
    return to_user_spec(saved)


@router.put("/spec", response_model=UserSpec)
def update_spec(
    body: UserSpec, user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    saved = _get_saved_spec(session, user.id)
    if saved is None:
        raise HTTPException(
            status_code=404,
            detail="스펙이 설정되지 않았습니다. POST /users/me/spec으로 먼저 생성해주세요.",
        )
    for field, value in body.model_dump().items():
        setattr(saved, field, value)
    session.add(saved)
    session.commit()
    session.refresh(saved)
    return to_user_spec(saved)
