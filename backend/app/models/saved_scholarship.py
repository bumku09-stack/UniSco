from datetime import UTC, datetime

from sqlmodel import Field, SQLModel, UniqueConstraint


class SavedScholarship(SQLModel, table=True):
    """유저가 찜한 장학금. 별도 boolean 없이 행 존재 여부로 찜 상태를 표현함 —
    찜하면 행 추가, 취소하면 행 삭제(app/api/scholarships.py의 save/unsave 참고)."""

    __table_args__ = (UniqueConstraint("user_id", "scholarship_id"),)

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    scholarship_id: int = Field(foreign_key="scholarship.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
