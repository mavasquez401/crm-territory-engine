#!/usr/bin/env python3
"""
Script to generate secure secrets for Airflow configuration.
Run this script to generate new secret keys for your .env file.
"""

import secrets
from cryptography.fernet import Fernet


def generate_airflow_secret_key():
    """
    Generate a secure secret key for Airflow webserver.
    This key is used for session management and CSRF protection.
    """
    return secrets.token_urlsafe(32)


def generate_fernet_key():
    """
    Generate a Fernet key for encrypting connection passwords in the database.
    This is used by Airflow to securely store sensitive connection information.
    """
    return Fernet.generate_key().decode()


def main():
    """
    Generate and display all required secrets for Airflow configuration.
    """
    print("=" * 70)
    print("Airflow Security Keys Generator")
    print("=" * 70)
    print()
    
    # Generate Airflow webserver secret key
    secret_key = generate_airflow_secret_key()
    print("🔐 Airflow Webserver Secret Key:")
    print(f"   AIRFLOW__WEBSERVER__SECRET_KEY={secret_key}")
    print()
    
    # Generate Fernet key for connection encryption
    fernet_key = generate_fernet_key()
    print("🔑 Fernet Key (for encrypting connection passwords):")
    print(f"   AIRFLOW__CORE__FERNET_KEY={fernet_key}")
    print()
    
    print("=" * 70)
    print("📝 Instructions:")
    print("=" * 70)
    print("1. Copy the keys above")
    print("2. Add them to your .env file (create from .env.example)")
    print("3. NEVER commit these keys to version control!")
    print("4. Restart Airflow webserver and scheduler after updating")
    print()
    print("⚠️  Security Notes:")
    print("   - Keep these keys secret and secure")
    print("   - Rotate keys periodically in production")
    print("   - Use different keys for dev/staging/production")
    print("   - If keys are compromised, generate new ones immediately")
    print("=" * 70)


if __name__ == "__main__":
    main()

