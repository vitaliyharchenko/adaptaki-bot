from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from db import database


# создаём роутер для дальнешей привязки к нему обработчиков
router = Router()


@router.message(Command("token"))
async def token_handler(msg: Message):
    user_data = database.get_user(user_id=msg.from_user.id)
    if user_data:
        token = user_data["token"]
        await msg.answer(f"Твой токен: {token}")
    else:
        await msg.answer(f"Твоего токена нет в базе данных")


@router.message(Command("profile"))
async def profilr_handler(msg: Message):
    user_data = database.get_user(user_id=msg.from_user.id)
    if user_data:
        await msg.answer(f"Твои данные: {user_data}")
    else:
        await msg.answer(f"Тебя нет в базе данных")


@router.message()
async def message_handler(msg: Message):
    await msg.answer(f"Неизвестная команда")
