from sqlalchemy import Column, Date, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.models.base_expense import BaseArticle


# __all__ = ['DailyExpense']
#
#
# class DailyExpense(BaseArticle):
#     __tablename__ = 'daily_expenses'
#
#     day = Column(Date, nullable=False)  # дата
#
#     user = relationship('User', back_populates='daily_expenses')
#
#     __table_args__ = (
#         UniqueConstraint('user_id', 'day', name='uq_user_day'),
#     )
