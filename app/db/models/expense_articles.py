from datetime import datetime

from sqlalchemy import (DECIMAL, BigInteger, Column, DateTime, ForeignKey,
                        Integer)
from sqlalchemy.orm import declared_attr, relationship

from app.db.models.base import Base

__all__ = [
    "BaseArticle",
    "AlcoholArticle",
    "CharityArticle",
    "DebtsArticle",
    "HouseholdArticle",
    "EatingOutArticle",
    "HealthArticle",
    "CosmeticsAndCareArticle",
    "EducationArticle",
    "PetsArticle",
    "PurchasesArticle",
    "ProductsArticle",
    "TravelArticle",
    "EntertainmentArticle",
    "FriendsAndFamilyArticle",
    "CigarettesArticle",
    "SportArticle",
    "DevicesArticle",
    "TransportArticle",
    "ServicesArticle",
]


class BaseArticle(Base):
    """
    Базовая модель статьи расходов.

    :param id: int - уникальный идентификатор статьи.
    :param user_id: int - идентификатор пользователя.
    :param summ: decimal - сумма статьи расходов.
    :param updated_at: datetime - дата и время последнего обновления.
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    user_id = Column(
        BigInteger, ForeignKey("users.tg_id", ondelete="CASCADE"), nullable=False
    )
    summ = Column(DECIMAL(10, 2), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @declared_attr
    def user(cls):
        """
        Связь с пользователем.

        :return: объект связи с пользователем.
        """
        return relationship("User", backref=cls.__tablename__, passive_deletes=True)


class AlcoholArticle(BaseArticle):
    """
    Модель статьи расходов на алкоголь.

    :param id: int - уникальный идентификатор статьи.
    :param user_id: int - идентификатор пользователя.
    :param summ: decimal - сумма расходов на алкоголь.
    :param updated_at: datetime - дата и время последнего обновления.
    """
    __tablename__ = "alcohol"


class CharityArticle(BaseArticle):
    """
    Модель статьи расходов на благотворительность.

    :param id: int - уникальный идентификатор статьи.
    :param user_id: int - идентификатор пользователя.
    :param summ: decimal - сумма расходов на благотворительность.
    :param updated_at: datetime - дата и время последнего обновления.
    """
    __tablename__ = "charity"


class DebtsArticle(BaseArticle):
    """
    Модель статьи расходов на долги.

    :param id: int - уникальный идентификатор статьи.
    :param user_id: int - идентификатор пользователя.
    :param summ: decimal - сумма расходов на долги.
    :param updated_at: datetime - дата и время последнего обновления.
    """
    __tablename__ = "debts"


class HouseholdArticle(BaseArticle):
    """
    Модель статьи расходов на домашние нужды.

    :param id: int - уникальный идентификатор статьи.
    :param user_id: int - идентификатор пользователя.
    :param summ: decimal - сумма расходов на домашние нужды.
    :param updated_at: datetime - дата и время последнего обновления.
    """
    __tablename__ = "household"


class EatingOutArticle(BaseArticle):
    """
    Модель статьи расходов на еду вне дома.

    :param id: int - уникальный идентификатор статьи.
    :param user_id: int - идентификатор пользователя.
    :param summ: decimal - сумма расходов на еду вне дома.
    :param updated_at: datetime - дата и время последнего обновления.
    """
    __tablename__ = "eating_out"


class HealthArticle(BaseArticle):
    """
    Модель статьи расходов на здравоохранение.

    :param id: int - уникальный идентификатор статьи.
    :param user_id: int - идентификатор пользователя.
    :param summ: decimal - сумма расходов на здравоохранение.
    :param updated_at: datetime - дата и время последнего обновления.
    """
    __tablename__ = "health"


class CosmeticsAndCareArticle(BaseArticle):
    """
    Модель статьи расходов на косметику и уход.

    :param id: int - уникальный идентификатор статьи.
    :param user_id: int - идентификатор пользователя.
    :param summ: decimal - сумма расходов на косметику и уход.
    :param updated_at: datetime - дата и время последнего обновления.
    """
    __tablename__ = "cosmetics_and_care"


class EducationArticle(BaseArticle):
    """
    Модель статьи расходов на образование.

    :param id: int - уникальный идентификатор статьи.
    :param user_id: int - идентификатор пользователя.
    :param summ: decimal - сумма расходов на образование.
    :param updated_at: datetime - дата и время последнего обновления.
    """
    __tablename__ = "education"


class PetsArticle(BaseArticle):
    """
    Модель статьи расходов на питомцев.

    :param id: int - уникальный идентификатор статьи.
    :param user_id: int - идентификатор пользователя.
    :param summ: decimal - сумма расходов на питомцев.
    :param updated_at: datetime - дата и время последнего обновления.
    """
    __tablename__ = "pets"


class PurchasesArticle(BaseArticle):
    """
    Модель статьи расходов на покупки.

    :param id: int - уникальный идентификатор статьи.
    :param user_id: int - идентификатор пользователя.
    :param summ: decimal - сумма расходов на покупки.
    :param updated_at: datetime - дата и время последнего обновления.
    """
    __tablename__ = "purchases"


class ProductsArticle(BaseArticle):
    """
    Модель статьи расходов на продукты.

    :param id: int - уникальный идентификатор статьи.
    :param user_id: int - идентификатор пользователя.
    :param summ: decimal - сумма расходов на продукты.
    :param updated_at: datetime - дата и время последнего обновления.
    """
    __tablename__ = "products"


class TravelArticle(BaseArticle):
    """
    Модель статьи расходов на путешествия.

    :param id: int - уникальный идентификатор статьи.
    :param user_id: int - идентификатор пользователя.
    :param summ: decimal - сумма расходов на путешествия.
    :param updated_at: datetime - дата и время последнего обновления.
    """
    __tablename__ = "travel"


class EntertainmentArticle(BaseArticle):
    """
    Модель статьи расходов на развлечения.

    :param id: int - уникальный идентификатор статьи.
    :param user_id: int - идентификатор пользователя.
    :param summ: decimal - сумма расходов на развлечения.
    :param updated_at: datetime - дата и время последнего обновления.
    """
    __tablename__ = "entertainment"


class FriendsAndFamilyArticle(BaseArticle):
    """
    Модель статьи расходов на друзей и семью.

    :param id: int - уникальный идентификатор статьи.
    :param user_id: int - идентификатор пользователя.
    :param summ: decimal - сумма расходов на друзей и семью.
    :param updated_at: datetime - дата и время последнего обновления.
    """
    __tablename__ = "friends_and_family"


class CigarettesArticle(BaseArticle):
    """
    Модель статьи расходов на сигареты.

    :param id: int - уникальный идентификатор статьи.
    :param user_id: int - идентификатор пользователя.
    :param summ: decimal - сумма расходов на сигареты.
    :param updated_at: datetime - дата и время последнего обновления.
    """
    __tablename__ = "cigarettes"


class SportArticle(BaseArticle):
    """
    Модель статьи расходов на спорт.

    :param id: int - уникальный идентификатор статьи.
    :param user_id: int - идентификатор пользователя.
    :param summ: decimal - сумма расходов на спорт.
    :param updated_at: datetime - дата и время последнего обновления.
    """
    __tablename__ = "sport"


class DevicesArticle(BaseArticle):
    """
    Модель статьи расходов на устройства.

    :param id: int - уникальный идентификатор статьи.
    :param user_id: int - идентификатор пользователя.
    :param summ: decimal - сумма расходов на устройства.
    :param updated_at: datetime - дата и время последнего обновления.
    """
    __tablename__ = "devices"


class TransportArticle(BaseArticle):
    """
    Модель статьи расходов на транспорт.

    :param id: int - уникальный идентификатор статьи.
    :param user_id: int - идентификатор пользователя.
    :param summ: decimal - сумма расходов на транспорт.
    :param updated_at: datetime - дата и время последнего обновления.
    """
    __tablename__ = "transport"


class ServicesArticle(BaseArticle):
    """
    Модель статьи расходов на услуги.

    :param id: int - уникальный идентификатор статьи.
    :param user_id: int - идентификатор пользователя.
    :param summ: decimal - сумма расходов на услуги.
    :param updated_at: datetime - дата и время последнего обновления.
    """
    __tablename__ = "services"
