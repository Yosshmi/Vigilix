from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Vigilix API"
    app_version: str = "0.1.0"
    environment: str = "development"
    api_prefix: str = "/api"
    cors_origins: list[str] = ["http://localhost:5173"]

    yolo_model: str = "yolo11n.pt"
    confidence_threshold: float = 0.35
    iou_threshold: float = 0.45
    inference_size: int = 640

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="VIGILIX_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
