import logging
from typing import List

from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat

import openai
from openai import AsyncOpenAI

from common.config import load_config
from app.utils import fabric_user_prompt


# Загрузка конфигурации
config = load_config()
openai.api_key = config.openai_key


logger = logging.getLogger(__name__)


# Класс для работы с ChatGPT
class ChatGPTModel:
    def __init__(self,
                 model: str = 'gpt-3.5-turbo',
                 system: str | None = None,
                 temperature: float = 0.0,
                 proxy: str = config.proxy):
        """
        model (str, optional) = 'gpt-3.5-turbo'.
        system (str | None) = None.
        temperature (float, optional) = 0.0.
        returns:
            str: ответ LLM
        """
        self.client = AsyncOpenAI()
        self.temperature = temperature
        self.model = model

        # Определяем необходимость Default System Prompt
        if system is None:
            self.system = 'Ты - нейроконсультант, пользователь ' \
                          'взаимодействует с тобой через Telegram\n' \
                          'Если контекст диалога не пустой, не привествуй пользователя' # noqa

        else:
            self.system = system

    # Функция получения ответа от ChatGPT
    async def get_answer(self,
                         topic: str,
                         username: str,
                         dialog_context: List[str]) -> str | None:
        """
        query (str): Вопрос пользователя
        username (str): Имя пользователя
        dialog_context (List[str]): История диалога
        """
        logger.info('Начало работы get_answer()..')

        user_message = fabric_user_prompt(
            username=username,
            dialog_context=dialog_context,
            topic=topic
        )

        logger.debug('Отправляем сообщение к ChatGPT: %s', user_message)
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {'role': 'system', 'content': self.system},
                    {'role': 'user', 'content': user_message}
                ]
            )
            logger.info('Response has been received (SUCCESS)')
        except Exception as e:
            logger.error(f'Ошибка при получении ответа от ChatGPT: {e}')
            return None

        return response.choices[0].message.content


class GigaChatModel:
    def __init__(self, token: str):
        self.model = GigaChat(credentials=token,
                              verify_ssl_certs=False)

    # Функция получения ответа от GigaChat
    async def get_answer(self,
                         topic: str,
                         username: str,
                         dialog_context: List[str]) -> str | None:
        """
        query (str): Вопрос пользователя
        username (str): Имя пользователя
        dialog_context (List[str]): История диалога
        """
        logger.debug('Запуск функции fabric_user_prompt()..')

        user_message: str = fabric_user_prompt(
            username=username,
            dialog_context=dialog_context,
            topic=topic
        )

        messages = [
            SystemMessage(content=self.system),
            HumanMessage(content=user_message)
        ]
        try:
            response = self.model(messages=messages)
            logger.info('Ответ от GigaChat получен (SUCCESS)')
        except Exception as e:
            logger.error('Ошибка при получении ответа от GigaChat: %s', e)
            return 'error'

        return response.content
