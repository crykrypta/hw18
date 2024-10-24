import logging
import aiohttp
from typing import List, Optional

# Инициализация логгера
logger = logging.getLogger(__name__)


class LLMSClient:
    def __init__(self,
                 base_url: str,
                 session: Optional[aiohttp.ClientSession] = None):
        """Инициализация клиента
        Args:
            base_url (str): 127.0.0.1:port
            session (ClientSession): aiohttp сессия
        """
        logger.info('Инициализирован клиент LLMSClient')
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

    async def fetch_chatgpt_answer(self, topic: str, username: str, dialog: List[str]): # noqa
        """Отправляет запрос к ChatGPT через FastAPI-сервис
        args:
            topic (str) - текст сообщения
            username (str) - имя пользователя
            dialog (List[str]) - последние 5 сообщений диалога
        returns:
            answer (dict) - ответ от ChatGPT"""
        logger.info('Начало работы функции fetch_model_answer')
        try:
            # Выполняем асинхронный POST запрос
            async with self.session.post(
                url=f'{self.base_url}/gpt/query',  # 127.0.0.1:5000/gpt/query
                json=self.build_json_payload(topic, username, dialog)  # JSON
            ) as response:

                if response.status == 200:
                    logger.info("Код ответа 200 (SUCCESS!)")
                    return await response.json()
                else:
                    logger.error(f"ОШИБКА ЗАПРОСА API Error: {response.status}") # noqa
                    return None

        except aiohttp.ClientError as e:
            logger.error('Ошибка запроса: %s', e)
            return None
        except Exception as e:
            logger.error('Произошла ошибка: %s', e)

    async def fetch_gigachat_answer(self, topic: str, username: str, dialog: List[str]): # noqa
        """Отправляет запрос к GigaChat через FastAPI-сервис
        args:
            topic (str) - текст сообщения
            username (str) - имя пользователя
            dialog (List[str]) - последние 5 сообщений диалога
        returns:
            answer (dict) - ответ от ChatGPT"""

        try:
            logger.info('Начало работы функции fetch_model_answer')

            payload = self.build_json_payload(topic, username, dialog)
            logger.debug('payload: %s', payload)

            url = f'{self.base_url}/sber/gigachat/query'
            logger.debug('url: %s', url)

            async with self.session.post(url=url, json=payload) as response:
                if response.status == 200:
                    logger.info("FastAPI: 200 (SUCCESS!)")
                    try:
                        return await response.json()
                    except Exception as e:
                        logger.error('Ошибка при -> return response.json(): %s', e) # noqa
                        return None
                else:
                    logger.error(f"FastAPI Error: {response.status}") # noqa
                    return None

        except aiohttp.ClientError as e:
            logger.error('Ошибка запроса: %s', e)
            return None
        except Exception as e:
            logger.error('Произошла ошибка: %s', e)
