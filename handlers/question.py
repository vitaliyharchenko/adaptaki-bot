from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F

from api import get_random_question

from filters.user_type import UserTypeFilter


# создаём роутер для дальнешей привязки к нему обработчиков
router = Router()


@router.message(Command("random"), UserTypeFilter(user_types=['reg', 'admin']))
async def random_question_handler(msg: Message):
    try:
        question = get_random_question(user_id=msg.from_user.id)
        await msg.answer(f"Вопрос {question['pk']} \n\n{question['question_text']}")
    except:
        await msg.answer(f"Ошибка загрузки вопроса")
