from sqlalchemy import (DECIMAL, BigInteger, Column, ForeignKey, Integer,
                        UniqueConstraint)
from sqlalchemy.orm import relationship

from app.db.models.base import Base

__all__ = ["MonthlyLimits"]


def get_field():
    return Column(DECIMAL, nullable=True, default=0)


class MonthlyLimits(Base):
    """
    Модель для хранения лимитов расходов на различные категории для пользователей.

    :param id: int - идентификатор записи.
    :param user_id: int - идентификатор пользователя (связь с таблицей пользователей).
    :param alcohol: decimal - лимит расходов на алкоголь.
    :param charity: decimal - лимит расходов на благотворительность.
    :param debts: decimal - лимит расходов на долги.
    :param household: decimal - лимит расходов на бытовые товары.
    :param eating_out: decimal - лимит расходов на походы в рестораны.
    :param health: decimal - лимит расходов на здоровье.
    :param cosmetics_and_care: decimal - лимит расходов на косметику и уход.
    :param education: decimal - лимит расходов на образование.
    :param pets: decimal - лимит расходов на питомцев.
    :param purchases: decimal - лимит расходов на покупки.
    :param products: decimal - лимит расходов на продукты.
    :param travel: decimal - лимит расходов на путешествия.
    :param entertainment: decimal - лимит расходов на развлечения.
    :param friends_and_family: decimal - лимит расходов на друзей и семью.
    :param cigarettes: decimal - лимит расходов на сигареты.
    :param sport: decimal - лимит расходов на спорт.
    :param devices: decimal - лимит расходов на устройства.
    :param transport: decimal - лимит расходов на транспорт.
    :param services: decimal - лимит расходов на услуги.
    :param user: relationship - связь с пользователем.
    """

    __tablename__ = "monthly_limits"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.tg_id"), nullable=False)

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

    user = relationship("User", backref="monthly_limits")
    __table_args__ = (UniqueConstraint("user_id", name="uq_user_monthly_limits"),)
