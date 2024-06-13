# Используем базовый образ Python для нашего приложения
FROM python:3.12
# Копируем файл requirements.txt
COPY /requirements.txt /usr/src/app/requirements.txt
# Устанавливаем рабочую директорию для Python приложения
WORKDIR /usr/src/app
# Устанавливаем необходимые зависимости
RUN pip install -r requirements.txt

COPY /backend .

# Запускаем Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]