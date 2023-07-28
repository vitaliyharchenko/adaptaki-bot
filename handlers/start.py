from aiogram import Router
from aiogram import types
from aiogram import F
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from filters.user_type import UserTypeFilter
from api import reg_user
from db import database


# создаём роутер для дальнешей привязки к нему обработчиков
router = Router()


@router.message(Command("start"), UserTypeFilter(user_types=['reg', 'admin']))
async def start_handler(msg: Message):
    await msg.answer(f"С возвращением!", reply_markup=types.ReplyKeyboardRemove())


# создаем конечный автомат для хранения остояний
class RegUser(StatesGroup):
    registration_need = State()
    choosing_first_name = State()
    choosing_last_name = State()
    choosing_class = State()
    choosing_phone = State()


@router.message(Command("start"), UserTypeFilter(user_types=['anon']))
async def start_handler(msg: Message, state: FSMContext):

    kb = [
        [types.InlineKeyboardButton(text="Начать регистрацию", callback_data="reg_start")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)

    await msg.answer(f"Привет! Я бот с задачами ЕГЭ. Давай знакомиться!\n\nЧтобы воспользоваться мной, нужно пройти простую регистрацию.", reply_markup=keyboard)
    await state.set_state(RegUser.registration_need)


@router.callback_query(RegUser.registration_need, F.data == 'reg_start')
async def cmd_reg(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(RegUser.choosing_first_name)
    await callback.message.edit_text(f"Давай начнем! Напиши свое имя:")
    await callback.answer()


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

@router.message(RegUser.choosing_class, F.text)
async def class_chosen(message: Message, state: FSMContext):
    class_of = message.text

    for cl in CLASSES:
        if class_of == cl[1]:
            class_of = cl[0]

    await state.update_data(class_of=class_of)

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

    user_data["telegram_id"] = message.from_user.id
    user_data["telegram_username"] = message.from_user.username

    try:
        user = reg_user(user_data)
        database.set_user(user_id=message.from_user.id, data=user)

        await message.answer(f"{user['first_name']}, вы успешно зарегистрированы! \n\n Чтобы перейти в главное меню, нажмите /menu", reply_markup=types.ReplyKeyboardRemove())
        await state.clear()
    except Exception as e:
        kb = [
            [types.InlineKeyboardButton(text="Начать регистрацию", callback_data="reg_start")]
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
        await message.answer(f"Ошибка при регистрации: {e} \n\nДавай начнем заново", reply_markup=keyboard)
        await state.set_state(RegUser.registration_need)
