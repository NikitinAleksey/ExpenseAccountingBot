from app.api.servises.texts.texts import texts
from app.db.models.expense_articles import (AlcoholArticle, CharityArticle,
                                            CigarettesArticle,
                                            CosmeticsAndCareArticle,
                                            DebtsArticle, DevicesArticle,
                                            EatingOutArticle, EducationArticle,
                                            EntertainmentArticle,
                                            FriendsAndFamilyArticle,
                                            HealthArticle, HouseholdArticle,
                                            PetsArticle, ProductsArticle,
                                            PurchasesArticle, ServicesArticle,
                                            SportArticle, TransportArticle,
                                            TravelArticle)


class ExpenseArticleMapping:
    data = texts["mapping_rus_to_classname"]

    @classmethod
    def get_class_from_article_name(cls, article_name: str):
        """
        Возвращает класс, соответствующий названию статьи расходов.

        :param article_name: str - название статьи расходов.
        :return: class - класс, соответствующий статье расходов, или None, если
                класс не найден.
        """
        class_name = cls.data.get(article_name.lower())
        if class_name:
            current_class = globals().get(class_name)
            return current_class


class ExpenseLimitsArticleMapping:
    data = texts["mapping_rus_to_eng"]

    @classmethod
    def get_field_name_from_article_name(cls, article_name: str):
        """
        Возвращает имя поля, соответствующее названию статьи расходов.

        :param article_name: str - название статьи расходов.
        :return: str - имя поля, соответствующее статье расходов, или None, если
                имя поля не найдено.
        """
        return cls.data.get(article_name)
