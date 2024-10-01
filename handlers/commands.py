import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from db.database import get_session
from db.requests import get_user_language

from lexicon import lexicon


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s '
                    '%(name)s - %(message)s ')

logger = logging.getLogger(__name__)

cmd_router = Router()


# Команда /help
@cmd_router.message(Command(commands=["help"]))
async def cmd_help(message: Message):
    async for session in get_session():
        language = await get_user_language(
            session,
            message.from_user.id
        )

    await message.answer(
        text=lexicon[language]["help"]
    )


# Кнопка - help
@cmd_router.callback_query(F.data == 'help')
async def callback_help(callback: CallbackQuery):
    async for session in get_session():
        language = await get_user_language(
            session,
            callback.from_user.id
        )

    await callback.message.answer(
        text=lexicon[language]['commands']['help']
    )
