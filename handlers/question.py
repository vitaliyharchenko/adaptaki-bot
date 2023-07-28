from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from api import get_random_question, get_token_from_state, post_question_answer, get_question
from texts import Texts

from filters.user_type import UserTypeFilter
from callback_factories import TrainerCallbackFactory, QuestionCallbackFactory


# создаём роутер для дальнешей привязки к нему обработчиков
router = Router()


# создаем конечный автомат для хранения остояний
class QuestionStates(StatesGroup):
    wait_for_answer = State()
    show_verdict = State()
    show_explanation = State()



@router.message(Command("random"), UserTypeFilter(user_types=['reg', 'admin']))
async def random_question_handler(msg: Message, state: FSMContext):
    token = get_token_from_state(state)
    try:
        question = get_random_question(token=token)
        await msg.answer(f"Вопрос {question['pk']} \n\n{question['question_text']}")
    except:
        await msg.answer(f"Ошибка загрузки вопроса")


# запрошена задача по тегу без указания конкретного номера
@router.callback_query(QuestionCallbackFactory.filter(F.exam_tag_id != 0), QuestionCallbackFactory.filter(F.question_id == 0))
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

    await callback.message.answer(text=f"Вопрос {question['pk']} \n\n{question['question_text']}\n\nОтправь ответ боту ниже", reply_markup=keyboard)
    await state.set_state(QuestionStates.wait_for_answer)
    await state.update_data(chosen_question_id=question['pk'])


# получено сообщение в состоянии ожидания ответа на задачу
@router.message(QuestionStates.wait_for_answer)
async def answer_handler(message: Message, state: FSMContext):
    answer = message.text
    token = await get_token_from_state(state)
    user_data = await state.get_data()
    chosen_question_id = user_data.get('chosen_question_id', 0)
    chosen_exam_id = user_data.get('chosen_exam_id', 0)
    chosen_se_id = user_data.get('chosen_se_id', 0)
    chosen_sen_id = user_data.get('chosen_sen_id', 0)
    chosen_exam_tag_id = user_data.get('chosen_exam_tag_id', 0)

    kb = [
        [types.InlineKeyboardButton(text="Вернуться в меню", callback_data=TrainerCallbackFactory(
                        exam_id=chosen_exam_id,
                        se_id=chosen_se_id,
                        sen_id=chosen_sen_id,
                        tag_id=chosen_exam_tag_id
                    ).pack())],
        [types.InlineKeyboardButton(text="Смотреть решение", callback_data=QuestionCallbackFactory(
                        question_id=chosen_question_id,
                        exam_tag_id=chosen_exam_tag_id
                    ).pack())]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)

    try:
        verdict = post_question_answer(token=token, answer=answer, question_id=chosen_question_id)
        await message.answer(f"Вердикт: {verdict}", reply_markup=keyboard)
    except:
        await message.answer(f"Ошибка при попытке ответить на вопрос")
    
    await state.set_state(QuestionStates.show_verdict)


# запрошено пояснение к задаче в состоянии демонстрации вердикта
@router.callback_query(QuestionStates.show_verdict, QuestionCallbackFactory.filter(F.question_id != 0))
async def explanation_handler(callback: types.CallbackQuery, callback_data: QuestionCallbackFactory, state: FSMContext):
    token = await get_token_from_state(state)

    chosen_question_id = callback_data.question_id

    user_data = await state.get_data()
    chosen_exam_id = user_data.get('chosen_exam_id', 0)
    chosen_se_id = user_data.get('chosen_se_id', 0)
    chosen_sen_id = user_data.get('chosen_sen_id', 0)
    chosen_exam_tag_id = user_data.get('chosen_exam_tag_id', 0)

    question = get_question(question_id=chosen_question_id, token=token, need_answer=True)

    kb = [
        [types.InlineKeyboardButton(text="Вернуться в меню", callback_data=TrainerCallbackFactory(
                        exam_id=chosen_exam_id,
                        se_id=chosen_se_id,
                        sen_id=chosen_sen_id,
                        tag_id=chosen_exam_tag_id
                    ).pack())]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)

    await callback.message.answer(text=f"Пояснение к вопросу {question['pk']} \n\n{question['explanation_text']}\n\n{question['all_options']}", reply_markup=keyboard)
    await state.set_state(QuestionStates.show_explanation)
