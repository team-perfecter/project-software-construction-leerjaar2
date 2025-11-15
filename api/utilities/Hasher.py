from argon2 import PasswordHasher
import hashlib
# A function that hashes a string. use this instead of hashing inside a function somewhere else, so the hashing method can be changed when needed.
def hash_string(string: str) -> str:

    # For now passwords are stored in MD5 so there is no point in hashing with argon2.
    #argon2_hasher = PasswordHasher()
    #argon2_hashed_string = argon2_hasher.hash(string)

    MD5_hashed_string = hashlib.md5(string.encode()).hexdigest()
    return MD5_hashed_string