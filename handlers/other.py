from aiogram import Router
from aiogram.types import Message


# создаём роутер для дальнешей привязки к нему обработчиков
router = Router()


@router.message()
async def message_handler(msg: Message):
    await msg.answer(f"Неизвестная команда")
