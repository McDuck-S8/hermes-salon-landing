FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data

# Health check
HEALTHCHECK --interval=60s --timeout=10s \
  CMD python -c "from aiogram import Bot; import os; Bot(token=os.environ['BOT_TOKEN'])" || exit 1

CMD ["python", "main.py"]
