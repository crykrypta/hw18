import logging

from aiogram import Router, F
from aiogram.types import Message

from db.database import get_session
from db.requests import get_user_language

from app.routing import query_with_username

from lexicon import lexicon


# Логирование
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s '
                    '%(name)s - %(message)s ')

logger = logging.getLogger(__name__)

# Создание роутера
msg_router = Router()


# Ответ на Любые текстовые сообщения
@msg_router.message(F.text)
async def any_text(message: Message):
    logger.info('Даем запрос в базу данных по <username>')
    async for session in get_session():
        username = await get_user_language(
            session, message.from_user.id
        )

    logger.info('Даем запрос к модели..')

    # Получение ответа от модели
    await message.answer(
        text=query_with_username(
            topic=message.text,
            username=username
        )
    )


# Ответ на голосовые сообщения
@msg_router.message(F.voice)
async def any_voice(message: Message):
    async for session in get_session():
        language = await get_user_language(
            session, message.from_user.id
        )
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

    logger.info('Фото получено')

    await message.bot.download_file(
        file_path=file.file_path,
        destination=destination_path
    )

    logger.info('Фото сохранено по пути: %s', destination_path)
    logger.info('Получаем язык пользователя...')
    # Получение языка пользователя
    async for session in get_session():
        language = await get_user_language(
            session, message.from_user.id
        )
    logger.info('Язык пользователя получен, генерируем ответ...')
    # Ответ пользователю
    await message.answer(
        text=lexicon[language]['types']['photo']
    )
