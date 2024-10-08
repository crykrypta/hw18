import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from aiogram.fsm.context import FSMContext
from states import Form

from keyboards import choose_lang_keyboard, get_main_keyboard

from db.requests import create_user, set_user_language, get_user_by_tg_id
from db.database import get_session

from lexicon import lexicon

logger = logging.getLogger(__name__)


router = Router()


# /start
@router.message(CommandStart())
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


# Выбор языка
@router.callback_query(Form.language, F.data.in_(['ru', 'eng']))
async def process_choose_lang(callback: CallbackQuery, state: FSMContext):
    language = callback.data
    async for session in get_session():
        user = await get_user_by_tg_id(session, callback.from_user.id)
        await set_user_language(session, callback.from_user.id, language)

    if language == "ru":
        await callback.answer("Вы выбрали русский язык!")
    elif language == "lang_eng":
        await callback.answer("You selected English!")

    text = f"""{lexicon[language]['text']['welcome']}\n
    Осталось запросов: {user.request_count}"""

    await callback.message.edit_text(
        text=text,
        reply_markup=get_main_keyboard(language))

    await state.clear()
