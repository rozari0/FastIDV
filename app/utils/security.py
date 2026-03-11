import string
from random import random

from pwdlib import PasswordHash

pwd_context = PasswordHash.recommended()


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def generate_secret(length: int = 32) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))
