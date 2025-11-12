from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Klasa do wczytywania ustawień z pliku .env
    Automatycznie mapuje zmienne z .env na atrybuty tej klasy.
    """


    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

    # Zmienne, które muszą być w .env
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_HOURS: int


# globalna instancję ustawień
settings = Settings()