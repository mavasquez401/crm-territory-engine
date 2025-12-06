# Deployment Guide

## Docker Compose Deployment

This guide covers deploying the entire CRM Territory & Segmentation Engine using Docker Compose.

---

## Prerequisites

- Docker Desktop installed (includes Docker Compose)
- 4GB+ RAM available
- Ports 3000, 8000, and 8080 available

---

## Quick Start

### 1. Set Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example
cp .env.example .env

# Generate secrets
python3 scripts/generate_secrets.py

# Edit .env and add the generated keys
```

Your `.env` should include:

```bash
# Airflow secrets
AIRFLOW__WEBSERVER__SECRET_KEY=your_generated_key
AIRFLOW__CORE__FERNET_KEY=your_generated_fernet_key

# Optional: Snowflake (if using)
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password

# Optional: AWS S3 (if using)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
S3_BUCKET_NAME=institutional-clients-raw
```

### 2. Build All Services

```bash
docker-compose build
```

This builds:
- **Airflow** (ETL pipeline)
- **API** (FastAPI backend)
- **Frontend** (React dashboard)

### 3. Start All Services

```bash
docker-compose up -d
```

Services will start in order:
1. Airflow (depends on nothing)
2. API (depends on Airflow for data)
3. Frontend (depends on API)

### 4. Access Services

Once all services are healthy:

- **Frontend Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Airflow UI**: http://localhost:8080
  - Username: `admin`
  - Password: `admin`

---

## Service Details

### Port Mappings

| Service | Internal Port | External Port | URL |
|---------|--------------|---------------|-----|
| Frontend | 80 | 3000 | http://localhost:3000 |
| API | 8000 | 8000 | http://localhost:8000 |
| Airflow | 8080 | 8080 | http://localhost:8080 |

### Volume Mounts

- `./data` → Shared data directory (read-only for API)
- `./airflow/dags` → Airflow DAG definitions
- `./airflow/logs` → Airflow execution logs
- `./python_etl` → ETL Python modules

---

## Docker Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f airflow
```

### Check Service Status

```bash
docker-compose ps
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart api
```

### Stop Services

```bash
# Stop all (keeps containers)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove everything (including volumes)
docker-compose down -v
```

### Rebuild After Code Changes

```bash
# Rebuild specific service
docker-compose build api
docker-compose up -d api

# Rebuild all services
docker-compose build
docker-compose up -d
```

---

## Troubleshooting

### Services Won't Start

**Check logs:**
```bash
docker-compose logs
```

**Common issues:**
- Port conflicts: Check if ports 3000, 8000, 8080 are available
- Missing `.env` file: Create from `.env.example`
- Insufficient memory: Increase Docker Desktop memory allocation

### API Can't Access Data

**Check volume mounts:**
```bash
docker-compose exec api ls -la /app/data
```

**Solution:**
- Ensure `data/core/` directory exists
- Run Airflow DAG to generate data files

### Frontend Can't Connect to API

**Check API health:**
```bash
curl http://localhost:8000/api/health
```

**Check nginx proxy:**
```bash
docker-compose logs frontend
```

**Solution:**
- Verify API service is running
- Check nginx.conf proxy configuration

### Airflow DAG Not Appearing

**Check DAG directory:**
```bash
docker-compose exec airflow ls -la /opt/airflow/airflow/dags
```

**Solution:**
- Verify DAG files are in `airflow/dags/`
- Check DAG syntax errors in logs
- Restart Airflow: `docker-compose restart airflow`

---

## Production Considerations

### Security

1. **Change default passwords:**
   - Airflow admin password
   - Generate strong secrets

2. **Use secrets management:**
   - Docker secrets
   - AWS Secrets Manager
   - HashiCorp Vault

3. **Enable HTTPS:**
   - Add SSL certificates
   - Configure nginx with SSL
   - Use reverse proxy (e.g., Traefik, nginx)

### Scalability

1. **Use external database:**
   - Replace SQLite with PostgreSQL
   - Configure in docker-compose.yml

2. **Add Redis for caching:**
   - Cache API responses
   - Airflow Celery executor

3. **Horizontal scaling:**
   - Multiple API instances behind load balancer
   - Kubernetes for orchestration

### Monitoring

1. **Add logging aggregation:**
   - ELK stack (Elasticsearch, Logstash, Kibana)
   - Grafana + Loki

2. **Add metrics:**
   - Prometheus
   - Grafana dashboards

3. **Add alerting:**
   - PagerDuty
   - Slack notifications

---

## Kubernetes Deployment (Optional)

For production Kubernetes deployment, see manifests in `k8s/` directory:

```bash
# Apply all manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n crm-territory

# Access services
kubectl port-forward svc/frontend 3000:80
kubectl port-forward svc/api 8000:8000
kubectl port-forward svc/airflow 8080:8080
```

---

## Environment Variables Reference

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `AIRFLOW__WEBSERVER__SECRET_KEY` | Airflow session key | Generated by script |
| `AIRFLOW__CORE__FERNET_KEY` | Airflow encryption key | Generated by script |

### Optional (Snowflake)

| Variable | Description | Example |
|----------|-------------|---------|
| `SNOWFLAKE_ACCOUNT` | Snowflake account ID | `abc12345` |
| `SNOWFLAKE_USER` | Snowflake username | `user@example.com` |
| `SNOWFLAKE_PASSWORD` | Snowflake password | `secure_password` |
| `SNOWFLAKE_WAREHOUSE` | Warehouse name | `COMPUTE_WH` |
| `SNOWFLAKE_ROLE` | Role name | `DATA_ENGINEER` |

### Optional (AWS S3)

| Variable | Description | Example |
|----------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | AWS access key | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `AWS_REGION` | AWS region | `us-east-1` |
| `S3_BUCKET_NAME` | S3 bucket name | `institutional-clients-raw` |

---

## Data Initialization

### First-Time Setup

1. **Start services:**
   ```bash
   docker-compose up -d
   ```

2. **Wait for Airflow to initialize:**
   ```bash
   docker-compose logs -f airflow
   # Wait for "Webserver started" message
   ```

3. **Trigger ETL DAG:**
   - Open http://localhost:8080
   - Login (admin/admin)
   - Find `crm_client_ingestion_dag`
   - Click "Trigger DAG"

4. **Verify data:**
   - Check `data/core/` for generated CSV files
   - Access API: http://localhost:8000/api/stats
   - View dashboard: http://localhost:3000

---

## Backup and Restore

### Backup Data

```bash
# Backup data directory
tar -czf crm-data-backup-$(date +%Y%m%d).tar.gz data/

# Backup Airflow database
docker-compose exec airflow sqlite3 /opt/airflow/airflow/airflow.db ".backup '/opt/airflow/airflow/airflow-backup.db'"
```

### Restore Data

```bash
# Restore data directory
tar -xzf crm-data-backup-YYYYMMDD.tar.gz

# Restart services
docker-compose restart
```

---

## Performance Tuning

### Airflow

- Increase worker concurrency in `airflow.cfg`
- Use PostgreSQL instead of SQLite
- Enable parallelism for DAG tasks

### API

- Add Redis caching layer
- Increase uvicorn workers
- Use gunicorn for production

### Frontend

- Enable nginx caching
- Use CDN for static assets
- Implement service worker for offline support

---

## Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Verify health: `docker-compose ps`
3. Review documentation in `README.md`

---

**Status**: Production-ready with Docker Compose
**Last Updated**: December 2025
