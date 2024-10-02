import openai
from openai import AsyncOpenAI

import aiohttp

from config import load_config

# Загрузка конфигурации
config = load_config()
openai.api_key = config.openai_key


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
            self.system = '''Ты - нейроконсультант,
            пользователь взаимодействует с тобой через Telegram\n
            Обращайся к пользователю по имени\n
            Вопросы будут подаваться в формате:
            Имя пользователя: <usename>\n
            Вопрос: <question>\n
            '''
        else:
            self.system = system

    # Функция получения ответа от ChatGPT
    async def get_answer(self, topic: str, username: str) -> str | None:
        """
        query (str): Вопрос пользователя
        username (str): Имя пользователя
        """
        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {'role': 'system', 'content': self.system},
                {'role': 'user',
                    'content': f'Имя пользователя: {username}\n'
                               f'Вопрос пользователя: {topic}'}
            ]
        )
        return response.choices[0].message.content
