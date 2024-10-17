import logging

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from common.db.database import get_session
from common.db.requests import (get_user_by_tg_id, reset_user_request_count,
                                set_user_language)

from bot.states import Chat, Form
from bot.handlers import utils
from bot.lexicon import lexicon
from bot.keyboards import KeyboardFactory
from bot.keyboards import (get_main_keyboard, choose_lang_keyboard,
                           chat_keyboard, reset_requests_keyboard)


logger = logging.getLogger(__name__)


cb_router = Router()

# ---------------------------MAIN KEYBOARD ----------------------------------


# Кнопка - "Помощь"
@cb_router.callback_query(F.data == 'help')
async def callback_help(callback: CallbackQuery):
    async for session in get_session():
        user = await get_user_by_tg_id(session, callback.from_user.id)
        language = user.language

    # Создаем клавиатуру
    try:
        kb = KeyboardFactory(language=language)
        keyboard = kb.create_keyboard(
            [['to_main', 'ch_lang']]
        )
    except Exception as e:
        logger.error(f'Error while creating keyboard: {e}')
        keyboard = None

    await callback.message.edit_text(
        text=lexicon[language]['commands']["help"],
        reply_markup=keyboard,
        parse_mode='HTML'
    )


# Кнопка - "Сброс запросов"
@cb_router.callback_query(F.data == 'reset_requests')
async def process_reset_requests(callback: CallbackQuery, state: FSMContext):
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
                    reply_markup=reset_requests_keyboard(user.language)
                )


# ---------------------------LANGUAGE CHANGE ----------------------------------

# Кнопка - "Смена языка"
@cb_router.callback_query(F.data == 'ch_lang')
async def process_change_language(callback: CallbackQuery, state: FSMContext):
    logger.debug('Started func: process_change_language..')

    # Устанавливаем состояние на выбор языка
    await state.set_state(Form.language)
    logger.info('State set to Form.language')

    # Отвечаем пользователю
    await callback.message.edit_text(
        text=lexicon['none']['choose_lang'],
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

    try:
        await callback.message.edit_text(
            text=lexicon[language]['text']['welcome'],
            reply_markup=get_main_keyboard(language))
        logger.info('Message edited with new language')
    except Exception as e:
        logger.error('Error while editing message: %s', str(e))

    await state.set_state(None)


# -----------------------------CHAT PROCESS-----------------------------------

# Кнопка - "Начать чат"
@cb_router.callback_query(F.data == 'start_chat')
async def process_chat_start(callback: CallbackQuery, state: FSMContext):
    logger.info('User %d started chat', callback.from_user.id)
    async for session in get_session():
        logger.debug('Getting user by tg_id..')
        user = await get_user_by_tg_id(session, callback.from_user.id)
        logger.debug('User found, id: %s', user.id)

    await state.set_state(Chat.active)
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
    logger.debug('Start handler process_chat_stop..')

    async for session in get_session():
        user = await get_user_by_tg_id(session, callback.from_user.id)

    await state.set_state(None)
    logger.info('user.id == %d;state set to None', user.id)

    await callback.message.edit_text(
        text=lexicon[user.language]['actions']['chat_stop'],
        reply_markup=get_main_keyboard(user.language)
    )


# Кнопка - "На главную"
@cb_router.callback_query(F.data == 'to_main')
async def go_to_main(callback: CallbackQuery):
    logger.info('User %d go to main', callback.from_user.id)
    # Получаем пользователя
    async for session in get_session():
        user = await get_user_by_tg_id(session, callback.from_user.id)

    # Отправляем пользователю главное меню
    await callback.message.edit_text(
        text=lexicon[user.language]['text']['main_menu'],
        reply_markup=get_main_keyboard(user.language)
    )
