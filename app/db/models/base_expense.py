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





# def expense_column():
#     return Column(DECIMAL(10, 2), default=0, server_default='0')
#
#
# class BaseExpense(Base):
#     __abstract__ = True
#
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('users.tg_id'), nullable=False)
#
#     products = expense_column()
#     eating_out = expense_column()
#     transport = expense_column()
#     household = expense_column()
#     health = expense_column()
#     purchases = expense_column()
#     entertainment = expense_column()
#     services = expense_column()
#     debts = expense_column()
#     friends_and_family = expense_column()
#     education = expense_column()
#     devices = expense_column()
#     cosmetics_and_care = expense_column()
#     travel = expense_column()
#     alcohol = expense_column()
#     cigarettes = expense_column()
#     sport = expense_column()
#     pets = expense_column()
#     charity = expense_column()
#     total = expense_column()




