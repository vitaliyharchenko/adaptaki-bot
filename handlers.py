from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F


# создаём роутер для дальнешей привязки к нему обработчиков
router = Router()


@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer("Привет! Я помогу тебе узнать твой ID, просто отправь мне любое сообщение")


@router.message(Command("contact"))
async def contact_handler(msg: Message):
    kb = [
        [types.KeyboardButton(text="Дать доступ", request_contact=True)]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Предоставьте доступ к номеру телефона для идентефикации")
    await msg.answer("Привет! Для продолжения работы поделись своим телефоном. К нему будет привязан профиль с твоей статистикой", reply_markup=keyboard)


@router.message(F.content_type.in_({'contact'}))
async def send_contact_handler(msg: Message):
    await msg.answer(f"Получен телефон: {msg.contact.phone_number}")


@router.message()
async def message_handler(msg: Message):
    await msg.answer(f"Твой ID: {msg.from_user.id}")