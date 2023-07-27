from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext

from api import get_random_question, get_token_from_state
from texts import Texts

from filters.user_type import UserTypeFilter
from callback_factories import TrainerCallbackFactory, QuestionCallbackFactory


# создаём роутер для дальнешей привязки к нему обработчиков
router = Router()


@router.message(Command("random"), UserTypeFilter(user_types=['reg', 'admin']))
async def random_question_handler(msg: Message, state: FSMContext):
    token = get_token_from_state(state)
    try:
        question = get_random_question(token=token)
        await msg.answer(f"Вопрос {question['pk']} \n\n{question['question_text']}")
    except:
        await msg.answer(f"Ошибка загрузки вопроса")


@router.callback_query(QuestionCallbackFactory.filter(F.exam_tag_id != 0))
async def exam_tag_question_handler(callback: types.CallbackQuery, callback_data: QuestionCallbackFactory, state: FSMContext):
    exam_tag_id = callback_data.exam_tag_id

    token = await get_token_from_state(state)

    user_data = await state.get_data()
    chosen_exam_id = user_data.get('chosen_exam_id', 0)
    chosen_se_id = user_data.get('chosen_se_id', 0)
    chosen_sen_id = user_data.get('chosen_sen_id', 0)
    chosen_exam_tag_id = user_data.get('chosen_exam_tag_id', 0)

    question = get_random_question(exam_tag_id=exam_tag_id, token=token)

    kb = [
        [types.InlineKeyboardButton(text=Texts.BACK_TEXT, callback_data=TrainerCallbackFactory(
                        exam_id=chosen_exam_id,
                        se_id=chosen_se_id,
                        sen_id=chosen_sen_id,
                        tag_id=chosen_exam_tag_id
                    ).pack())]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)

    await callback.message.edit_text(text=f"Вопрос {question['pk']} \n\n{question['question_text']}", reply_markup=keyboard)
