FROM python:3.12-slim

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Persist the SQLite DB outside the image layer
VOLUME ["/app/data"]

CMD ["python", "bot.py"]
