from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram import F

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from urllib.request import urlopen
import json

from filters.user_type import UserTypeFilter


# создаём роутер для дальнешей привязки к нему обработчиков
router = Router()

# создаем конечный автомат для хранения остояний
class RegUser(StatesGroup):
    choosing_first_name = State()
    choosing_last_name = State()
    choosing_class = State()
    choosing_phone = State()

# список доступных классов
CLASSES = (
    ('parent', 'Родитель'),
    ('old', 'Выпускник'),
    ('2024', '11 класс'),
    ('2025', '10 класс'),
    ('2026', '9 класс'),
    ('2027', '8 класс'),
    ('2028', '7 класс'),
)


@router.message(Command("reg"), UserTypeFilter(user_types=['anon', 'reg']))
async def cmd_reg(message: Message, state: FSMContext):
    await message.answer(
        text="Для работы в нашем боте нужно пройти короткую регистрацию. Напиши свое имя:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    # Устанавливаем пользователю состояние "выбирает название"
    await state.set_state(RegUser.choosing_first_name)


@router.message(RegUser.choosing_first_name, F.text)
async def first_name_chosen(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer(
        text="Спасибо. Теперь, пожалуйста, введите фамилию:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(RegUser.choosing_last_name)


@router.message(RegUser.choosing_last_name, F.text)
async def last_name_chosen(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)

    keyboard = []
    for cl in CLASSES:
        keyboard.append([KeyboardButton(text=cl[1])])

    reply_markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    await message.answer(
        text="Отлично! Теперь выберите класс:",
        reply_markup=reply_markup
    )
    await state.set_state(RegUser.choosing_class)


@router.message(RegUser.choosing_class, F.text)
async def class_chosen(message: Message, state: FSMContext):
    await state.update_data(class_of=message.text)

    kb = [
        [types.KeyboardButton(text="Дать доступ", request_contact=True)]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

    await message.answer("Наконец поделись своим телефоном. К нему будет привязан профиль с твоей статистикой. Для этого нажми кнопку 'Дать доступ' ниже", reply_markup=keyboard)
    await state.set_state(RegUser.choosing_phone)


@router.message(RegUser.choosing_phone, F.content_type.in_({'contact'}))
async def phone_chosen(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)

    user_data = await state.get_data()

    await message.answer(f"Твой набор данных:{user_data}")
    await state.clear()








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
