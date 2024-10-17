import logging
from typing import List

import openai
from openai import AsyncOpenAI

from common.config import load_config

# Загрузка конфигурации
config = load_config()
openai.api_key = config.openai_key


logger = logging.getLogger(__name__)


# Класс для работы с LLM
class SimpleLLM:
    def __init__(self,
                 model: str = 'gpt-3.5-turbo',
                 system: str | None = None,
                 temperature: float = 0.0):
        """
        model (str, optional) = 'gpt-3.5-turbo'.
        system (str | None) = None.
        temperature (float, optional) = 0.0.
        returns:
            str: ответ LLM
        """

        self.temperature = temperature
        self.model = model
        self.client = AsyncOpenAI()

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
        logger.info('Running method - get_answer..')
        # logger.info('topic: {0}'.format(topic))
        # logger.info('username: {0}'.format(username))
        # logger.info('dialog_context: {0}'.format(*dialog_context))

        try:
            user_message = 'Имя пользователя: {0}\n Контекст диалога: {1}\nОтветь на вопрос: {2}'.format( # noqa
                username, dialog_context, topic
            )
            logger.info('Message has been formed (SUCCESS) ')
        except Exception as e:
            logger.error(f'Ошибка при формировании сообщения пользователя: {e}') # noqa
            return None

        logger.info('Sending request to ChatGPT: {0}'.format(user_message))

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
