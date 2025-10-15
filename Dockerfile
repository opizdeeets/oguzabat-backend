# Берём минимальный образ Python
FROM python:3.12-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем только файл зависимостей сначала
COPY requirements.txt .

# Устанавливаем только нужные пакеты
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код проекта
COPY . .

# Переменные окружения
ENV PYTHONUNBUFFERED=1

# Команда запуска
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]