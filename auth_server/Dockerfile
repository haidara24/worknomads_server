FROM python:3.13.3-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc libpq-dev build-essential curl

WORKDIR /app

# COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY requirements.txt /app/

# Upgrade pip & retry logic
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir --default-timeout=100 --retries=10 -r requirements.txt

COPY . /app/

# RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

CMD ["python","manage.py","runserver","0.0.0.0:8000"]
