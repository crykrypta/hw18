import logging

from db.models import User

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


# Функция для создания нового пользователя
async def create_user(session: AsyncSession,
                      tg_id: int,
                      name: str,
                      language: str = 'ru') -> User:
    logger.debug(f'Создаем пользователя: {name} with tg_id {tg_id}')
    user = User(tg_id=tg_id, name=name, language=language)

    logger.debug('Добавляем пользователя в сессию')
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


# Функция для получения списка пользователей
async def get_user_by_tg_id(session: AsyncSession, tg_id: int) -> User | None:
    result = await session.execute(select(User).where(User.tg_id == tg_id))
    return result.scalars().first()


# Функция для получения языка пользователя
async def get_user_language(session: AsyncSession, tg_id: int) -> str | None:
    try:
        result = await session.execute(
            select(User.language).where(User.tg_id == tg_id)
        )
        return result.scalars().first()
    except NoResultFound:
        logger.error(f'Язык пользователя: {tg_id} не найден')
        return 'ru'
    except Exception as e:
        logger.error(f'Ошибка при получении языка пользователя: {e}')
        return 'ru'


# Функция для получения языка пользователя
async def get_username(session: AsyncSession, tg_id: int) -> str | None:
    try:
        result = await session.execute(
            select(User.name).where(User.tg_id == tg_id)
        )
        return result.scalars().first()
    except NoResultFound:
        logger.error(f'Имя пользователя: {tg_id} не найдено')
        return 'unknown'
    except Exception as e:
        logger.error(f'Ошибка при получении имени пользователя: {e}')
        return 'unknown'
