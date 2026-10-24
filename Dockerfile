# ==========================================
# STAGE 1: Builder (полный образ языка, согласно методичке 5.1.1)
# ==========================================
FROM python:3.11 AS builder

WORKDIR /app

# 1. Сначала ТОЛЬКО манифест зависимостей — ключевой приём для кэширования слоя
COPY requirements-prod.txt .

# 2. Изолированное виртуальное окружение
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 3. Устанавливаем production-зависимости (без кэша pip, чтобы не раздувать слой)
RUN pip install --no-cache-dir -r requirements-prod.txt

# 4. HARDENING: удаляем из venv инструменты сборки.
#    - экономия ~15 МБ в финальном образе;
#    - удаление уязвимых vendored-копий setuptools/wheel
#      (CVE-2026-23949, CVE-2026-24049), на которых падал Trivy Quality Gate.
#    Важно удалить и distutils-precedence.pth, иначе Python будет ругаться
#    при старте на отсутствующий модуль _distutils_hack.
RUN set -eux; \
    VENV_SITE=/opt/venv/lib/python3.11/site-packages; \
    rm -rf "$VENV_SITE/pip" "$VENV_SITE"/pip-*.dist-info \
           "$VENV_SITE/setuptools" "$VENV_SITE"/setuptools-*.dist-info \
           "$VENV_SITE/wheel" "$VENV_SITE"/wheel-*.dist-info \
           "$VENV_SITE/pkg_resources" "$VENV_SITE/_distutils_hack" \
           "$VENV_SITE/distutils-precedence.pth"; \
    rm -f /opt/venv/bin/pip /opt/venv/bin/pip3 /opt/venv/bin/pip3.11 \
          /opt/venv/bin/wheel


# ==========================================
# STAGE 2: Runtime (компактный образ, согласно методичке 5.1.3)
# ==========================================
FROM python:3.11-slim AS runtime

WORKDIR /app

# 1. HARDENING: базовый образ python:3.11-slim несёт pip/setuptools/wheel,
#    которые в runtime не нужны, но содержат уязвимые vendored-зависимости.
#    Удаляем их полностью (минус ~25 МБ и минус 2 HIGH-уязвимости).
RUN set -eux; \
    PY_SITE=/usr/local/lib/python3.11/site-packages; \
    rm -rf "$PY_SITE/pip" "$PY_SITE"/pip-*.dist-info \
           "$PY_SITE/setuptools" "$PY_SITE"/setuptools-*.dist-info \
           "$PY_SITE/wheel" "$PY_SITE"/wheel-*.dist-info \
           "$PY_SITE/pkg_resources" "$PY_SITE/_distutils_hack" \
           "$PY_SITE/distutils-precedence.pth"; \
    rm -f /usr/local/bin/pip /usr/local/bin/pip3 /usr/local/bin/pip3.11 \
          /usr/local/bin/wheel \
          /usr/local/bin/easy_install /usr/local/bin/easy_install-3.11; \
    rm -rf /var/lib/apt/lists/* /root/.cache

# 2. Копируем готовое окружение из builder (dev-зависимостей здесь нет!)
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 3. Копируем исходный код приложения
COPY app/ ./app/
COPY run.py .

# 4. Best Practice: запуск от лица не-root пользователя
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

# 5. Запуск приложения через production WSGI-сервер
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]