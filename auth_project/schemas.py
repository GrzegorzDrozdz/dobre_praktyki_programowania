from pydantic import BaseModel, ConfigDict # POPRAWKA: Importujemy ConfigDict
from typing import List, Optional

# Schemat do logowania
class LoginData(BaseModel):
    username: str
    password: str

# Schemat tokena
class Token(BaseModel):
    access_token: str
    token_type: str

# Schemat danych wewnątrz tokena (payload)
class TokenData(BaseModel):
    sub: str
    roles: List[str] = []

# Schemat do tworzenia nowego użytkownika
class UserCreate(BaseModel):
    username: str
    password: str
    roles: List[str] = ["ROLE_USER"] # Domyślna rola

# Schemat do wyświetlania danych użytkownika
class UserDisplay(BaseModel):
    username: str
    roles: List[str]


    model_config = ConfigDict(from_attributes=True)