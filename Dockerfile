FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3000

CMD ["gunicorn", "main:app", "--workers", "2", "--worker-class", "gthread", "--threads", "4", "--bind", "0.0.0.0:3000"]
