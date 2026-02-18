from ..core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from typing import Optional


class Url(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_url: Mapped[str] = mapped_column(nullable=False)
    short_url: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    click: Mapped[int] = mapped_column(default=0)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    creator = relationship("User", back_populates="urls")