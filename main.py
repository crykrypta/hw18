from aiogram import Bot, Dispatcher
import asyncio

from config import load_config

from handlers.commands import cmd_router
from handlers.chat import msg_router
from handlers.callbacks import cb_router

from db.database import init_db

from aiogram.fsm.storage.redis import RedisStorage, Redis  # NEW

from logs import LogConfig

logger = LogConfig.setup_logging()


# Загрузка конфигурации
config = load_config()

redis = Redis(host=config.redis_host)  # NEW
storage = RedisStorage(redis=redis)  # NEW

# Создание бота и диспетчера
bot = Bot(token=config.tg_token)
dp = Dispatcher(storage=storage)  # NEW


# Создание асинхронной функции работы бота
async def main():
    await init_db()
    dp.include_router(cmd_router)  # Commands
    dp.include_router(cb_router)   # Callbacks
    dp.include_router(msg_router)  # Messages

    await dp.start_polling(bot)

# Запуск бота
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.WARNING('Bot stopped!')
