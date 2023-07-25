from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F


from urllib.request import urlopen
import json


# создаём роутер для дальнешей привязки к нему обработчиков
router = Router()


@router.message(Command("contact"))
async def contact_handler(msg: Message):
    kb = [
        [types.KeyboardButton(text="Дать доступ", request_contact=True)]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Предоставьте доступ к номеру телефона для идентефикации")
    await msg.answer("Привет! Для регистрации поделись своим телефоном. К нему будет привязан профиль с твоей статистикой", reply_markup=keyboard)


@router.message(F.content_type.in_({'contact'}))
async def send_contact_handler(msg: Message):
    await msg.answer(f"Получен телефон: {msg.contact.phone_number}")


@router.message(Command("check"))
async def check_reg_handler(msg: Message):
    try:
        url = f'http://127.0.0.1:8000/users/check/telegram/{msg.from_user.id}/'
        response = urlopen(url)
        user =  json.load(response)
        await msg.answer(f"{user['first_name']} {user['last_name']}, вы зарегистрированы: {user}")
    except:
        await msg.answer(f"Вы не зарегистрированы")
