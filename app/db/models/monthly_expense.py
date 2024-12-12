from sqlalchemy import Column, Date, UniqueConstraint, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.models.base_expense import BaseArticle
from app.db.models.auxiliary_tables import Month, Year


# __all__ = ['MonthlyExpense']


# class MonthlyExpense(BaseArticle):
#     __tablename__ = 'monthly_expenses'
#
#     month = Column(Integer, nullable=False)
#
#     __table_args__ = (
#         UniqueConstraint('user_id', 'year', 'month', 'article_id', name='unique_user_month_article'),
#     )

# class MonthlyExpense(BaseExpense):
#     __tablename__ = 'monthly_expenses'
#
#     month_id = Column(Integer, ForeignKey('months.id'), nullable=False)
#     year_id = Column(Integer, ForeignKey('years.id'), nullable=False)
#
#     user_id = Column(Integer, ForeignKey('users.tg_id'), nullable=False)
#     user = relationship('User', back_populates='monthly_expenses')
#
#     month = relationship('Month')
#     year = relationship('Year')
#
#     __table_args__ = (
#         UniqueConstraint('user_id', 'month_id', 'year_id', name='uq_user_month'),
#     )
