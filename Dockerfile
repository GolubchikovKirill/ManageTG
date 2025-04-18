FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-dev \
    build-essential \
    postgresql-client


RUN python3 -m venv /env
ENV PATH="/env/bin:$PATH"

WORKDIR /app


COPY requirements.txt .


RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


COPY . .


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]