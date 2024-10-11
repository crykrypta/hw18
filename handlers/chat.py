from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from typing import List, Dict

from lexicon import lexicon
from keyboards import chat_keyboard

from db.models import User
from db.database import get_session
from db.requests import (increment_user_request_count,
                         get_user_by_tg_id,
                         get_user_dialog_context,
                         add_dialog_context,
                         handle_user_requests_limit)

from sqlalchemy.exc import SQLAlchemyError

from app.requests import ChatGPTClient

from states import Chat

from handlers import utils

import logging
from exc import RequestsLimitError

logger = logging.getLogger(__name__)


# Создание роутера
msg_router = Router()

MAX_REQUESTS_PER_DAY = 5


# Ответ на Любые текстовые сообщения
@msg_router.message(Chat.active, F.text)
async def chat_process(message: Message, state: FSMContext):
    generating_msg = await message.answer(
        text='Генерация ответа..'
    )

    # Даем запроса в Базу данных
    async for session in get_session():
        logger.info('Получаем обьект user..')
        user: User = await get_user_by_tg_id(
            session=session,
            tg_id=message.from_user.id
        )
        if user:
            logger.info('Обьект user получен (SUCCESS)')

            try:  # Получаем количество запросов пользователя и увеличиваем его на 1  # noqa
                await increment_user_request_count(
                    session=session,
                    user_id=user.id
                )
            except Exception as e:
                logger.error('Ошибка при увеличении счетчика запросов %s', e)

            # Пользователь исчерпал лимит запросов
            if await handle_user_requests_limit(
                user=user,
                state=state,
                generating_msg=generating_msg,
                rq_limit=MAX_REQUESTS_PER_DAY
            ):
                return  # STOP

            try:  # Получаем контекст диалога пользователя
                logger.info('Получаем контекст диалога...')
                context: List[str] = await get_user_dialog_context(
                    session=session,
                    user_id=user.id
                )
                logger.info('Контекст диалога получен (SUCCESS)')

            except RequestsLimitError:
                logger.warning('Превышено количество запросов пользователя: %s', user.id) # noqa
                state.set_state(Chat.requests_limit)

            except Exception as e:
                logger.error('Ошибка при получении контекста диалога: %s', e) # noqa
                context = []

            # ---------------- CONNECT TO FAST API ----------------------|
            logger.info('Подключаемся к FastAPI...')
            client: Dict = ChatGPTClient(base_url='http://127.0.0.1:5000')

            logger.info('Отправляем запрос API на получение ответа...')
            try:
                response = await client.fetch_model_answer(
                    topic=message.text,
                    username=user.name,
                    dialog=context
                )
                logger.info('Ответ от API получен (SUCCESS)')
            except Exception as e:
                logger.error(f'Ошибка при получении ответа от API: {e}') # noqa
                response = {'content': 'Извините, произошла ошибка'}
            finally:
                # </Закрываем сессию FastAPI>
                await client.session.close()

            # ---------------ADD CONTEXT TO DATABASE---------------------|
            try:
                await add_dialog_context(
                    session=session,
                    user_id=user.id,
                    user_message=message.text,
                    model_message=response['content']
                )
                await session.commit()
                await session.refresh(user)
                logger.info('Контекст диалога добавлен в БД (SUCCESS)')

            except SQLAlchemyError as e:
                logger.error(f'Ошибка при добавлении контекста диалога: {e}') # noqa

            # Отправляем ответ пользователю
            try:
                logger.info('Отправляем ответ пользователю...')
                await generating_msg.edit_text(
                    text=utils.message_and_requests(
                        message=response['content'], request_count=user.request_count # noqa
                    ),
                    reply_markup=chat_keyboard(user.language)
                )
            except Exception as e:
                logger.error(f'Ошибка при отправке ответа пользователю: {e}') # noqa

        else:  # Пользователь не найден
            logger.error('Пользователь не найден')
            await generating_msg.edit_text(
                text=lexicon[user.language]['error']['user_not_found']
            )
