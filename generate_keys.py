#!/usr/bin/env python3
"""
Script to generate secure keys for SecureBridge configuration.
Run this to generate SECRET_KEY and API_KEY_ENCRYPTION_KEY.
"""
import secrets
from cryptography.fernet import Fernet

def generate_secret_key(length: int = 32) -> str:
    """Generate a secure random secret key."""
    return secrets.token_hex(length)

def generate_encryption_key() -> str:
    """Generate a Fernet encryption key."""
    return Fernet.generate_key().decode()

if __name__ == "__main__":
    print("=" * 60)
    print("SecureBridge - Security Keys Generator")
    print("=" * 60)
    print("\nGenerating secure keys for your .env file...\n")
    
    secret_key = generate_secret_key()
    encryption_key = generate_encryption_key()
    
    print(f"SECRET_KEY={secret_key}")
    print(f"API_KEY_ENCRYPTION_KEY={encryption_key}")
    
    print("\n" + "=" * 60)
    print("⚠️  IMPORTANT: Copy these keys to your .env file")
    print("⚠️  Keep these keys secret and never commit them to git!")
    print("=" * 60)
