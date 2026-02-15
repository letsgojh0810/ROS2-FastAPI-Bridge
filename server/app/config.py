from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://robot:robot1234@localhost:5432/robot_monitoring"
    CORS_ORIGINS: list[str] = ["*"]

    model_config = {"env_file": ".env"}


settings = Settings()
