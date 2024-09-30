from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton)

reply_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='/start')],
        [KeyboardButton(text='/help')],
    ],
    resize_keyboard=True
)
