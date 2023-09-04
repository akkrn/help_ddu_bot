import asyncio
import logging

from aiogram import Bot, Dispatcher
from bot.config_data.config import Config, load_config
from bot.fsm import storage
from bot.handlers import user_handlers, fsm_handlers, other_handlers

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s "
        "[%(asctime)s] - %(name)s - %(message)s",
    )

    logger.info("Starting bot")
    config = load_config()
    bot = Bot(token=config.tg_bot.BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher(storage=storage)

    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)
    dp.include_router(fsm_handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
