import logging
import aiohttp
from typing import List, Optional

# Инициализация логгера
logger = logging.getLogger(__name__)


class ChatGPTClient:
    def __init__(self,
                 base_url: str,
                 session: Optional[aiohttp.ClientSession] = None):
        """Инициализация клиента
        Args:
            base_url (str): 127.0.0.1:port
            session (ClientSession): aiohttp сессия
        """
        self.base_url = base_url
        self.session = session or aiohttp.ClientSession()

    # Метод для закрытия сессии
    async def close(self):
        """Закрыть сессию при завершении работы."""
        if not self.session.closed:
            await self.session.close()
            logger.info('Session closed')

    def build_json_payload(self,
                           topic: str,
                           username: str,
                           dialog: List[str]) -> dict:
        """Формируем JSON-данные для запроса
        Args:
            topic (str) - вопрос пользователя
            username (str) - имя пользователя
            dialog (List[str]) - последние 5 сообщений диалога"""
        logger.info("Формирование JSON-данных для запроса..")
        return {
            'topic': topic,
            'username': username,
            'dialog': dialog  # Добавляем историю диалога
        }

    async def fetch_model_answer(self,
                                 topic: str,
                                 username: str,
                                 dialog: List[str]):
        """
        Отправляет запрос к ChatGPT через FastAPI-сервис, возвращает ответ
        args:
            topic (str) - текст сообщения
            username (str) - имя пользователя
            dialog (List[str]) - последние 5 сообщений диалога
        returns:
            answer (dict) - ответ от ChatGPT"""
        try:
            logger.info("Отправляем запрос к API..(./gpt/query)")

            # Выполняем асинхронный POST запрос
            async with self.session.post(
                url=f'{self.base_url}/gpt/query',  # 127.0.0.1:5000/gpt/query
                json=self.build_json_payload(topic, username, dialog)  # JSON
            ) as response:

                if response.status == 200:
                    logger.info("ОТВЕТ 200 ПОЛУЧЕН")
                    return await response.json()
                else:
                    logger.error(f"ОШИБКА ЗАПРОСА API Error: {response.status}") # noqa
                    return None

        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {str(e)}")
            return None
