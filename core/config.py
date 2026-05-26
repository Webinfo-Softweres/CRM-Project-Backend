from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    PROJECT_NAME: str = "CRM Backend"

    DEBUG: bool = False

    DATABASE_URL: str

    SECRET_KEY: str

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    BIOMETRIC_DEVICE_IP: str

    BIOMETRIC_DEVICE_PORT: int = 4370



    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


@lru_cache()
def get_settings():

    return Settings()


settings = get_settings()
