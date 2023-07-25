from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F


from urllib.request import urlopen
import json


# создаём роутер для дальнешей привязки к нему обработчиков
router = Router()


@router.message(Command("random"))
async def random_question_handler(msg: Message):
    try:
        url = f'http://127.0.0.1:8000/questions/random'
        response = urlopen(url)
        question =  json.load(response)
        await msg.answer(f"Вопрос {question['pk']} \n\n{question['question_text']}")
    except:
        await msg.answer(f"Ошибка загрузки вопроса")
