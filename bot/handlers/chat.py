import logging

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from typing import List, Dict

from bot.lexicon import lexicon
from bot.keyboards import chat_keyboard, requests_limit_keyboard
from bot.states import Chat
from bot.handlers import utils

from common.config import load_config
from common.db.models import User
from common.db.database import get_session
from common.api_requests import ChatGPTClient
from common.db.requests import (get_user_by_tg_id,
                                get_user_dialog_context,
                                add_dialog_context,
                                handle_user_requests_limit)


logger = logging.getLogger(__name__)

config = load_config()

# Создание роутера
msg_router = Router()

MAX_REQUESTS_PER_DAY = 5


# Ответ на Любые текстовые сообщения
@msg_router.message(Chat.active, F.text)
async def chat_process(message: Message, state: FSMContext):
    generating_msg = await message.answer(
        text='Генерация ответа..'
    )
    # --------------------- DATABASE -----------------------|

    # Даем запроса в Базу данных
    async for session in get_session():
        logger.info('Получаем обьект user..')
        user: User = await get_user_by_tg_id(
            session=session,
            tg_id=message.from_user.id
        )
        if user is None:
            logger.error('Пользователь не найден!')
            await generating_msg.edit_text(
                text=lexicon[user.language]['error']['user_not_found']
            )

        # ПОЛУЧАЕМ КОЛИЧЕСТВО ЗАПРОСОВ
        limit_reached = await handle_user_requests_limit(
            user=user, state=state,
            generating_msg=generating_msg,
            rq_limit=MAX_REQUESTS_PER_DAY
        )
        if limit_reached:  # ЕСЛИ ДОСТИГНУТ ЛИМИТ ЗАПРОСОВ
            logger.warning('Пользователь %d достиг лимита запросов', user.id) # noqa

            state.set_state(Chat.limit_reached)  # STATE -> LIMIT

            await generating_msg.edit_text(
                text=lexicon[user.language]['error']['requests_limit'],
                reply_markup=requests_limit_keyboard(user.language))
            return  # ->|STOP|

        # Если запросы есть идем дальше
        context: List[str] = await get_user_dialog_context(session=session,
                                                           user_id=user.id)

        # ---------------------- FAST API ----------------------|

        # Получем класс ChatGPTClient для взаимодействия с нашим API
        client: Dict = ChatGPTClient(base_url=config.fastapi_url)

        try:
            response = await client.fetch_model_answer(
                topic=message.text,
                username=user.name,
                dialog=context
            )
        except Exception as e:
            logger.error(f'Ошибка при получении ответа от API: {e}') # noqa
            response = {'content': 'Извините, произошла ошибка'}
        finally:
            logger.info('Сессия закрыта')
            await client.session.close()

        await add_dialog_context(session=session, user_id=user.id,
                                 user_message=message.text,
                                 model_message=response['content'])

        await session.commit()
        await session.refresh(user)

        try:  # Отправляем ответ пользователю
            await generating_msg.edit_text(
                text=utils.message_and_requests(message=response['content'],
                                                request_count=user.request_count), # noqa
                reply_markup=chat_keyboard(user.language)
            )
        except Exception as e:
            logger.error(f'Ошибка при отправке ответа пользователю: {e}') # noqa