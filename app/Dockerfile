FROM python:3.12.5

WORKDIR /app

COPY requirements.txt /app/

EXPOSE 5000

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

ENTRYPOINT ["uvicorn", "app.routing:app", "--port 5000"]

CMD ["python3", "main.py"]