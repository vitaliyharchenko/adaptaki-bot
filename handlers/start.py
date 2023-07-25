from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from filters.user_type import UserTypeFilter


# создаём роутер для дальнешей привязки к нему обработчиков
router = Router()


@router.message(Command("start"), UserTypeFilter(user_types=['reg', 'admin']))
async def start_handler(msg: Message):
    await msg.answer(f"С возвращением!")


@router.message(Command("start"), UserTypeFilter(user_types=['anon']))
async def start_handler(msg: Message):
    await msg.answer(f"Привет! Я бот с задачами ЕГЭ. Давай знакомиться!\n\nЧтобы воспользоваться мной, нужно пройти простую регистрацию. Для этого нажми /reg")
