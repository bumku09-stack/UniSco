from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.deps import get_current_user, get_saved_spec
from app.core.matching import find_similar, match_scholarships, to_user_spec
from app.db.session import get_session
from app.models import SavedScholarship, SavedSpec, Scholarship, User

router = APIRouter()


@router.get("/scholarships/recommendations", response_model=list[Scholarship])
def recommendations(
    saved: SavedSpec = Depends(get_saved_spec), session: Session = Depends(get_session)
):
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


@router.get("/scholarships/{scholarship_id}/similar", response_model=list[Scholarship])
def similar_scholarships(
    scholarship_id: int,
    exclude_id: int | None = None,
    limit: int = 3,
    saved: SavedSpec = Depends(get_saved_spec),
    session: Session = Depends(get_session),
):
    """상세페이지 "이런 장학금은 어때요?" 추천 전용 API(2026-08-03 추가) — 전에는 프론트가
    /scholarships로 전체 목록을 받아와 화면에서 직접 골라냈는데(내 조건 필터 없이 분류만
    보고 골랐음), 이제 서버에서 "내 조건에 맞는 것" 안에서만 같은 중분류→대분류→워딩 유사도
    순으로 추려서 내려줌(core/matching.py의 find_similar 참고)."""
    target = session.get(Scholarship, scholarship_id)
    if target is None:
        raise HTTPException(status_code=404, detail="장학금을 찾을 수 없습니다.")

    spec = to_user_spec(saved)
    scholarships = session.exec(select(Scholarship)).all()
    eligible = match_scholarships(scholarships, spec)
    return find_similar(target, eligible, limit=limit, exclude_id=exclude_id)


def _find_saved_scholarship(
    session: Session, user_id: int, scholarship_id: int
) -> SavedScholarship | None:
    return session.exec(
        select(SavedScholarship).where(
            SavedScholarship.user_id == user_id,
            SavedScholarship.scholarship_id == scholarship_id,
        )
    ).first()


@router.post("/scholarships/{scholarship_id}/save", status_code=204)
def save_scholarship(
    scholarship_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """찜하기. 이미 찜한 상태에서 또 눌러도 에러 없이 그냥 넘어감(idempotent) — 프론트가
    현재 찜 여부를 매번 정확히 추적 안 해도 되게(낙관적 업데이트 후 재클릭 등에도 안전)."""
    if session.get(Scholarship, scholarship_id) is None:
        raise HTTPException(status_code=404, detail="장학금을 찾을 수 없습니다.")
    if _find_saved_scholarship(session, user.id, scholarship_id) is None:
        session.add(SavedScholarship(user_id=user.id, scholarship_id=scholarship_id))
        session.commit()


@router.delete("/scholarships/{scholarship_id}/save", status_code=204)
def unsave_scholarship(
    scholarship_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    existing = _find_saved_scholarship(session, user.id, scholarship_id)
    if existing is not None:
        session.delete(existing)
        session.commit()
