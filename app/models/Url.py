from ..core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey


class Url(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_url: Mapped[str] = mapped_column(nullable=False)
    short_url: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    click: Mapped[int] = mapped_column(default=0)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    creator = relationship("User", back_populates="urls")