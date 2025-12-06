from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, bigintpk


class ApiKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[bigintpk]

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    prefix: Mapped[str] = mapped_column(
        String(50), index=True, nullable=False, unique=True
    )

    hashed_key: Mapped[str] = mapped_column(String(255), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)

    user = relationship("User", backref="api_keys")
