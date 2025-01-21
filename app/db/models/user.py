from sqlalchemy import Column, Integer, String, BigInteger
from sqlalchemy.orm import relationship

from app.db.models.base import Base


__all__ = ["User"]


class User(Base):
    __tablename__ = "users"

    tg_id = Column(BigInteger, primary_key=True)
    name = Column(String(50), nullable=False)
    timezone = Column(Integer, nullable=False)
