import json


__all__ = ["load_texts"]


def load_texts() -> dict:
    with open("app/api/static/texts.json", "r", encoding="utf-8") as file:
        return json.load(file)


texts = load_texts()
