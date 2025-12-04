# Security Guidelines

## 🔒 Overview

This document outlines security best practices for the CRM Territory & Segmentation Engine project.

## 🚨 Critical Security Concerns

### 1. Secret Key Management

**NEVER commit secrets to version control!**

#### Airflow Secret Key
The `secret_key` in `airflow.cfg` is used for:
- Flask session management
- CSRF token generation
- Request authorization to Celery workers

**Current Status:**
- ✅ `airflow.cfg` is in `.gitignore`
- ✅ `.env` is in `.gitignore`
- ✅ `.env.example` template provided

#### How to Secure Your Installation

1. **Generate New Secrets**
   ```bash
   cd crm-territory-engine
   python scripts/generate_secrets.py
   ```

2. **Create Your .env File**
   ```bash
   cp .env.example .env
   # Edit .env and add your generated secrets
   ```

3. **Set Environment Variables**
   
   Airflow reads configuration from environment variables with the format:
   ```
   AIRFLOW__SECTION__KEY=value
   ```

   For example:
   ```bash
   export AIRFLOW__WEBSERVER__SECRET_KEY="your-secret-key-here"
   export AIRFLOW__CORE__FERNET_KEY="your-fernet-key-here"
   ```

4. **Load Environment Variables**
   
   Add to your shell startup file (`~/.zshrc` or `~/.bashrc`):
   ```bash
   # Load Airflow environment variables
   if [ -f ~/path/to/crm-territory-engine/.env ]; then
       export $(cat ~/path/to/crm-territory-engine/.env | grep -v '^#' | xargs)
   fi
   ```

   Or use `python-dotenv` in your Python scripts:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

### 2. Fernet Key for Connection Encryption

Airflow uses Fernet encryption to store connection passwords in the database.

**Generate a Fernet Key:**
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

**Set in Environment:**
```bash
export AIRFLOW__CORE__FERNET_KEY="your-fernet-key-here"
```

**⚠️ Important:** If you change the Fernet key, existing encrypted connections will become unreadable!

### 3. Database Security

#### Development (SQLite)
- SQLite database (`airflow.db`) is in `.gitignore`
- Suitable for local development only
- No network access required

#### Production (PostgreSQL/MySQL)
- Use a dedicated database server
- Store credentials in environment variables
- Use SSL/TLS for database connections
- Restrict network access with firewall rules

**Example PostgreSQL Connection:**
```bash
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="postgresql+psycopg2://user:password@localhost:5432/airflow"
```

### 4. SMTP Credentials

If using email notifications, store SMTP credentials securely:

```bash
export AIRFLOW__SMTP__SMTP_USER="your-email@example.com"
export AIRFLOW__SMTP__SMTP_PASSWORD="your-app-password"
```

**Best Practice:** Use app-specific passwords, not your main email password.

## 🔐 Secret Rotation

### When to Rotate Secrets

- **Immediately** if a secret is compromised or exposed
- **Regularly** as part of security maintenance (quarterly recommended)
- **Before** moving to production
- **After** team member departures

### How to Rotate Secrets

1. Generate new secrets using `scripts/generate_secrets.py`
2. Update `.env` file with new values
3. Restart all Airflow components:
   ```bash
   # Stop all Airflow processes
   pkill -f airflow
   
   # Restart with new secrets
   airflow webserver &
   airflow scheduler &
   ```
4. Update any external systems that use these secrets

## 🛡️ Additional Security Best Practices

### File Permissions

Ensure sensitive files have restricted permissions:
```bash
chmod 600 .env
chmod 600 airflow/airflow.cfg
chmod 700 airflow/
```

### Git Security

**Before committing:**
```bash
# Check for secrets in staged files
git diff --cached | grep -i "secret\|password\|key"

# Use git-secrets to prevent committing secrets
git secrets --scan
```

**If you accidentally commit a secret:**
1. Rotate the compromised secret immediately
2. Remove from git history:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch path/to/file" \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. Force push (⚠️ coordinate with team)

### Production Deployment

For production environments:

1. **Use a Secrets Manager**
   - AWS Secrets Manager
   - HashiCorp Vault
   - Azure Key Vault
   - Google Cloud Secret Manager

2. **Enable Airflow Secrets Backend**
   ```python
   # In airflow.cfg or environment
   AIRFLOW__SECRETS__BACKEND=airflow.providers.amazon.aws.secrets.systems_manager.SystemsManagerParameterStoreBackend
   ```

3. **Implement Access Controls**
   - Use IAM roles/policies
   - Principle of least privilege
   - Audit access logs

4. **Network Security**
   - Use VPC/private networks
   - Enable SSL/TLS for all connections
   - Implement firewall rules
   - Use reverse proxy (nginx/Apache)

### Monitoring & Auditing

- Enable Airflow audit logs
- Monitor for unauthorized access attempts
- Set up alerts for security events
- Regular security audits

## 📚 Resources

- [Airflow Security Documentation](https://airflow.apache.org/docs/apache-airflow/stable/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Cryptography Documentation](https://cryptography.io/)

## 🚨 Reporting Security Issues

If you discover a security vulnerability, please:
1. **DO NOT** create a public GitHub issue
2. Contact the project maintainer directly
3. Provide detailed information about the vulnerability
4. Allow time for the issue to be addressed before public disclosure

---

**Remember:** Security is everyone's responsibility. When in doubt, ask!

