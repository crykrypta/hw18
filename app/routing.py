from fastapi import FastAPI

from app.models import Query
from app.llms import ChatGPTModel, GigaChatModel

from common.logs import LogConfig
from common.config import load_config

config = load_config()


# Инициализация логгера
logger = LogConfig.setup_logging()

app = FastAPI()


# Модели для запросов к LLM:

# ChatGPT
gpt = ChatGPTModel(
    model='gpt-3.5-turbo',
    temperature=0.1
)
# GigaChat
gigachat = GigaChatModel(token=config.gigachat.auth)


# ENDPOINTS:

# Маршрут для получения ответа от ChatGPT
@app.post("/gpt/query")
async def query_to_chatgpt(query: Query):
    logger.debug('ENDPOINT: /gpt/query')
    try:
        response = await gpt.get_answer(
            topic=query.topic,
            username=query.username,
            dialog_context=query.dialog
        )
        logger.info('Response from ChatGPT received (SUCCESS)')
        return {"content": response}

    except Exception as e:
        logger.error(f'Error while processing request: {e}')


# Маршрут для получения ответа от ChatGPT
@app.post("/sber/gigachat/query")
async def query_to_gigachat(query: Query):
    logger.debug('ENDPOINT: /sber/gigachat/query')
    try:
        response = gigachat.get_answer(
            topic=query.topic,
            username=query.username,
            dialog_context=query.dialog
        )
        return {"content": response}

    except Exception as e:
        logger.error(f'Error while processing request: {e}')
