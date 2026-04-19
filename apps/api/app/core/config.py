from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "AI YouTube Strategist Dashboard API"
    app_version: str = "0.1.0"

    cors_allow_origins: str = "http://localhost:3000"

    youtube_api_key: str = ""
    youtube_api_base_url: str = "https://www.googleapis.com/youtube/v3"

    gemini_api_key: str = ""
    gemini_synthesis_model: str = "gemini-3-flash-preview"

    upload_dir: str = "uploads"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()