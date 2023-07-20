import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import config
from handlers import router


async def main():
    # инициализация бота с настройкой разметки сообщений (HTML, Markdown)
    # мы используем HTML, чтобы избежать проблем с экранированием символов
    bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)

    # хранилище данных для состояний пользователей
    # все данные бота, которые мы не сохраняем в БД (к примеру состояния), будут стёрты при перезапуске
    dp = Dispatcher(storage=MemoryStorage())

    # подключает к нашему диспетчеру все обработчики, которые используют router
    dp.include_router(router)

    # удаляем все обновления, которые произошли после последнего завершения работы бота
    # Это нужно, чтобы бот обрабатывал только те сообщения, которые пришли ему непосредственно во время его работы, а не за всё время
    await bot.delete_webhook(drop_pending_updates=True)

    # запускаем бота
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())