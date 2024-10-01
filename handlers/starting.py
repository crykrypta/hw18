import logging

from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from aiogram.fsm.context import FSMContext
from states import Form

from sqlalchemy.future import select

from keyboards import choose_lang_keyboard, get_menu_kb

from db.requests import create_user
from db.database import get_session
from db.models import User

from lexicon import lexicon


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s '
                    '%(name)s - %(message)s ')

logger = logging.getLogger(__name__)

router = Router()


# /start
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(Form.language)
    await message.answer(
        text=('Привет! Выбери удобный для тебя язык\n'
              'Hi! Choose a language you like'),
        reply_markup=choose_lang_keyboard)


# Выбор языка
@router.callback_query(Form.language)
async def process_choose_lang(callback: CallbackQuery, state: FSMContext):
    language = callback.data
    async for session in get_session():
        try:
            # Проверка, существует ли уже пользователь
            existing_user = await session.execute(
                select(User).where(User.tg_id == callback.from_user.id)
            )
            user = existing_user.scalar_one_or_none()
            if user:
                logger.info(f"Пользователь {user.name} уже существует.")
                language = user.language
                session.commit()
            else:
                await create_user(
                    session=session,
                    tg_id=callback.from_user.id,
                    name=callback.from_user.username or "Unknown",
                    language=language
                )
                await session.commit()
        except Exception as e:
            await callback.answer("Произошла ошибка при сохранении данных.")
            logging.error(f"Ошибка при сохранении данных: {e}")
            return

    if language == "ru":
        await callback.answer("Вы выбрали русский язык!")
    elif language == "lang_eng":
        await callback.answer("You selected English!")

    await callback.message.edit_text(
        text=lexicon[language]['text']["welcome"],
        reply_markup=get_menu_kb(
            language,
            *lexicon[language]["buttons"].keys()
        )
    )

    await state.clear()
