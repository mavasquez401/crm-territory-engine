#!/bin/bash

# Script to generate and setup Airflow secrets
# Usage: ./scripts/setup_secrets.sh

set -e

echo "🔐 Airflow Secrets Setup Script"
echo "================================"
echo ""

# Check if .env already exists
if [ -f ".env" ]; then
    echo "⚠️  Warning: .env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting without changes."
        exit 0
    fi
fi

# Generate Airflow Webserver Secret Key
echo "Generating Airflow Webserver Secret Key..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Generate Fernet Key
echo "Generating Airflow Fernet Key..."
FERNET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

# Create .env file
cat > .env << EOF
# Airflow Environment Variables
# Generated on $(date)
# DO NOT COMMIT THIS FILE TO VERSION CONTROL

# Airflow Webserver Secret Key
# Used for Flask session management and CSRF protection
AIRFLOW__WEBSERVER__SECRET_KEY=${SECRET_KEY}

# Airflow Fernet Key
# Used for encrypting connection passwords in the database
AIRFLOW__CORE__FERNET_KEY=${FERNET_KEY}

# Database Connection (SQLite for development)
# For production, use PostgreSQL or MySQL
# AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://user:password@localhost:5432/airflow

# SMTP Configuration (optional - for email notifications)
# AIRFLOW__SMTP__SMTP_USER=your-smtp-user
# AIRFLOW__SMTP__SMTP_PASSWORD=your-smtp-password
# AIRFLOW__SMTP__SMTP_HOST=smtp.gmail.com
# AIRFLOW__SMTP__SMTP_PORT=587
# AIRFLOW__SMTP__SMTP_MAIL_FROM=airflow@example.com
EOF

echo ""
echo "✅ Secrets generated successfully!"
echo ""
echo "📝 Your .env file has been created with the following keys:"
echo "   - AIRFLOW__WEBSERVER__SECRET_KEY"
echo "   - AIRFLOW__CORE__FERNET_KEY"
echo ""
echo "🔒 Security Reminders:"
echo "   1. The .env file is already in .gitignore"
echo "   2. NEVER commit the .env file to version control"
echo "   3. Keep these keys secure and rotate them periodically"
echo ""
echo "🚀 Next Steps:"
echo "   1. Load environment variables: export \$(cat .env | xargs)"
echo "   2. Start Airflow: cd airflow && airflow webserver & airflow scheduler"
echo ""
echo "💡 Tip: Use 'direnv' for automatic environment variable loading"
echo "   Install: brew install direnv"
echo "   Setup: echo 'eval \"\$(direnv hook bash)\"' >> ~/.bashrc"
echo "   Allow: direnv allow ."
echo ""

