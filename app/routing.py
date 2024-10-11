import logging

from fastapi import FastAPI
from app.models import Query
from app.llms import SimpleLLM

# Инициализация логгера
logger = logging.getLogger(__name__)

app = FastAPI()
llm = SimpleLLM(
    model='gpt-3.5-turbo',
    temperature=0.1
)


# Маршрут для получения ответа от ChatGPT
@app.post("/gpt/query")
async def query_to_chatgpt(query: Query):
    logger.info('Отправляем запрос в ChatGPT...')
    try:
        response = await llm.get_answer(
            topic=query.topic,
            username=query.username,
            dialog_context=query.dialog
        )
        logger.info('Response from ChatGPT received (SUCCESS)')
        return {"content": response}

    except Exception as e:
        logger.error(f'Error while processing request: {e}')
