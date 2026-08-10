from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.core.matching import match_scholarships
from app.db.session import get_session
from app.models import Scholarship, UserSpec

router = APIRouter()


@router.post("/match", response_model=list[Scholarship])
def match(body: UserSpec, session: Session = Depends(get_session)):
    """로그인 없이 즉석 매칭 — 요청 바디로 받은 스펙을 그 자리에서 채점만 하고 아무것도
    저장 안 함(2026-08-04에 프론트가 안 써서 지웠다가, 2026-08-10 "로그인 없이 가볍게
    둘러보기" 게스트 플로우용으로 다시 붙임 — frontend/src/app/spec/page.tsx가 비로그인
    상태일 때 이 엔드포인트로 보냄). 로그인 유저용 /scholarships/recommendations와 완전히
    같은 core/matching.py의 match_scholarships를 그대로 씀 — 게스트/로그인 유저 사이에
    매칭 로직이 갈릴 일이 없음."""
    scholarships = session.exec(select(Scholarship)).all()
    return match_scholarships(scholarships, body)
