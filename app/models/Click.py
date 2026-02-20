from ..core.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from datetime import datetime

class Click(Base):
    __tablename__ = "clicks"

    id: Mapped[int] = mapped_column(primary_key=True)
    url_id: Mapped[int] = mapped_column(ForeignKey("urls.id", ondelete="CASCADE"), nullable=False)
    short_url: Mapped[str] = mapped_column(String(40), nullable=False)

    ip_address: Mapped[str] = mapped_column(String(45))
    user_agent: Mapped[str] = mapped_column(Text)
    country: Mapped[str] = mapped_column(String(2))
    device_type: Mapped[str] = mapped_column(String(20)) 
    browser: Mapped[str] = mapped_column(String(50))
    os: Mapped[str] = mapped_column(String(50))
    
    clicked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())