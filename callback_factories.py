from aiogram.filters.callback_data import CallbackData


# Фабрика коллбеков для обработки нажатий на экзамены
class TrainerCallbackFactory(CallbackData, prefix='trainer'):
    exam_id: int
    se_id: int
    sen_id: int
    tag_id: int
    edit: bool


# Фабрика коллбеков для обработки состояния с вопросами
class QuestionCallbackFactory(CallbackData, prefix='questions'):
    exam_tag_id: int
    question_id: int