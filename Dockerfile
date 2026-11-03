FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8000

HEALTHCHECK --interval=5s --timeout=3s --start-period=10s --retries=5 \
    CMD python -c "import json, urllib.request; assert json.load(urllib.request.urlopen('http://127.0.0.1:8000/ping', timeout=2)) is True"

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
