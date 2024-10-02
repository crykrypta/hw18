import aiohttp

import logging

logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s - %(levelname)s'
                           '%(name)s - %(message)s ')

logger = logging.getLogger(__name__)


# Отдельная функция для работы с API
async def fetch_model_answer(json_data):
    async with aiohttp.ClientSession() as session:
        url = 'http://127.0.0.1:5000/gpt/query'
        async with session.post(url=url, json=json_data) as response:
            if response.status == 200:
                return await response.json()
            else:
                logger.error(f"API Error: {response.status}")
                return None
