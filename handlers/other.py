from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

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


@router.message(Command("exam_tree"))
async def profilr_handler(msg: Message):
    exam_tree = database.exam_tree
    if exam_tree:
        print(exam_tree)
        await msg.answer(f"Дерево экзаменов загружено!")
    else:
        await msg.answer(f"Дерево экзаменов не загружено!")


@router.message(Command("reset"))
async def reset_handler(msg: Message, state: FSMContext):
    state.clear()
    await msg.answer(f"Данные сброшены")


@router.message()
async def message_handler(msg: Message):
    await msg.answer(f"Неизвестная команда")


@router.callback_query()
async def callback_handler(callback: types.CallbackQuery):
    await callback.message.answer(text=f"Неизвестный callback: {callback.data}")