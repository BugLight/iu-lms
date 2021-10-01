import hashlib
import random

from sessions.settings import settings


def hash_password(password: str, salt: str = settings.PASSWORD_SALT) -> bytes:
    return hashlib.sha256((salt + password).encode("utf-8"), usedforsecurity=True).digest()


def generate_password(length: int = settings.PASSWORD_DEFAULT_LENGTH) -> str:
    return "".join(random.sample("abcdefghijklmnopqrstuvwxyz01234567890", length))
