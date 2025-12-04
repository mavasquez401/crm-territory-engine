#!/usr/bin/env python3
"""
Generate secure secrets for Airflow configuration.
This script generates cryptographically secure random keys for:
- Airflow Webserver Secret Key (Flask session management)
- Airflow Fernet Key (Connection password encryption)
"""

import secrets
import sys

try:
    from cryptography.fernet import Fernet
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False


def generate_webserver_secret():
    """
    Generate a secure random secret key for Flask webserver.
    Returns a URL-safe base64-encoded string.
    """
    return secrets.token_urlsafe(32)


def generate_fernet_key():
    """
    Generate a Fernet key for encrypting connection passwords.
    Returns a base64-encoded 32-byte key.
    """
    if HAS_CRYPTOGRAPHY:
        return Fernet.generate_key().decode()
    else:
        # Fallback: Generate a base64-encoded 32-byte key manually
        import base64
        key_bytes = secrets.token_bytes(32)
        return base64.urlsafe_b64encode(key_bytes).decode()


def main():
    """Main function to generate and display secrets."""
    print("=" * 70)
    print("🔐 Airflow Secrets Generator")
    print("=" * 70)
    print()
    
    # Check for cryptography package
    if not HAS_CRYPTOGRAPHY:
        print("⚠️  Warning: 'cryptography' package not found")
        print("   Using fallback method for Fernet key generation")
        print("   For production, install: pip install cryptography")
        print()
        print("-" * 70)
        print()
    
    # Generate secrets
    webserver_secret = generate_webserver_secret()
    fernet_key = generate_fernet_key()
    
    print("✅ Generated secure secrets for your Airflow installation:")
    print()
    print("-" * 70)
    print("AIRFLOW WEBSERVER SECRET KEY")
    print("-" * 70)
    print(f"AIRFLOW__WEBSERVER__SECRET_KEY={webserver_secret}")
    print()
    print("Purpose: Flask session management and CSRF protection")
    print("Usage: Add this to your .env file")
    print()
    
    print("-" * 70)
    print("AIRFLOW FERNET KEY")
    print("-" * 70)
    print(f"AIRFLOW__CORE__FERNET_KEY={fernet_key}")
    print()
    print("Purpose: Encrypting connection passwords in the database")
    print("Usage: Add this to your .env file")
    print()
    
    print("=" * 70)
    print("📝 NEXT STEPS:")
    print("=" * 70)
    print()
    print("1. Copy the generated keys above")
    print("2. Add them to your .env file:")
    print()
    print("   cp .env.example .env")
    print("   # Edit .env and paste the keys")
    print()
    print("3. Load environment variables before starting Airflow:")
    print()
    print("   export $(cat .env | grep -v '^#' | xargs)")
    print()
    print("4. Start Airflow services:")
    print()
    print("   cd airflow")
    print("   export AIRFLOW_HOME=$(pwd)")
    print("   airflow webserver & airflow scheduler")
    print()
    
    print("=" * 70)
    print("⚠️  SECURITY WARNINGS:")
    print("=" * 70)
    print()
    print("• NEVER commit .env or airflow.cfg to version control")
    print("• Keep these keys secure and confidential")
    print("• Rotate keys periodically (quarterly recommended)")
    print("• Use a secrets backend (AWS/GCP/Vault) in production")
    print("• See SECURITY.md for detailed security guidelines")
    print()
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
