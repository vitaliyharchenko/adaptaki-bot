from aiogram import Router
from aiogram import types
from aiogram import F
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from filters.user_type import UserTypeFilter


# создаём роутер для дальнешей привязки к нему обработчиков
router = Router()


@router.message(Command("start"), UserTypeFilter(user_types=['reg', 'admin']))
async def start_handler(msg: Message):
    await msg.answer(f"С возвращением!")


# создаем конечный автомат для хранения остояний
class RegUser(StatesGroup):
    registration_need = State()
    choosing_first_name = State()
    choosing_last_name = State()
    choosing_class = State()
    choosing_phone = State()


@router.message(Command("start"), UserTypeFilter(user_types=['anon', 'reg']))
async def start_handler(msg: Message, state: FSMContext):

    kb = [
        [types.KeyboardButton(text="Начать регистрацию")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

    await msg.answer(f"Привет! Я бот с задачами ЕГЭ. Давай знакомиться!\n\nЧтобы воспользоваться мной, нужно пройти простую регистрацию.", reply_markup=keyboard)
    await state.set_state(RegUser.registration_need)


@router.message(RegUser.registration_need, F.text == 'Начать регистрацию')
async def cmd_reg(message: Message, state: FSMContext):
    await message.answer(
        text="Давай начнем! Напиши свое имя:",
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

    await message.answer(f"Твой набор данных:{user_data}", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()
