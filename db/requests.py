from typing import List
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, update
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound

from db.models import User, DialogContext

from handlers import utils

import logging

logger = logging.getLogger(__name__)


# Функция для получения обьекта User
async def get_user_by_tg_id(session: AsyncSession, tg_id: int) -> User | None:
    try:
        result = await session.execute(
            select(User).where(User.tg_id == tg_id)
        )
        return result.scalar_one()
    except NoResultFound:
        logger.error(f'Пользователь {tg_id} не найден')
        return None
    except Exception as e:
        logger.error(f'Ошибка при получении пользователя: {e}')
        return None


# Функция для создания нового пользователя
async def create_user(session: AsyncSession,
                      tg_id: int,
                      name: str,
                      language: str = 'ru') -> User:
    logger.debug(f'Проверяем наличие: {name} with tg_id {tg_id}')

    # Проверка на наличие пользвователя
    existing_user = await get_user_by_tg_id(session, tg_id)
    if existing_user:
        logger.debug(f'Пользователь {tg_id} уже существует')
        return existing_user

    # Если такого пользователя не существует
    logger.debug(f'Создаем пользователя: {name} with tg_id {tg_id}')
    user = User(tg_id=tg_id, name=name, language=language)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


# Функция для установки языка пользователя
async def set_user_language(session: AsyncSession,
                            tg_id: int,
                            language: str):
    try:
        await session.execute(
            update(User).where(User.tg_id == tg_id).values(language=language)
        )
        await session.commit()
        await session.refresh(User)
        logger.info(f"Язык пользователя {tg_id} успешно обновлен на {language}") # noqa
    except Exception as e:
        logger.error(f'Ошибка при установке языка пользователя: {e}')


# Функция для увеличения счетчика запросов пользователя
async def increment_user_request_count(session: AsyncSession, user_id: int):
    user = await session.get(User, user_id)

    if user:  # Проверка наличия пользователя
        current_time = datetime.utcnow()

        # Если прошло больше 24 часов, сбросить счетчик запросов
        if (current_time - user.last_request_date) >= timedelta(days=1):
            user.request_count = 1
        else:  # Если нет - то увеличить на 1
            user.request_count += 1

        # Обновить дату последнего запроса
        user.last_request_date = datetime.utcnow()
        await session.commit()
        await session.refresh(user)
        return user.request_count
    else:
        logger.error(f'Пользователь {user_id} не найден')
        return None


# Функция для увеличения счетчика запросов пользователя
async def reset_user_request_count(session: AsyncSession, user_id: int):
    user = await session.get(User, user_id)
    if user:
        await session.execute(
            update(User)
            .where(User.id == user.id)
            .values(request_count=0)
        )
        await session.commit()
        await session.refresh(user)
    else:
        logger.error(f'Пользователь {user_id} не найден')


# Получить актуальный контекст диалога для пользователя
async def get_user_dialog_context(
        session: AsyncSession,
        user_id: int) -> List[str]:
    user = await session.get(User, user_id)
    if not user:
        return []

    contexts = await session.scalars(
        select(DialogContext)
        .where(DialogContext.user_id == user.id)
        .order_by(DialogContext.timestamp.desc())
        .limit(5)
    )
    return [context.message for context in contexts.all()]


# Функция для добавления контекста диалога
async def add_dialog_context(
        session: AsyncSession,
        user_id: int,
        user_message: str,
        model_message: str) -> None:
    """Добавляет контекст диалога в базу данных

    Args:
        session (AsyncSession): Текущая сессия
        user_id (int): ID пользователя
        user_message (str): сообщение от пользователя
        model_message (str): сообщение от модели
    """
    user = await session.get(User, user_id)
    if not user:
        logger.warning(f"Пользователь с id {user_id} не найден.")
        return None

    # Собираем в строку контекст диалога с помощью кастомной утилиты
    context = utils.fabric_context_message(user_message, model_message)

    new_context = DialogContext(user_id=user.id, message=context)

    session.add(new_context)

    # Удаляем старые контексты, если их больше 5
    context_count = await session.scalar(
        select(func.count()).select_from(DialogContext)
        .where(DialogContext.user_id == user.id)
    )
    if context_count is not None and context_count > 5:
        oldest_contexts = await session.scalars(
            select(DialogContext)
            .where(DialogContext.user_id == user.id)
            .order_by(DialogContext.timestamp)
            .limit(context_count - 5)
        )
        for context in oldest_contexts:
            await session.delete(context)

    await session.commit()


async def handle_user_request(session, user, max_requests) -> List[str] | str:
    # Увеличиваем счетчик запросов пользователя
    await increment_user_request_count(session=session, user_id=user.id)
    # Проверяем количество запросов пользователя
    if user.request_count > max_requests:
        return "Превышено максимальное количество запросов"
    # Получаем контекст диалога пользователя
    logger.info('ПОЛУЧАЕМ КОНТЕКСТ ДИАЛОГА')
    context = await session.scalars(
        select(DialogContext.context)
        .where(DialogContext.user_id == user.id)
        .order_by(DialogContext.timestamp.desc())
    )
    logger.info(f'КОНТЕКСТ ДИАЛОГА ПОЛУЧЕН: {context}')
    await session.commit()
    return context
