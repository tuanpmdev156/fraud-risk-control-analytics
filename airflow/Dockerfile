FROM apache/airflow:2.10.4-python3.11

# Switch to root for system-level dependencies
USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        g++ \
        libpq-dev \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Switch back to airflow user to install Python packages safely
USER airflow

# Copy Python dependencies file
COPY requirements.txt /requirements.txt

# Install dependencies with constraints to avoid accidental Airflow upgrades
RUN pip install --no-cache-dir \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.4/constraints-3.11.txt" \
    -r /requirements.txt

# Ensure project root is in PYTHONPATH for importing scripts
ENV PYTHONPATH="/opt/airflow"