from sqlalchemy import DECIMAL, Column, ForeignKey, Integer

from app.db.models.base import Base

__all__ = ["BaseArticle"]


class BaseArticle(Base):
    """
    Базовый класс для статей расходов.

    :param id: int - уникальный идентификатор записи.
    :param user_id: int - идентификатор пользователя в Telegram.
    :param year: int - год, к которому относится статья расходов.
    :param article_id: int - идентификатор статьи расходов.
    :param summ: decimal - сумма, соответствующая статье расходов.
    """

    __abstract__ = True

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.tg_id"), nullable=False)
    year = Column(Integer, nullable=False)

    article_id = Column(Integer, ForeignKey("expense_articles.id"), nullable=False)
    summ = Column(DECIMAL(10, 2), default=0)
