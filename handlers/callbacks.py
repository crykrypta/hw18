from aiogram import Router, F
from aiogram.types import CallbackQuery

from db.database import get_session
from db.requests import get_user_by_tg_id, reset_user_request_count

from keyboards import get_main_keyboard, choose_lang_keyboard
from lexicon import lexicon

import logging

logger = logging.getLogger(__name__)


cmd_router = Router()


# Кнопка - "Помощь"
@cmd_router.callback_query(F.data == 'help')
async def callback_help(callback: CallbackQuery):
    async for session in get_session():
        user = await get_user_by_tg_id(session, callback.from_user.id)
        language = user.language

    await callback.message.answer(
        text=lexicon[language]['commands']['help']
    )


# Кнопка - "Сброс запросов"
@cmd_router.callback_query(F.data == 'reset_requests')
async def process_reset_requests(callback: CallbackQuery):
    logger.debug('Started func: process_reset_requests..')
    async for session in get_session():
        # Получаем пользователя
        logger.debug('Getting user by tg_id..')
        user = await get_user_by_tg_id(session, callback.from_user.id)

        try:  # Пытаемся обновить User.requests_count
            await reset_user_request_count(session, user.id)
            await session.commit()
            logger.info('User.requests_count reseted (SUCCESS)')
        except Exception as e:  # Если ошибка, откатываем транзакцию
            logger.error('Error while reseting User.requests_count: %s', str(e))
            await session.rollback()

        await callback.message.edit_text(
                    text=lexicon[user.language]['actions']['reset_requests'],
                    reply_markup=get_main_keyboard(user.language)
                )


# Кнопка - "Смена языка"
@cmd_router.callback_query(F.data == 'ch_lang')
async def process_change_language(callback: CallbackQuery):
    logger.debug('Started func: process_change_language..')
    async for session in get_session():
        # Получаем пользователя
        logger.debug('Getting user by tg_id..')
        user = await get_user_by_tg_id(session, callback.from_user.id)

        await callback.message.edit_text(
            text=lexicon[user.language]['actions']['ch_lang'],
            reply_markup=choose_lang_keyboard
        )


#