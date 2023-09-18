from dataclasses import dataclass

from environs import Env


@dataclass
class OpenAIConfig:
    api_key: str
    url: str


@dataclass
class DatabaseConfig:
    database: str
    db_host: str
    db_user: str
    db_password: str
    db_port: int


@dataclass
class TgBot:
    token: str


@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig
    openai: OpenAIConfig


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
            db_port=env.int("DB_PORT"),
        ),
        openai=OpenAIConfig(
            api_key=env("OPENAI_API_KEY"), url=env("OPENAI_API_URL")
        ),
    )
