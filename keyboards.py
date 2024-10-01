from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicon import lexicon

# Inline клавиатура для выбора Языка
choose_lang_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Русский', callback_data='ru'),
         InlineKeyboardButton(text='English', callback_data='eng')]
    ]
)


# Inline клавиатура для главного меню
def get_menu_kb(language: str, *args) -> InlineKeyboardMarkup:
    """_summary_

    Args:
        language (str): ru | eng
        *args (str): Актуальные команды /help /start и т.д.
    
    Returns:
        InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    for command in args:
        builder.add(InlineKeyboardButton(
            text=lexicon[language]['buttons'][command],
            callback_data=command))

    return builder.as_markup()
