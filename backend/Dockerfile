FROM python:3.12
COPY requirements.txt /usr/src/donStart/backend/requirements.txt
WORKDIR /usr/src/donStart/backend
RUN pip install -r requirements.txt
COPY . .

WORKDIR /usr/src/donStart

CMD sh -c "alembic upgrade head ; uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"