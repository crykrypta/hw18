import logging

from typing import List
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, update
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound

from keyboards import requests_limit_keyboard

from db.models import User, DialogContext

from handlers import utils
from states import Chat
from lexicon import lexicon


from exc import UserRequestError, RequestsLimitError


logger = logging.getLogger(__name__)


# Функция для получения обьекта User
async def get_user_by_tg_id(session: AsyncSession, tg_id: int) -> User | None:
    logger.debug('Getting user by tg_id: %d', tg_id)
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
        # Логируем обновление языка пользователя
        logger.info('Обновляем язык пользователя tg_id: %d на %s', tg_id, repr(language)) # noqa
        await session.execute(
            update(User)
            .where(User.tg_id == tg_id)
            .values(language=language)
        )
        await session.commit()

        logger.info('Обновление языка пользователя tg_id: %d - Успешно!', tg_id) # noqa
    except Exception as e:
        logger.error('Ошибка при установке языка пользователя: %s', e)


# Функция для увеличения счетчика запросов пользователя
async def increment_user_request_count(session: AsyncSession, user_id: int):
    user = await session.get(User, user_id)
    if user:  # Если пользователь найден
        current_time = datetime.utcnow()  # Получаем текущее время

        # Если прошло больше 24 часов с последнего запроса - сбросить счетчик запросов  # noqa
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
        logger.error('Пользователь %s не найден', user_id)
        raise UserRequestError('Пользователь %s не найден', user_id)


# Сброс запросов пользователя
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


async def handle_user_request(session, user, max_requests) -> List[str] | str | None: # noqa
    # Увеличиваем счетчик запросов пользователя
    try:
        await increment_user_request_count(session=session, user_id=user.id)
        logger.info('Счетчик запросов увеличен')
    except Exception as e:
        logger.error('Ошибка при увеличении счетчика запросов: %s', e)
        raise UserRequestError('Ошибка при увеличении счетчика запросов')

    # Проверяем количество запросов пользователя
    if user.request_count > max_requests:
        logger.warning('Превышено максимальное количество запросов для user: %d', user.id) # noqa
        raise RequestsLimitError('Превышено максимальное количество запросов')

    try:  # Получаем контекст диалога пользователя
        logger.info('Получаем контекст диалога...')
        context = await session.scalars(
            select(DialogContext.context)
            .where(DialogContext.user_id == user.id)
            .order_by(DialogContext.timestamp.desc())
        )
        await session.commit()
        return context
        logger.info('Dialog context received (SUCESS)')

    except Exception as e:
        logger.error('Ошибка при получении контекста диалога: %s', e)
        raise UserRequestError('Ошибка при получении контекста диалога')


async def set_chat_state(state, state_value):
    """Изменяет состояние state на state_value + логирует
    Args:
        state (FSMContext): state: FSMContext текущего обработчика
        state_value (State()): Конечное состояние"""

    try:
        await state.set_state(state_value)
    except Exception as e:
        logger.error('Ошибка при установке состояния: %s', e)


async def send_limit_exceeded_message(user, generating_msg) -> None:
    """Функция отправки сообщения о том, что лимит запросов исчерпан

    Args:
        user (User): Обьект пользователя User
        generating_msg (message): Редактируемое сообщение
    """
    try:
        await generating_msg.edit_text(
            text=lexicon[user.language]['error']['requests_limit'],
            reply_markup=requests_limit_keyboard(user.language)
        )
        logger.warning('Отправлено сообщение о превышении лимита запросов')
    except Exception as e:
        logger.error('Ошибка при отправке сообщения пользователю: %s', e)


async def handle_user_requests_limit(user, state, generating_msg, rq_limit):
    """Логика, при исчерпывании лимита запросов

    Args:
        user (User): обьект SQLAlchemyORM о пользователе
        state (FSMContext): Текущее состояние контекста

        generating_msg (Message): Изменяемое сообщение
        rq_limit (int): Суточный лимит запросов для текущего пользователя

    Returns:
        bool
    """
    if user.request_count > rq_limit:
        logger.warning('Превышено количество запросов пользователя: %s', user.id) # noqa
        await set_chat_state(state, Chat.requests_limit)
        await send_limit_exceeded_message(user, generating_msg)
        return True
    return False
