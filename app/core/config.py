from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "FriendlyEats FastAPI"
    ENVIRONMENT: str = "local"
    FIREBASE_PROJECT_ID: str = "demo-friendlyeats"
    FIREBASE_CREDENTIALS_PATH: str | None = None
    FIRESTORE_EMULATOR_HOST: str | None = None


settings = Settings()
