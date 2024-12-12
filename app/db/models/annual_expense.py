from sqlalchemy import Column, Date, UniqueConstraint, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.models.base_expense import BaseArticle
from app.db.models.auxiliary_tables import Year


# __all__ = ['AnnualExpense']


# class AnnualExpense(BaseArticle):
#     __tablename__ = 'annual_expenses'
#
#     __table_args__ = (
#         UniqueConstraint('user_id', 'year', 'article_id', name='unique_user_year_article'),
#     )
