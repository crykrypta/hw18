from datetime import datetime
from typing import List

from sqlalchemy import Integer, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from db.database import Base
from logs import LogConfig

logger = LogConfig.setup_logging()


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    name: Mapped[str] = mapped_column(String(100), default='unknown')
    language: Mapped[str] = mapped_column(String(10), default='ru')
    request_count: Mapped[int] = mapped_column(Integer, default=0)

    last_request_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)

    # Отношение с DialogContext
    dialog_contexts: Mapped[List["DialogContext"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan")


class DialogContext(Base):
    __tablename__ = "dialog_contexts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    message: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)

    # Отношения с User
    user: Mapped["User"] = relationship(
        back_populates="dialog_contexts")
