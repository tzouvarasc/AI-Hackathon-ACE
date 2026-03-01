FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY shared /app/shared
COPY apps /app/apps

CMD ["uvicorn", "apps.family_api.app.main:app", "--host", "0.0.0.0", "--port", "8003"]
