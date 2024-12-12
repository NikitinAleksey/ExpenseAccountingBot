from sqlalchemy import Column, Integer, String
from app.db.models.base import Base


# __all__ = ['Month', 'Year']
#
#
# class Month(Base):
#     __tablename__ = 'months'
#
#     id = Column(Integer, primary_key=True)
#     title = Column(String(10), nullable=False)
#
#
# class Year(Base):
#     __tablename__ = 'years'
#
#     id = Column(Integer, primary_key=True)
#     year = Column(Integer, nullable=False, unique=True)
