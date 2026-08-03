from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.core.matching import match_scholarships, to_user_spec
from app.db.session import get_session
from app.models import SavedSpec, Scholarship, User

router = APIRouter()


@router.get("/scholarships", response_model=list[Scholarship])
def list_scholarships(session: Session = Depends(get_session)):
    return session.exec(select(Scholarship)).all()


@router.get("/scholarships/recommendations", response_model=list[Scholarship])
def recommendations(
    user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    saved = session.exec(select(SavedSpec).where(SavedSpec.user_id == user.id)).first()
    if saved is None:
        raise HTTPException(
            status_code=404,
            detail="스펙이 설정되지 않았습니다. POST /users/me/spec으로 먼저 설정해주세요.",
        )
    spec = to_user_spec(saved)
    scholarships = session.exec(select(Scholarship)).all()
    return match_scholarships(scholarships, spec)


# /scholarships/recommendations 뒤에 둬야 함 — 먼저 두면 "recommendations"이
# {scholarship_id}(int)로 해석 시도되다가 실패해서 404/422가 남.
@router.get("/scholarships/{scholarship_id}", response_model=Scholarship)
def get_scholarship(scholarship_id: int, session: Session = Depends(get_session)):
    scholarship = session.get(Scholarship, scholarship_id)
    if scholarship is None:
        raise HTTPException(status_code=404, detail="장학금을 찾을 수 없습니다.")
    return scholarship
