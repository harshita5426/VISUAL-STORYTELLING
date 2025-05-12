# utils/password.py

import bcrypt

def hash_password(password: str) -> str:
    """Hash the password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(input_password: str, stored_password: str) -> bool:
    """Verify the password against the stored hashed password"""
    return bcrypt.checkpw(input_password.encode('utf-8'), stored_password.encode('utf-8'))
