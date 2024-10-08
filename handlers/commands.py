from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart

from aiogram.fsm.context import FSMContext
from states import Form

from db.database import get_session
from db.requests import (get_user_by_tg_id, create_user)

from lexicon import lexicon
from keyboards import choose_lang_keyboard

import logging

logger = logging.getLogger(__name__)


cmd_router = Router()


# /start
@cmd_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    # Логируем начало работы бота
    logger.info('User %d started the bot!', message.from_user.id)

    # Создаем пользователя в БД
    async for session in get_session():
        await create_user(session=session,
                          tg_id=message.from_user.id,
                          name=message.from_user.full_name)
    # Устанавливаем состояние для выбора языка
    await state.set_state(Form.language)
    # И отправляем пользователю клавиатуру для выбора языка
    logger.info('Установлено состояние Form.language')
    await message.answer(
        text=('Привет! Выбери удобный для тебя язык\n'
              'Hi! Choose a language you like'),
        reply_markup=choose_lang_keyboard)


# Команда /help
@cmd_router.message(Command(commands=["help"]))
async def cmd_help(message: Message):
    async for session in get_session():
        user = await get_user_by_tg_id(session, message.from_user.id)
        language = user.laguage
    await message.answer(
        text=lexicon[language]["help"]
    )
