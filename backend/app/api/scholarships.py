from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db.session import get_session
from app.models import Scholarship

router = APIRouter()


@router.get("/scholarships", response_model=list[Scholarship])
def list_scholarships(session: Session = Depends(get_session)):
    return session.exec(select(Scholarship)).all()
