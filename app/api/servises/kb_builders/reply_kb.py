from aiogram.utils.keyboard import ReplyKeyboardBuilder


class ReplyKeyBoard:
    @classmethod
    def create_kb(cls, buttons: list[str]):
        builder = ReplyKeyboardBuilder()
        cls._create_buttons(buttons=buttons, builder=builder)
        builder.adjust(1)
        return builder.as_markup()

    @classmethod
    def _create_buttons(cls, buttons: list[str], builder: ReplyKeyboardBuilder):
        for button in buttons:
            builder.button(text=button)
