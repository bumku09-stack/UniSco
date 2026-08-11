from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.deps import find_saved_spec, get_current_user, get_saved_spec
from app.core.matching import to_user_spec
from app.core.security import verify_password
from app.db.session import get_session
from app.models import (
    DeleteAccountRequest,
    EmailVerification,
    PasswordReset,
    SavedScholarship,
    SavedSpec,
    Scholarship,
    SpecStatusResponse,
    User,
    UserSpec,
)

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


@router.delete("", status_code=204)
def delete_account(
    body: DeleteAccountRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """계정 완전 삭제. 되돌릴 수 없음 — 비밀번호 재확인을 받은 뒤에만 실행함(모델 쪽
    DeleteAccountRequest 주석 참고). FK가 CASCADE로 안 걸려있어서(schema.sql 기준) 참조하는
    테이블들을 먼저 지우고 마지막에 User를 지움 — 순서가 바뀌면 FK 제약 위반으로 실패함."""
    if not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")

    for model in (SavedScholarship, SavedSpec, EmailVerification, PasswordReset):
        rows = session.exec(select(model).where(model.user_id == user.id)).all()
        for row in rows:
            session.delete(row)
    session.delete(user)
    session.commit()
