from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from db.database import get_session
from db.requests import get_user_by_tg_id

from lexicon import lexicon

import logging

logger = logging.getLogger(__name__)


cmd_router = Router()


# Команда /help
@cmd_router.message(Command(commands=["help"]))
async def cmd_help(message: Message):
    async for session in get_session():
        user = await get_user_by_tg_id(session, message.from_user.id)
        language = user.laguage
    await message.answer(
        text=lexicon[language]["help"]
    )
