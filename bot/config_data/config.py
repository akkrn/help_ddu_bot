from dataclasses import dataclass
from environs import Env


@dataclass
class DatabaseConfig:
    DATABASE: str
    DB_HOST: str
    DB_USER: str
    DB_password: str


@dataclass
class TgBot:
    BOT_TOKEN: str


@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig


def load_config(path: str | None) -> Config:
    env: Env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(token=env("BOT_TOKEN")),
        db=DatabaseConfig(
            database=env("DATABASE"),
            db_host=env("DB_HOST"),
            db_user=env("DB_USER"),
            db_password=env("DB_PASSWORD"),
        ),
    )
