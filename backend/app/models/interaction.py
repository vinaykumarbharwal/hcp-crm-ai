from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Interaction(Base):
    __tablename__ = "interactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    hcp_name: Mapped[str] = mapped_column(String(120), index=True)
    product: Mapped[str] = mapped_column(String(120), index=True)
    sentiment: Mapped[str] = mapped_column(String(40), default="neutral")
    interaction_type: Mapped[str] = mapped_column(String(40), default="Meeting")
    interaction_date: Mapped[str] = mapped_column(String(20), default="")
    interaction_time: Mapped[str] = mapped_column(String(20), default="")
    transcript: Mapped[str] = mapped_column(Text)
    action_items: Mapped[str] = mapped_column(Text, default="[]")
    compliance_status: Mapped[str] = mapped_column(String(40), default="clear")
    resource_request: Mapped[str | None] = mapped_column(String(120), nullable=True)
    competitive_intelligence: Mapped[str | None] = mapped_column(String(160), nullable=True)
    draft_summary: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)