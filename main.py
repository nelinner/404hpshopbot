# main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from database import init_db
from handlers import router

logging.basicConfig(level=logging.INFO)

bot = Bot(token="8254209430:AAEGZGjdnzSXFUudGjF9MOydkU7s8QyDR28", parse_mode="HTML")

async def main():
    await init_db()
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    # Передаём бота в обработчики
    router.bot = bot
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())