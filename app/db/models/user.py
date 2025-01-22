from sqlalchemy import BigInteger, Column, Integer, String

from app.db.models.base import Base

__all__ = ["User"]


class User(Base):
    __tablename__ = "users"

    tg_id = Column(BigInteger, primary_key=True)
    name = Column(String(50), nullable=False)
    timezone = Column(Integer, nullable=False)
