# 🔐 Quick Security Reference Card

## 🚨 The Problem
Your `airflow.cfg` file contained a hardcoded secret key that should never be in version control.

## ✅ The Solution
Secrets are now managed via environment variables using a `.env` file.

---

## 🚀 Quick Setup (Choose One Method)

### Method 1: Automated Python Script ⭐ RECOMMENDED
```bash
# Generate secrets
python3 scripts/generate_secrets.py

# Create .env from template
cp .env.example .env

# Edit .env and paste the generated keys
# Then load them:
export $(cat .env | grep -v '^#' | xargs)
```

### Method 2: Automated Bash Script
```bash
# One command to do everything
./scripts/setup_secrets.sh

# Load environment variables
export $(cat .env | xargs)
```

### Method 3: Manual (One-Liners)
```bash
# Generate and display keys
echo "AIRFLOW__WEBSERVER__SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
echo "AIRFLOW__CORE__FERNET_KEY=$(python3 -c 'import base64, secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())')"

# Add to .env file manually
```

---

## 📋 Before Starting Airflow (EVERY TIME)

```bash
# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Then start Airflow
cd airflow
export AIRFLOW_HOME=$(pwd)
airflow webserver --port 8080 &
airflow scheduler &
```

---

## 🔍 Verify Setup

```bash
# Check if environment variables are loaded
echo $AIRFLOW__WEBSERVER__SECRET_KEY
echo $AIRFLOW__CORE__FERNET_KEY

# Both should show your secret keys (not empty)
```

---

## ⚠️ Critical Rules

| ✅ DO | ❌ DON'T |
|-------|----------|
| Use `.env` for secrets | Commit `.env` to git |
| Load env vars before starting Airflow | Hardcode secrets in config files |
| Keep `.env` private | Share secrets in chat/email |
| Rotate secrets quarterly | Reuse secrets across environments |
| Use secrets backend in production | Use SQLite in production |

---

## 📁 Files You Should Know About

| File | Purpose | Commit to Git? |
|------|---------|----------------|
| `.env` | **Your actual secrets** | ❌ NO - gitignored |
| `.env.example` | Template with no secrets | ✅ YES |
| `airflow.cfg` | Airflow config (local paths) | ❌ NO - gitignored |
| `SECURITY.md` | Detailed security guide | ✅ YES |
| `scripts/generate_secrets.py` | Generate secure keys | ✅ YES |

---

## 🆘 Emergency: Secret Compromised

```bash
# 1. Generate new secrets immediately
python3 scripts/generate_secrets.py

# 2. Update .env with new keys
nano .env

# 3. Restart all Airflow services
pkill -f airflow
cd airflow && export AIRFLOW_HOME=$(pwd)
airflow webserver & airflow scheduler &

# 4. All users must log in again
```

---

## 🏢 Production Checklist

- [ ] Use PostgreSQL/MySQL (not SQLite)
- [ ] Enable SSL/TLS for webserver
- [ ] Use secrets backend (AWS/GCP/Vault)
- [ ] Enable authentication (OAuth/LDAP)
- [ ] Restrict network access
- [ ] Set up monitoring and alerts
- [ ] Regular security audits
- [ ] Rotate secrets quarterly

---

## 💡 Pro Tips

### Auto-load environment variables with direnv
```bash
# Install direnv
brew install direnv  # macOS
# or: apt install direnv  # Linux

# Add to shell config (~/.bashrc or ~/.zshrc)
eval "$(direnv hook bash)"  # or zsh

# Enable for this project
cd crm-territory-engine
direnv allow .

# Now .env loads automatically when you cd into the directory!
```

### Create a startup script
```bash
# Create start.sh
cat > start.sh << 'EOF'
#!/bin/bash
export $(cat .env | grep -v '^#' | xargs)
cd airflow
export AIRFLOW_HOME=$(pwd)
airflow webserver --port 8080 &
airflow scheduler &
echo "✅ Airflow started!"
EOF

chmod +x start.sh
./start.sh
```

---

## 📚 More Information

- **Detailed Guide**: See [SECURITY.md](SECURITY.md)
- **Setup Summary**: See [SECURITY_SETUP_SUMMARY.md](SECURITY_SETUP_SUMMARY.md)
- **Airflow Docs**: https://airflow.apache.org/docs/apache-airflow/stable/security/

---

## 🎯 TL;DR

1. **Run**: `python3 scripts/generate_secrets.py`
2. **Create**: `.env` file with the generated keys
3. **Load**: `export $(cat .env | grep -v '^#' | xargs)`
4. **Start**: Airflow as usual
5. **Never**: Commit `.env` or `airflow.cfg` to git

---

**Status**: ✅ Security issue resolved  
**Last Updated**: December 4, 2025

