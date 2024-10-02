from fastapi import FastAPI

from app.models import Query
from app.llms import SimpleLLM


app = FastAPI()
llm = SimpleLLM(
    model='gpt-3.5-turbo',
    temperature=0.1
)


# Маршрут для получения ответа от ChatGPT
@app.get("/gpt/query")
async def query_with_username(query: Query):
    response = await llm.get_answer(query.topic, query.username)
    return {"response": response}
