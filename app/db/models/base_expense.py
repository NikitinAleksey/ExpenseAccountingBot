from sqlalchemy import Column, Integer, DECIMAL, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.models.base import Base


__all__ = ['BaseArticle']


class BaseArticle(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.tg_id'), nullable=False)
    year = Column(Integer, nullable=False)

    article_id = Column(Integer, ForeignKey('expense_articles.id'), nullable=False)  # Ссылка на статью расходов
    summ = Column(DECIMAL(10, 2), default=0)
