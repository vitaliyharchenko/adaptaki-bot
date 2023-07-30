from aiogram import Router, types
from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from db import database
from filters.user_type import UserTypeFilter
from handlers.trainer import TrainerCallbackFactory


# создаём роутер для дальнешей привязки к нему обработчиков
router = Router()
router.message.filter(
    UserTypeFilter(user_types=['reg', 'admin'])
)


# клавиатура для главного меню
def main_kb(edit=False):
    kb = [
        [types.InlineKeyboardButton(text="Тренажер с задачами", callback_data=TrainerCallbackFactory(
                exam_id=0,
                se_id=0,
                sen_id=0,
                tag_id=0,
                edit=edit
            ).pack())],
        [types.InlineKeyboardButton(text="Профиль", callback_data="menu_profile")]
    ]
    main_keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    return main_keyboard

@router.message(Command("menu"))
async def menu_handler(msg: Message):
    await msg.answer(f"Главное меню", reply_markup=main_kb(edit=True))


@router.callback_query(F.data=='menu')
async def menu_callback_handler(callback: types.CallbackQuery):
    await callback.message.edit_text(text="Главное меню", reply_markup=main_kb(edit=True))


@router.callback_query(F.data=='menu_profile')
async def profile_handler(callback: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    user_data = state_data.get("user_data", False)

    kb = [
        [types.InlineKeyboardButton(text="Назад", callback_data="menu")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)

    if user_data:
        await callback.message.edit_text(f"Твои данные: {user_data}", reply_markup=keyboard)
    else:
        await callback.message.edit_text(f"Твои данные недоступны", reply_markup=keyboard)