from passlib.context import CryptContext
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def normalize_password(password: str) -> str:
    # Convert to SHA256 (fixed length, safe for bcrypt)
    return hashlib.sha256(password.encode()).hexdigest()


def hash_password(password: str):
    normalized = normalize_password(password)
    return pwd_context.hash(normalized)


def verify_password(plain, hashed):
    normalized = normalize_password(plain)
    return pwd_context.verify(normalized, hashed)