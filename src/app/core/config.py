import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field

class Settings(BaseSettings):
    
    # Variables generales
    ENV_STATE: str = os.getenv("LICIT_ENV", "dev").lower()
    APP_NAME: str = "Licit API"
    DEBUG: bool = False
    API_V1_STR: str


    # Variables de DB (se llenarán desde los archivos .env)
    DB_USER: str
    DB_PASS: str
    DB_PORT: int
    DB_NAME: str
    DB_HOST: str = "localhost"

    # Secret Key para JWT
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+asyncmy://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(
        # Orden de prioridad: .env.dev sobrescribe a .env.base
        # Las variables de entono reales sobrescriben a ambos
        env_file = (".env", f".env.{ENV_STATE}"),
        extra = "ignore"
    )

settings = Settings()
