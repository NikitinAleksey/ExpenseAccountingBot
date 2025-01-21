from sqlalchemy import Column, Date, UniqueConstraint, Integer, ForeignKey, DECIMAL, BigInteger
from sqlalchemy.orm import relationship

from app.db.models.base import Base


__all__ = ['MonthlyLimits']


def get_field():
    return Column(DECIMAL, nullable=True, default=0)


class MonthlyLimits(Base):
    __tablename__ = 'monthly_limits'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.tg_id'), nullable=False)

    alcohol = get_field()
    charity = get_field()
    debts = get_field()
    household = get_field()
    eating_out = get_field()
    health = get_field()
    cosmetics_and_care = get_field()
    education = get_field()
    pets = get_field()
    purchases = get_field()
    products = get_field()
    travel = get_field()
    entertainment = get_field()
    friends_and_family = get_field()
    cigarettes = get_field()
    sport = get_field()
    devices = get_field()
    transport = get_field()
    services = get_field()

    user = relationship('User', backref='monthly_limits')
    __table_args__ = (
        UniqueConstraint('user_id', name='uq_user_monthly_limits'),
    )
