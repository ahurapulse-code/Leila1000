FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend ./backend
COPY frontend ./frontend
COPY alembic.ini ./alembic.ini
RUN test -f /app/frontend/index.html && test -f /app/frontend/manifest.webmanifest && test -f /app/frontend/worker.js
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
CMD ["sh", "-c", "alembic upgrade head && python -m backend.app.seed && exec uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
