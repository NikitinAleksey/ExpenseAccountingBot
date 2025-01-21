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
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    user_id = Column(
        BigInteger, ForeignKey("users.tg_id", ondelete="CASCADE"), nullable=False
    )

    summ = Column(DECIMAL(10, 2), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @declared_attr
    def user(cls):
        return relationship("User", backref=cls.__tablename__, passive_deletes=True)


class AlcoholArticle(BaseArticle):
    __tablename__ = "alcohol"


class CharityArticle(BaseArticle):
    __tablename__ = "charity"


class DebtsArticle(BaseArticle):
    __tablename__ = "debts"


class HouseholdArticle(BaseArticle):
    __tablename__ = "household"


class EatingOutArticle(BaseArticle):
    __tablename__ = "eating_out"


class HealthArticle(BaseArticle):
    __tablename__ = "health"


class CosmeticsAndCareArticle(BaseArticle):
    __tablename__ = "cosmetics_and_care"


class EducationArticle(BaseArticle):
    __tablename__ = "education"


class PetsArticle(BaseArticle):
    __tablename__ = "pets"


class PurchasesArticle(BaseArticle):
    __tablename__ = "purchases"


class ProductsArticle(BaseArticle):
    __tablename__ = "products"


class TravelArticle(BaseArticle):
    __tablename__ = "travel"


class EntertainmentArticle(BaseArticle):
    __tablename__ = "entertainment"


class FriendsAndFamilyArticle(BaseArticle):
    __tablename__ = "friends_and_family"


class CigarettesArticle(BaseArticle):
    __tablename__ = "cigarettes"


class SportArticle(BaseArticle):
    __tablename__ = "sport"


class DevicesArticle(BaseArticle):
    __tablename__ = "devices"


class TransportArticle(BaseArticle):
    __tablename__ = "transport"


class ServicesArticle(BaseArticle):
    __tablename__ = "services"


# class Total(BaseArticle):
#     __tablename__ = 'total'
#
#     date = Column(DateTime, default=datetime.utcnow)
#     summ = Column(DECIMAL(10, 2), default=0)
