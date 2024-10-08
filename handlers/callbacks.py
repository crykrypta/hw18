from aiogram import Router, F
from aiogram.types import CallbackQuery

from aiogram.fsm.context import FSMContext
from states import Chat, Form

from db.database import get_session
from db.requests import (get_user_by_tg_id, reset_user_request_count,
                         set_user_language)

from handlers import utils

from keyboards import get_main_keyboard, choose_lang_keyboard, chat_keyboard
from lexicon import lexicon

import logging

logger = logging.getLogger(__name__)


cb_router = Router()

# ---------------------------MAIN KEYBOARD ----------------------------------


# Кнопка - "Помощь"
@cb_router.callback_query(F.data == 'help')
async def callback_help(callback: CallbackQuery):
    async for session in get_session():
        user = await get_user_by_tg_id(session, callback.from_user.id)
        language = user.language

    await callback.message.answer(
        text=lexicon[language]['commands']['help']
    )


# Кнопка - "Сброс запросов"
@cb_router.callback_query(F.data == 'reset_requests')
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
            logger.error('Error while reseting User.requests_count: %s', str(e)) # noqa
            await session.rollback()

        await callback.message.edit_text(
                    text=lexicon[user.language]['actions']['reset_requests'],
                    reply_markup=get_main_keyboard(user.language)
                )


# ---------------------------LANGUAGE CHANGE ----------------------------------

# Кнопка - "Смена языка"
@cb_router.callback_query(F.data == 'ch_lang')
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


# Кнопки `ru` и `eng` для выбора языка
@cb_router.callback_query(Form.language, F.data.in_(['ru', 'eng']))
async def process_choose_lang(callback: CallbackQuery, state: FSMContext):
    logger.debug('Started func: process_choose_lang..')
    language = callback.data
    async for session in get_session():
        try:
            await set_user_language(session, callback.from_user.id, language)
            await session.commit()
            logger.info('User %d set language to %s', callback.from_user.id, language) # noqa
        except Exception as e:
            logger.error('Error while setting language: %s', str(e))
            await session.rollback()

    await callback.message.edit_text(
        text=lexicon[language]['text']['welcome'],
        reply_markup=get_main_keyboard(language))

    await state.reset_state()


# -----------------------------CHAT PROCESS-----------------------------------

# Кнопка - "Начать чат"
@cb_router.callback_query(F.data == 'start_chat')
async def process_chat_start(callback: CallbackQuery, state: FSMContext):
    logger.info('User %d started chat', callback.from_user.id)
    async for session in get_session():
        logger.debug('Getting user by tg_id..')
        user = await get_user_by_tg_id(session, callback.from_user.id)
        logger.debug('User found, id: %s', user.id)

    state.set_state(Chat.active)
    logger.info('State set to Chat.activate')

    await callback.message.edit_text(
        text=(utils.message_and_requests(
            lexicon[user.language]['actions']['chat_start'],
            request_count=user.request_count)
        ),
        reply_markup=chat_keyboard(user.language)
    )


# Кнопка - "Остановить чат"
@cb_router.callback_query(Chat.active, F.data == 'chat_stop')
async def process_chat_stop(callback: CallbackQuery, state: FSMContext):
    logger.debug('Started func: process_chat_stop..')
    await state.reset_state()
