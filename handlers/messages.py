from aiogram import Router, F
from aiogram.types import Message

from typing import List, Dict

from lexicon import lexicon
from keyboards import get_main_keyboard

from db.models import User
from db.database import get_session
from db.requests import (increment_user_request_count,
                         get_user_by_tg_id,
                         get_user_dialog_context,
                         add_dialog_context)

from app.requests import ChatGPTClient
from handlers import utils

import logging

logger = logging.getLogger(__name__)


# Создание роутера
msg_router = Router()

max_requests = 5


# Ответ на Любые текстовые сообщения
@msg_router.message(F.text)
async def any_text(message: Message):
    logger.info('Даем запрос в базу данных по <username>')
    generating_msg = await message.answer(
        text='Генерация ответа..'
    )

    # Даем запроса в Базу данных
    async for session in get_session():
        user: User = await get_user_by_tg_id(
            session=session,
            tg_id=message.from_user.id
        )
        if user:
            # Увеличиваем счетчик запросов пользователя
            await increment_user_request_count(session=session,
                                               user_id=user.id)
            # Проверяем количество запросов пользователя
            if user.request_count <= max_requests:  # OK
                # Получаем контекст диалога пользователя
                logger.info('ПОЛУЧАЕМ КОНТЕКСТ ДИАЛОГА')
                context: List[str] = await get_user_dialog_context(
                    session=session,
                    user_id=user.id
                )
                await session.commit()
                await session.refresh(user)
                logger.info(f'КОНТЕКСТ ДИАЛОГА ПОЛУЧЕН: {context}')

                # <Подключаемся к FastAPI>
                client: Dict = ChatGPTClient(base_url='http://127.0.0.1:5000')

                logger.info(f'ОТПРАВЛЯЕМ ЗАПРОС К FastAPI topic: {message.text}, dialog: {context}') # noqa
                response = await client.fetch_model_answer(
                    topic=message.text,
                    username=user.name,
                    dialog=context
                )
                # </Закрываем сессию FastAPI>
                await client.session.close()

                # Добавляем контекст диалога в Базу данных
                await add_dialog_context(
                    session=session,
                    user_id=user.id,
                    user_message=message.text,
                    model_message=response['content']
                )

                await session.commit()
                await session.refresh(user)

                # Отправляем ответ пользователю
                await generating_msg.edit_text(
                    text=utils.message_and_requests(
                        message=response['content'],
                        request_count=user.request_count,
                    )
                )

            else:  # Превышено количество запросов
                logger.error(f'Requests limit user_id: {user.id}')
                await generating_msg.edit_text(
                    text=lexicon[user.language]['error']['requests_limit'],
                    reply_markup=get_main_keyboard(user.language)
                )

        else:  # Пользователь не найден
            logger.error('Пользователь не найден')
            await generating_msg.edit_text(
                text=lexicon[user.language]['error']['user_not_found']
            )


# Ответ на голосовые сообщения
@msg_router.message(F.voice)
async def any_voice(message: Message):
    async for session in get_session():
        user = get_user_by_tg_id(session=session, tg_id=message.from_user.id)
        language = user.language
    await message.answer(
        text=lexicon[language]['types']['voice']
    )


# Ответ на фотографии
@msg_router.message(F.photo)
async def process_get_photo(message: Message):
    # Загрузка фотографии
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    destination_path = f'content/photos/{photo.file_id}.jpg'
    await message.bot.download_file(
        file_path=file.file_path,
        destination=destination_path
    )
    logger.info('Фото сохранено по пути: %s', destination_path)

    async for session in get_session():  # Получаем язык пользователя
        user = get_user_by_tg_id(session=session, tg_id=message.from_user.id)
        language = user.language
    # Ответ пользователю
    await message.answer(
        text=lexicon[language]['types']['photo']
    )
