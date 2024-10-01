import logging

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base

from config import load_config


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s '
                    '%(name)s - %(message)s ')

logger = logging.getLogger(__name__)

# Получение конфигурации
config = load_config()

# DATABASE URL
DATABASE_URL = config.db_url

# Создание асинхронного движка
engine = create_async_engine(DATABASE_URL, echo=True)

# Создание базы для моделей
Base = declarative_base()

# Создание фабрики сессий
AsyncSessionLocal = sessionmaker(  # type: ignore
    bind=engine,                   # type: ignore
    class_=AsyncSession,           # type: ignore
    expire_on_commit=False
)


# Функция-генератор для получения сессии
async def get_session():
    async with AsyncSessionLocal() as session:
        logger.info("Session created")
        yield session


async def init_db():
    async with engine.begin() as conn:
        logger.info("Creating tables...")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Tables created")
