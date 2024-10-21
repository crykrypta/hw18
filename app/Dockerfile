FROM python:3.11.5

WORKDIR /app

COPY ./app ./app
COPY ./common ./common

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r ./app/requirements.txt

ENTRYPOINT ["uvicorn", "app.routing:app", "--host", "0.0.0.0", "--port", "5000"]