FROM python:3.11.5

WORKDIR /app

COPY ./bot ./bot
COPY ./common ./common

RUN pip install --no-cache-dir -r ./bot/requirements.txt

ENTRYPOINT ["python3", "-m", "bot.main"]