from aiogram import Bot, Dispatcher
from config_data.config import load_config
from database import Database
from fsm_settings import storage

config = load_config(path=None)
bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
db = Database(
    name=config.db.database,
    user=config.db.db_user,
    password=config.db.db_password,
    host=config.db.db_host,
    port=config.db.db_port,
)
dp = Dispatcher(storage=storage)
