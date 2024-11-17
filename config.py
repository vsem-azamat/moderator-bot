from decouple import config


class Config:
    BOT_TOKEN: str = config("BOT_TOKEN", cast=str)
    SUPER_ADMINS: list[int] = [int(id_admin) for id_admin in config("ADMINS", cast=str).split(",")]

    # DATABASE
    DB_USER: str = config("DB_USER", cast=str)
    DB_PASSWORD: str = config("DB_PASSWORD", cast=str)
    DB_NAME: str = config("DB_NAME", cast=str)

    # DATABASE URL
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@db/{self.DB_NAME}"

cnfg = Config()
