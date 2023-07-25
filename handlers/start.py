from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command


# создаём роутер для дальнешей привязки к нему обработчиков
router = Router()


@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer("Привет! Я бот с задачами ЕГЭ. Давай знакомиться! /n/n Чтобы воспользоваться мной, нужно пройти простую регистрацию. Для этого нажми /reg")
