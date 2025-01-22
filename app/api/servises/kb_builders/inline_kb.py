from aiogram.utils.keyboard import InlineKeyboardBuilder


class InlineKeyBoard:
    @classmethod
    def create_kb(cls, buttons: list[list], adjust: int = 2):
        """
        Создает клавиатуру с заданными кнопками и настройками.

        :param buttons: list[list] - список кнопок, каждая кнопка представлена
                        списком с текстом и callback_data.
        :param adjust: int - количество колонок для кнопок в клавиатуре.
        :return: возвращает клавиатуру в виде разметки.
        """
        builder = InlineKeyboardBuilder()
        cls._create_buttons(buttons=buttons, builder=builder)
        builder.adjust(adjust)
        return builder.as_markup()

    @classmethod
    def _create_buttons(cls, buttons: list[list], builder: InlineKeyboardBuilder):
        """
        Создает кнопки для клавиатуры.

        :param buttons: list[list] - список кнопок, каждая кнопка представлена
                        списком с текстом и callback_data.
        :param builder: InlineKeyboardBuilder - объект для построения клавиатуры.
        :return: None
        """
        for button in buttons:
            builder.button(text=button[0], callback_data=button[1])
