FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    AGENDAHS_DB=/app/data/eventos.db

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data
VOLUME ["/app/data"]

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "wsgi:app"]
