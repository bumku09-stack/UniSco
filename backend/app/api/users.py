from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.api.deps import find_saved_spec, get_current_user, get_saved_spec
from app.core.matching import to_user_spec
from app.db.session import get_session
from app.models import SavedSpec, SpecStatusResponse, User, UserSpec

router = APIRouter(prefix="/users/me")


@router.get("/spec-status", response_model=SpecStatusResponse)
def spec_status(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return SpecStatusResponse(spec_completed=find_saved_spec(session, user.id) is not None)


@router.post("/spec", response_model=UserSpec)
def create_spec(
    body: UserSpec, user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    if find_saved_spec(session, user.id) is not None:
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
def read_spec(saved: SavedSpec = Depends(get_saved_spec)):
    return to_user_spec(saved)


@router.put("/spec", response_model=UserSpec)
def update_spec(
    body: UserSpec,
    saved: SavedSpec = Depends(get_saved_spec),
    session: Session = Depends(get_session),
):
    for field, value in body.model_dump().items():
        setattr(saved, field, value)
    session.add(saved)
    session.commit()
    session.refresh(saved)
    return to_user_spec(saved)
