import logging
from typing import List

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
    keyboard = InlineKeyboardMarkup(
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
    return keyboard


# Клавиатура "Превышение лимита запросов"
def requests_limit_keyboard(language: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=lexicon[language]['buttons']['help'],
                callback_data='help'),
             InlineKeyboardButton(
                text=lexicon[language]['buttons']['to_main'],
                callback_data='to_main')],

            [InlineKeyboardButton(
                text=lexicon[language]['buttons']['reset_requests'],
                callback_data='reset_requests')],
        ]
    )
    return keyboard


# Клавиатура "Сброс запросов"
def reset_requests_keyboard(language: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=lexicon[language]['buttons']['help'],
                callback_data='help'),
             InlineKeyboardButton(
                text=lexicon[language]['buttons']['to_main'],
                callback_data='to_main')],
            [InlineKeyboardButton(
                text=lexicon[language]['buttons']['start_chat'],
                callback_data='start_chat')]
        ]
    )
    return keyboard


class KeyboardFactory:
    def __init__(self, language):
        """Конструктор класса KeyboardFactory.
        Создает экземпляр класса с набором кнопок,
        которые могут быть использованы для создания клавиатуры.

        Args:
        language (str): Язык 'ru' | 'eng'"""
        self.buttons = {
            'start_chat': InlineKeyboardButton(
                text=lexicon[language]['buttons']['start_chat'],
                callback_data='start_chat'),
            'stop_chat': InlineKeyboardButton(
                text=lexicon[language]['buttons']['stop_chat'],
                callback_data='chat_stop'),
            'help': InlineKeyboardButton(
                text=lexicon[language]['buttons']['help'],
                callback_data='help'),
            'reset_requests': InlineKeyboardButton(
                text=lexicon[language]['buttons']['reset_requests'],
                callback_data='reset_requests'),
            'to_main': InlineKeyboardButton(
                text=lexicon[language]['buttons']['to_main'],
                callback_data='to_main'),
            'ch_lang': InlineKeyboardButton(
                 text=lexicon[language]['buttons']['ch_lang'],
                 callback_data='ch_lang'),
        }
        logger.debug('KeyboardFactory created!')


    def create_keyboard(self, button_rows: List[List[str]]) -> InlineKeyboardMarkup: # noqa
        """Создает клавиатуру с заданными рядами кнопок.

        Args:
        button_rows (List[List[str]]): Двумерный список из имен кнопок

        Returns:
        InlineKeyboardMarkup:

        Example of using:
        factory = KeyboardFactory('en')
        keyboard = factory.create_keyboard([['start_chat', 'stop_chat'],
                                            ['help', 'reset_requests'],
                                            ['to_main', 'ch_lang']])"""
        keyboard_rows = []
        for row in button_rows:
            buttons = [self.buttons.get(name) for name in row if self.buttons.get(name)] # noqa
            keyboard_rows.append(buttons)

        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)

        logger.debug('Keyboard created!')
        return keyboard
