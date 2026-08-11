from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.deps import find_saved_spec, get_current_user, get_saved_spec
from app.core.matching import to_user_spec
from app.db.session import get_session
from app.models import SavedScholarship, SavedSpec, Scholarship, SpecStatusResponse, User, UserSpec

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


@router.get("/saved-scholarships", response_model=list[Scholarship])
def list_saved_scholarships(
    user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    """카드 목록의 하트(찜) 표시를 채우는 데 씀 — 프론트가 이 결과에서 id만 뽑아 Set으로
    만들어 매칭 결과와 클라이언트에서 대조함(app/api/scholarships.py의 save/unsave가
    실제 찜 상태를 바꿈, 여긴 조회 전용)."""
    saved_ids = session.exec(
        select(SavedScholarship.scholarship_id).where(SavedScholarship.user_id == user.id)
    ).all()
    if not saved_ids:
        return []
    return session.exec(select(Scholarship).where(Scholarship.id.in_(saved_ids))).all()
