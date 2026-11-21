# Stage 1: build dependencies
FROM python:3.12-slim AS build
WORKDIR /app
COPY requirements.txt .
COPY wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels --prefix=/install -r requirements.txt

# Stage 2: minimal runtime
FROM python:3.12-slim
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/* \
    && useradd -r -u 10001 appuser
COPY --from=build /install /usr/local
WORKDIR /app
COPY app.py .
ARG APP_VERSION=1.0.0
ARG BROKEN=false
ENV APP_VERSION=$APP_VERSION BROKEN=$BROKEN PYTHONUNBUFFERED=1
USER appuser
EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"
CMD ["gunicorn", "-b", "0.0.0.0:8080", "-w", "2", "app:app"]