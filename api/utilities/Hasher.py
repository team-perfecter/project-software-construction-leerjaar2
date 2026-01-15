import hashlib
from argon2 import PasswordHasher


def hash_string(string: str, use_argon2: bool) -> str:
    """
    Hashes a string with either MD5 or argon2
    Args:
        string (str): The string that needs to be hashed
        use_argon2 (bool): Whether argon2 or MD5 needs to be used

    Returns:
        str: The hashed string
    """

    if use_argon2:
        argon2_hasher = PasswordHasher()
        return argon2_hasher.hash(string)
    else:
        return hashlib.md5(string.encode()).hexdigest()
