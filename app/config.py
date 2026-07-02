from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    bot_token: str
    admin_ids: str = ""

    db_user: str
    db_pass: str
    db_name: str
    db_host: str = "db"
    db_port: int = 5432

    redis_host: str = "redis"
    redis_port: int = 6379

    files_dir: str = "/app/files"

    card_number: str = ""
    card_holder: str = ""
    support_username: str = ""

    click_service_id: str = ""
    click_merchant_id: str = ""
    click_secret_key: str = ""

    web_host: str = "0.0.0.0"
    web_port: int = 8000
    public_url: str = ""

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_pass}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def admin_id_list(self) -> list[int]:
        return [int(x) for x in self.admin_ids.split(",") if x.strip()]


settings = Settings()
