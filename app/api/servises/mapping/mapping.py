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
    ServicesArticle
)


class ExpenseArticleMapping:
    data = {
        'алкоголь': 'AlcoholArticle',
        'благотворительность': 'CharityArticle',
        'долги и кредиты': 'DebtsArticle',
        'домашнее хозяйство': 'HouseholdArticle',
        'еда вне дома': 'EatingOutArticle',
        'здоровье': 'HealthArticle',
        'косметика и уход': 'CosmeticsAndCareArticle',
        'образование': 'EducationArticle',
        'питомцы': 'PetsArticle',
        'покупки': 'PurchasesArticle',
        'продукты': 'ProductsArticle',
        'путешествия': 'TravelArticle',
        'развлечения': 'EntertainmentArticle',
        'семья и друзья': 'FriendsAndFamilyArticle',
        'сигареты': 'CigarettesArticle',
        'спорт': 'SportArticle',
        'техника': 'DevicesArticle',
        'транспорт': 'TransportArticle',
        'услуги': 'ServicesArticle',
    }

    @classmethod
    def get_class_from_article_name(cls, article_name: str):
        class_name = cls.data.get(article_name.lower())
        if class_name:
            current_class = globals().get(class_name)
            return current_class
        # return article_name


class ExpenseLimitsArticleMapping:
    data = {
        'алкоголь': 'alcohol',
        'благотворительность': 'charity',
        'долги и кредиты': 'debts',
        'домашнее хозяйство': 'household',
        'еда вне дома': 'eating_out',
        'здоровье': 'health',
        'косметика и уход': 'cosmetics_and_care',
        'образование': 'education',
        'питомцы': 'pets',
        'покупки': 'purchases',
        'продукты': 'products',
        'путешествия': 'travel',
        'развлечения': 'entertainment',
        'семья и друзья': 'friends_and_family',
        'сигареты': 'cigarettes',
        'спорт': 'sport',
        'техника': 'devices',
        'транспорт': 'transport',
        'услуги': 'services',
    }

    @classmethod
    def get_field_name_from_article_name(cls, article_name: str):
        return cls.data.get(article_name)
