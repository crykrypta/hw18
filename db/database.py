from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base

from config import load_config
from logs import LogConfig

logger = LogConfig.setup_logging()

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
        try:
            yield session  # Передаем сессию для использования
        except Exception as e:
            logger.error(f"Ошибка во время операции с сессией: {str(e)}")
            await session.rollback()  # Откат в случае ошибки
        finally:
            await session.close()  # Закрываем сессию после использования


# Инициализация базы данных
async def init_db():
    try:
        async with engine.begin() as conn:
            logger.info("Creating tables...")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Tables created!")
    except Exception as e:
        logger.error(f"Error during table creation: {str(e)}")
