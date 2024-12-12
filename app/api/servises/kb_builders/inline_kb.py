from aiogram.utils.keyboard import InlineKeyboardBuilder


class InlineKeyBoard:
    @classmethod
    def create_kb(cls, buttons: list[list], adjust: int = 2):
        builder = InlineKeyboardBuilder()
        cls._create_buttons(buttons=buttons, builder=builder)
        builder.adjust(adjust)
        return builder.as_markup()

    @classmethod
    def _create_buttons(cls, buttons: list[list], builder: InlineKeyboardBuilder):
        for button in buttons:
            builder.button(text=button[0], callback_data=button[1])
