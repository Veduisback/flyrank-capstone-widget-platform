from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FlyRank Widget Platform"
    database_url: str
    jwt_secret: str
    jwt_expire_minutes: int = 60
    cors_origins: str = "http://localhost:5500"

    geo_provider_a_enabled: bool = True
    geo_provider_b_enabled: bool = True
    notification_enabled: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


settings = Settings()