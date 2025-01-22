import json

__all__ = ["load_texts"]


def load_texts() -> dict:
    """
    Загружает тексты из файла JSON.

    :return: dict - словарь с текстами, загруженными из файла.
    """
    with open("app/api/static/texts.json", "r", encoding="utf-8") as file:
        return json.load(file)


texts = load_texts()

