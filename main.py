from aiogram import Bot, Dispatcher
import asyncio
import logging

from config import load_config

from handlers.starting import router
from handlers.commands import cmd_router
from handlers.messages import msg_router

from db.database import init_db


# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

# Загрузка конфигурации
config = load_config()

# Создание бота и диспетчера
bot = Bot(token=config.tg_token)
dp = Dispatcher()


# Создание асинхронной функции работы бота
async def main():
    await init_db()
    dp.include_router(router)
    dp.include_router(cmd_router)
    dp.include_router(msg_router)
    await dp.start_polling(bot)

# Запуск бота
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Bot stopped!')
