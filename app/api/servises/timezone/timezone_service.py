import re


def parse_timezone(message: str) -> int | None:
    """
    Разбирает сообщение с часовым поясом и возвращает целое число, обозначающее часовой пояс.

    :param message: Строка вида "Город (UTC±HH:MM)".
    :return: Часовой пояс в виде целого числа (например, +3 для UTC+03:00).
    """
    message = message.replace('−', '-')
    match = re.search(r"UTC\s*([+\-−]?\d+):\d+", message)
    if match:
        return int(match.group(1))
    raise ValueError("Часовой пояс не найден в сообщении. Попробуйте снова.")






