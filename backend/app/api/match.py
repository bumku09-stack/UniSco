from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.core.matching import match_scholarships
from app.db.session import get_session
from app.models import Scholarship, UserSpec

router = APIRouter()


@router.post("/match", response_model=list[Scholarship])
def match(spec: UserSpec, session: Session = Depends(get_session)):
    scholarships = session.exec(select(Scholarship)).all()
    return match_scholarships(scholarships, spec)
