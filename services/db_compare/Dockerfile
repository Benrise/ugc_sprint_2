FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir asyncpg beanie motor

CMD ["python","-u", "pg_vs_mongo.py"]

