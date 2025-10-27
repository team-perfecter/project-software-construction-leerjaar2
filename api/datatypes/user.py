from dataclasses import dataclass
from datetime import date

@dataclass
class User:
    id: int
    username: str
    password: str
    name: str
    email: str
    phone: str
    birth_year: date