from sqlalchemy import BigInteger, String
from sqlalchemy.orm import mapped_column, Mapped

from db.database import Base


# Модель пользователя
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    name: Mapped[str] = mapped_column(String(32))
    language: Mapped[str] = mapped_column(String(16))

    def __repr__(self):
        return (f"<User(id={self.id},  \
                username={self.username}, \
                lexicon={self.email})>")
