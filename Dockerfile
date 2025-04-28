FROM python:3.11-slim

# Установка зависимостей для компиляции
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    libffi-dev \
    postgresql-client \
    curl \
    libssl-dev \
    pkg-config \
    git \
    && apt-get clean

# Установка Rust и Cargo (если нужны для jiter)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Добавление пути для cargo
ENV PATH="/root/.cargo/bin:${PATH}"

# Установка uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Установка pip и uv
RUN pip install --upgrade pip && pip install uv

# Установка рабочей директории
WORKDIR /app

# Копирование pyproject.toml и uv.lock
COPY pyproject.toml uv.lock /app/

# Установка зависимостей через pip в активное окружение
RUN uv sync

# Установка uvicorn и alembic через pip
RUN pip install uvicorn alembic

# Добавление скрипта entrypoint
COPY scripts/entrypoint.sh /app/scripts/entrypoint.sh
RUN chmod +x /app/scripts/entrypoint.sh

# Копирование остальной части проекта
COPY . .

# Порт
EXPOSE 8000

# Точка входа
ENTRYPOINT ["/app/scripts/entrypoint.sh"]