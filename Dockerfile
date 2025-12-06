# =====================================================
# Airflow ETL Pipeline Dockerfile
# =====================================================

FROM apache/airflow:2.7.3-python3.11

# Switch to root for system packages
USER root

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Switch back to airflow user
USER airflow

# Copy requirements and install Python dependencies
COPY requirements.txt /opt/airflow/requirements.txt
RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt

# Copy application code
COPY --chown=airflow:root . /opt/airflow

# Set environment variables
ENV AIRFLOW_HOME=/opt/airflow/airflow
ENV PYTHONPATH=/opt/airflow:$PYTHONPATH

# Expose Airflow webserver port
EXPOSE 8080

# Initialize database and create admin user on first run
# Then start webserver and scheduler
CMD airflow db init && \
    airflow users create \
        --username admin \
        --firstname Admin \
        --lastname User \
        --role Admin \
        --email admin@example.com \
        --password admin || true && \
    airflow webserver & \
    airflow scheduler
