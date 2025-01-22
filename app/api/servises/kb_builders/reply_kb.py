from aiogram.utils.keyboard import ReplyKeyboardBuilder


class ReplyKeyBoard:
    @classmethod
    def create_kb(cls, buttons: list[str]) -> str:
        """
        Создает клавиатуру с заданными кнопками.

        :param buttons: list[str] - список строк с текстами для кнопок.
        :return: str - разметка клавиатуры для отправки пользователю.
        """
        builder = ReplyKeyboardBuilder()
        cls._create_buttons(buttons=buttons, builder=builder)
        builder.adjust(1)
        return builder.as_markup()

    @classmethod
    def _create_buttons(cls, buttons: list[str], builder: ReplyKeyboardBuilder):
        """
        Добавляет кнопки в клавиатуру.

        :param buttons: list[str] - список строк с текстами для кнопок.
        :param builder: ReplyKeyboardBuilder - объект для построения клавиатуры.
        """
        for button in buttons:
            builder.button(text=button)
