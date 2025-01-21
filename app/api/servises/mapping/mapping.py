from app.db.models.expense_articles import (
    AlcoholArticle,
    CharityArticle,
    DebtsArticle,
    HouseholdArticle,
    EatingOutArticle,
    HealthArticle,
    CosmeticsAndCareArticle,
    EducationArticle,
    PetsArticle,
    PurchasesArticle,
    ProductsArticle,
    TravelArticle,
    EntertainmentArticle,
    FriendsAndFamilyArticle,
    CigarettesArticle,
    SportArticle,
    DevicesArticle,
    TransportArticle,
    ServicesArticle,
)
from app.api.servises.texts.texts import texts


class ExpenseArticleMapping:
    data = texts["mapping_rus_to_classname"]

    @classmethod
    def get_class_from_article_name(cls, article_name: str):
        class_name = cls.data.get(article_name.lower())
        if class_name:
            current_class = globals().get(class_name)
            return current_class
        # return article_name


class ExpenseLimitsArticleMapping:
    data = texts["mapping_rus_to_eng"]

    @classmethod
    def get_field_name_from_article_name(cls, article_name: str):
        return cls.data.get(article_name)
