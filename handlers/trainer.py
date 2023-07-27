from aiogram import Router, types
from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.context import FSMContext

from aiogram.filters.callback_data import CallbackData

from db import database
from texts import Texts
from filters.user_type import UserTypeFilter


# создаём роутер для дальнешей привязки к нему обработчиков
router = Router()
router.message.filter(
    UserTypeFilter(user_types=['reg', 'admin'])
)

# Фабрика коллбеков для обработки нажатий на экзамены
class TrainerCallbackFactory(CallbackData, prefix='trainer'):
    exam_id: int
    se_id: int
    sen_id: int
    tag_id: int


# формируем клавиатуру для выбора экзамена
def select_exam_keyboard() -> InlineKeyboardMarkup:
    array_buttons: list[list[InlineKeyboardButton]] = []

    exam_tree = database.exam_tree

    for exam in exam_tree:
        if exam["is_active"]:
            array_buttons.append([
                InlineKeyboardButton(
                    text=exam['title'],
                    callback_data=TrainerCallbackFactory(
                        exam_id=exam["pk"],
                        se_id=0,
                        sen_id=0,
                        tag_id=0
                    ).pack()
                )
            ])
    
    array_buttons.append([
        InlineKeyboardButton(
            text=Texts.BACK_TEXT,
            callback_data="menu"
        )
    ])

    markup: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=array_buttons)
    return markup


@router.callback_query(TrainerCallbackFactory.filter(F.exam_id == 0))
async def exam_choice_handler(callback: types.CallbackQuery, callback_data: TrainerCallbackFactory):
    await callback.message.edit_text(text="Выбирай экзамен", reply_markup=select_exam_keyboard())


# формируем клавиатуру для выбора предмета под экзамен
def select_subject_keyboard(exam_id) -> InlineKeyboardMarkup:
    array_buttons: list[list[InlineKeyboardButton]] = []

    exam = database.get_exam(exam_id=exam_id)

    array_buttons.append([
        InlineKeyboardButton(
            text=Texts.BACK_TEXT,
            callback_data=TrainerCallbackFactory(
                exam_id=0,
                se_id=0,
                sen_id=0,
                tag_id=0
            ).pack()
        )
    ])

    for se in exam["subject_exams"]:
        if se["is_active"]:
            array_buttons.append([
                InlineKeyboardButton(
                    text=se['subject']['title'],
                    callback_data=TrainerCallbackFactory(
                        exam_id=exam_id,
                        se_id=se["pk"],
                        sen_id=0,
                        tag_id=0
                    ).pack()
                )
            ])

    markup: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=array_buttons)
    return markup


@router.callback_query(TrainerCallbackFactory.filter(F.exam_id != 0), TrainerCallbackFactory.filter(F.se_id == 0))
async def subject_choice_handler(callback: types.CallbackQuery, callback_data: TrainerCallbackFactory):
    exam_id = callback_data.exam_id
    await callback.message.edit_text(text=f"Выбирай предмет:", reply_markup=select_subject_keyboard(callback_data.exam_id))


# формируем клавиатуру для выбора номера в предмета под экзамен
def select_num_keyboard(exam_id, se_id) -> InlineKeyboardMarkup:
    array_buttons: list[list[InlineKeyboardButton]] = []

    se = database.get_subject_exam(exam_id=exam_id, se_id=se_id)

    array_buttons.append([
        InlineKeyboardButton(
            text=Texts.BACK_TEXT,
            callback_data=TrainerCallbackFactory(
                exam_id=exam_id,
                se_id=0,
                sen_id=0,
                tag_id=0
            ).pack()
        )
    ])

    for sen in se["subject_exam_numbers"]:
        if sen["is_active"]:
            title = f"{sen['num']}. {sen['title']}"
            array_buttons.append([
                InlineKeyboardButton(
                    text=title,
                    callback_data=TrainerCallbackFactory(
                        exam_id=exam_id,
                        se_id=se_id,
                        sen_id=sen["pk"],
                        tag_id=0
                    ).pack()
                )
            ])

    markup: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=array_buttons)
    return markup


@router.callback_query(TrainerCallbackFactory.filter(F.se_id != 0), TrainerCallbackFactory.filter(F.sen_id == 0))
async def num_choice_handler(callback: types.CallbackQuery, callback_data: TrainerCallbackFactory):
    exam_id, se_id = callback_data.exam_id, callback_data.se_id

    se = database.get_subject_exam(exam_id=exam_id, se_id=se_id)

    await callback.message.edit_text(text=f"{se['exam']['title']} по предмету <b>{se['subject']['title']}</b>\n<i>Доступно задач: {se['questions_exist']}</i>", reply_markup=select_num_keyboard(callback_data.exam_id, callback_data.se_id))


# формируем клавиатуру для выбора темы в номере в предмета под экзамен
def select_tag_keyboard(exam_id, se_id, sen_id) -> InlineKeyboardMarkup:
    array_buttons: list[list[InlineKeyboardButton]] = []

    sen = database.get_subject_exam_number(exam_id=exam_id, se_id=se_id, sen_id=sen_id)

    array_buttons.append([
        InlineKeyboardButton(
            text=Texts.BACK_TEXT,
            callback_data=TrainerCallbackFactory(
                exam_id=exam_id,
                se_id=se_id,
                sen_id=0,
                tag_id=0
            ).pack()
        )
    ])

    for exam_tag in sen["exam_tags"]:
        if exam_tag["is_active"]:
            array_buttons.append([
                InlineKeyboardButton(
                    text=exam_tag["title"],
                    callback_data=TrainerCallbackFactory(
                        exam_id=exam_id,
                        se_id=se_id,
                        sen_id=sen_id,
                        tag_id=exam_tag["pk"]
                    ).pack()
                )
            ])

    markup: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=array_buttons)
    return markup


@router.callback_query(TrainerCallbackFactory.filter(F.sen_id != 0), TrainerCallbackFactory.filter(F.tag_id == 0))
async def tag_choice_handler(callback: types.CallbackQuery, callback_data: TrainerCallbackFactory):
    exam_id, se_id, sen_id = callback_data.exam_id, callback_data.se_id, callback_data.sen_id
    se = database.get_subject_exam(exam_id=exam_id, se_id=se_id)
    sen = database.get_subject_exam_number(exam_id=exam_id, se_id=se_id, sen_id=sen_id)
    await callback.message.edit_text(text=f"Номер {sen['num']} из {se['exam']['title']} по предмету {se['subject']['title']}\nТема: <b>{sen['title']}</b>\n<i>Доступно задач: {sen['questions_exist']}</i>", reply_markup=select_tag_keyboard(callback_data.exam_id, callback_data.se_id, callback_data.sen_id))


@router.callback_query(TrainerCallbackFactory.filter(F.tag_id != 0))
async def tag_handler(callback: types.CallbackQuery, callback_data: TrainerCallbackFactory):
    exam_id, se_id, sen_id, tag_id = callback_data.exam_id, callback_data.se_id, callback_data.sen_id, callback_data.tag_id

    se = database.get_subject_exam(exam_id=exam_id, se_id=se_id)
    sen = database.get_subject_exam_number(exam_id=exam_id, se_id=se_id, sen_id=sen_id)
    tag = database.get_subject_exam_number_tag(exam_id=exam_id, se_id=se_id, sen_id=sen_id, tag_id=tag_id)

    kb = [
        [types.InlineKeyboardButton(text=Texts.BACK_TEXT, callback_data=TrainerCallbackFactory(
            exam_id=exam_id,
            se_id=se_id,
            sen_id=sen_id,
            tag_id=0
        ).pack())]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)

    await callback.message.edit_text(text=f"Номер {sen['num']} из {se['exam']['title']} по предмету {se['subject']['title']}\nТема: <b>{sen['title']}</b>\nПодтема:<b>{tag['title']}</b>\n<i>Доступно задач: {tag['questions_exist']}</i>", reply_markup=keyboard)