FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    wget gnupg \
    && rm -rf /var/lib/apt/lists/*

RUN pip install browser-use-sdk playwright supabase
RUN playwright install chromium
RUN playwright install-deps

WORKDIR /app
COPY cron_job_v2.py .
COPY accounts_v2.py .

CMD ["python", "-u", "cron_job_v2.py"]