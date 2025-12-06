# Security Guidelines

## 🔒 Secrets Management

This project uses environment variables to manage sensitive configuration values. **Never commit secrets to version control.**

## Setup Instructions

### 1. Create Environment File

Copy the example environment file and fill in your actual values:

```bash
cp .env.example .env
```

### 2. Generate Secret Keys

#### Airflow Webserver Secret Key
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Airflow Fernet Key (for encrypting connection passwords)
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 3. Update .env File

Add the generated keys to your `.env` file:

```bash
AIRFLOW__WEBSERVER__SECRET_KEY=<your-generated-secret-key>
AIRFLOW__CORE__FERNET_KEY=<your-generated-fernet-key>
```

### 4. Load Environment Variables

Before starting Airflow, load the environment variables:

```bash
# Option 1: Source the .env file (bash/zsh)
export $(cat .env | xargs)

# Option 2: Use direnv (recommended for automatic loading)
# Install direnv: brew install direnv
# Add to your shell: eval "$(direnv hook bash)"  # or zsh
# Then: direnv allow .

# Option 3: Load in Python scripts
# Use python-dotenv package
pip install python-dotenv
```

## 🚨 Security Checklist

- [ ] `.env` file is in `.gitignore`
- [ ] `airflow.cfg` is in `.gitignore` (contains local paths)
- [ ] All secrets use environment variables
- [ ] Secret keys are randomly generated (not defaults)
- [ ] `.env.example` contains no actual secrets
- [ ] Production uses a proper secrets backend (AWS Secrets Manager, HashiCorp Vault, etc.)

## 🔐 Airflow Configuration Security

### Environment Variables Override

Airflow supports environment variable overrides using the pattern:
```
AIRFLOW__SECTION__KEY=value
```

For example:
- `AIRFLOW__WEBSERVER__SECRET_KEY` overrides `[webserver] secret_key`
- `AIRFLOW__CORE__FERNET_KEY` overrides `[core] fernet_key`

### Secrets Backend (Production)

For production deployments, use Airflow's secrets backend feature:

```python
# In airflow.cfg or via environment variables
[secrets]
backend = airflow.providers.amazon.aws.secrets.systems_manager.SystemsManagerParameterStoreBackend
backend_kwargs = {"connections_prefix": "/airflow/connections", "variables_prefix": "/airflow/variables"}
```

Supported backends:
- AWS Systems Manager Parameter Store
- AWS Secrets Manager
- Google Cloud Secret Manager
- HashiCorp Vault
- Azure Key Vault

## 📝 What NOT to Commit

Never commit these files or values:
- `.env` - Contains actual secrets
- `airflow.cfg` - Contains local paths and potentially secrets
- `airflow.db` - Contains encrypted connection data
- `webserver_config.py` - May contain authentication configs
- Any file with API keys, passwords, or tokens

## 🔄 Rotating Secrets

If a secret is compromised:

1. **Generate new secret key**:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Update `.env` file** with new key

3. **Restart Airflow services**:
   ```bash
   # Stop all Airflow processes
   pkill -f airflow
   
   # Restart webserver and scheduler
   airflow webserver -D
   airflow scheduler -D
   ```

4. **Invalidate all sessions** (users will need to log in again)

## 🏢 Production Best Practices

1. **Use a secrets backend** (AWS Secrets Manager, Vault, etc.)
2. **Enable SSL/TLS** for webserver
3. **Use PostgreSQL or MySQL** instead of SQLite
4. **Enable authentication** (OAuth, LDAP, etc.)
5. **Restrict network access** (firewall, VPC)
6. **Regular security audits** and dependency updates
7. **Implement least privilege** access controls
8. **Enable audit logging**
9. **Use encrypted connections** to databases
10. **Rotate secrets regularly** (quarterly or after personnel changes)

## 📚 Additional Resources

- [Airflow Security Documentation](https://airflow.apache.org/docs/apache-airflow/stable/security/)
- [Airflow Secrets Backend](https://airflow.apache.org/docs/apache-airflow/stable/security/secrets/secrets-backend/)
- [OWASP Security Guidelines](https://owasp.org/www-project-top-ten/)

## 🆘 Security Incident Response

If you suspect a security breach:

1. **Immediately rotate all secrets**
2. **Check Airflow logs** for suspicious activity
3. **Review database audit logs**
4. **Notify team members**
5. **Document the incident**
6. **Update security measures** to prevent recurrence
