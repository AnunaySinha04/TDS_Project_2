FROM python:3.11-slim

WORKDIR /app

# system deps that might be needed by some packages
RUN apt-get update && apt-get install -y build-essential libpq-dev libssl-dev wget && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--limit-concurrency", "100"]
