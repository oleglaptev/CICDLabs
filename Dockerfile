# ==========================================
# STAGE 1: Builder (Сборка и установка зависимостей)
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /app

# 1. Копируем только production-зависимости для использования кэша Docker
COPY requirements-prod.txt .

# 2. Создаем изолированное виртуальное окружение
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 3. Устанавливаем зависимости без кэша pip (чтобы не раздувать слой)
RUN pip install --no-cache-dir -r requirements-prod.txt


# ==========================================
# STAGE 2: Runtime (Финальный легковесный образ)
# ==========================================
FROM python:3.11-slim AS runtime

WORKDIR /app

# 1. Копируем ТОЛЬКО виртуальное окружение из builder (dev-зависимостей здесь нет!)
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 2. Копируем исходный код приложения
COPY app/ ./app/
COPY run.py .

# 3. Best Practice: Запуск от лица не-root пользователя (Security)
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# 4. Открываем порт
EXPOSE 5000

# 5. Запускаем приложение через production WSGI-сервер gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]