from pydantic_settings import SettingsConfigDict, BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
    POSTGRES_HOST: str = Field(..., json_schema_extra={"env": "POSTGRES_HOST"})
    POSTGRES_PORT: int = Field(..., json_schema_extra={"env": "POSTGRES_PORT"})
    POSTGRES_DB: str = Field(..., json_schema_extra={"env": "POSTGRES_DB"})
    POSTGRES_USER: str = Field(..., json_schema_extra={"env": "POSTGRES_USER"})
    POSTGRES_PASSWORD: str = Field(..., json_schema_extra={"env": "POSTGRES_PASSWORD"})

    JWT_SECRET: Optional[str] = Field(None, json_schema_extra={"env": "JWT_SECRET"})

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
