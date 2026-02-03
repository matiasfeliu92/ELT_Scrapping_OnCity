FROM apache/airflow:2.8.1

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY dags/ /opt/airflow/dags/

ENV PYTHONPATH=${PYTHONPATH}:/opt/airflow/src

USER root

RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libxkbcommon0 \
    libxdamage1 \
    libgbm1 \
    libasound2 \
    libxshmfence1 \
    libgtk-3-0 \
    && apt-get clean

USER airflow