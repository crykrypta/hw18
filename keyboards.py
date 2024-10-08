import logging

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicon import lexicon

# Инициализация логгера
logger = logging.getLogger(__name__)


# Inline клавиатура для выбора Языка
choose_lang_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Русский', callback_data='ru'),
         InlineKeyboardButton(text='English', callback_data='eng')]
    ]
)


# Inline клавиатура для главного меню
def get_menu_kb(language: str, *args) -> InlineKeyboardMarkup:
    """Клавиатура выбора языка
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

    builder.adjust(1)

    return builder.as_markup()


# Inline клавиатура для главного меню
def get_main_keyboard(language: str) -> InlineKeyboardMarkup:
    """
    Args:
        language (str): Язык 'ru' | 'eng'
    Returns:
        InlineKeyboardMarkup: Клавиатура ((help, ch_lang), (chat_start)) # noqa
    """
    main_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=lexicon[language]['buttons']['help'],
                callback_data='help'),
             InlineKeyboardButton(
                 text=lexicon[language]['buttons']['ch_lang'],
                 callback_data='ch_lang')],
            [InlineKeyboardButton(
                text=lexicon[language]['buttons']['start_chat'],
                callback_data='start_chat')]
        ]
    )
    return main_keyboard


# Inline клавиатура для главного меню
def chat_keyboard(language: str) -> InlineKeyboardMarkup:
    """
    Args:
        language (str): Язык 'ru' | 'eng'
        in_chat (bool): Находится ли пользователь в чате
    Returns:
        InlineKeyboardMarkup: Клавиатура ((help, ch_lang), (reset_requests, chat_stop)) # noqa
    """
    main_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=lexicon[language]['buttons']['help'],
                callback_data='help'),
             InlineKeyboardButton(
                text=lexicon[language]['buttons']['stop_chat'],
                callback_data='chat_stop')],

            [InlineKeyboardButton(
                text=lexicon[language]['buttons']['reset_requests'],
                callback_data='reset_requests')],
        ]
    )
    return main_keyboard
