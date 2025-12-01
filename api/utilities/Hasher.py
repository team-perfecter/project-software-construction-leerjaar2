from argon2 import PasswordHasher
import hashlib
# A function that hashes a string. use this instead of hashing inside a function somewhere else, so the hashing method can be changed when needed.
def hash_string(string: str) -> str:
# use argon 2 bool
    # For now passwords are stored in MD5 so there is no point in hashing with argon2.

    # if use_argon2:
    #     argon2_hasher = PasswordHasher()
    #     # return argon2_hasher.hash(string)
    #     return hashlib.md5(string.encode()).hexdigest()
    # else:
    return hashlib.md5(string.encode()).hexdigest()