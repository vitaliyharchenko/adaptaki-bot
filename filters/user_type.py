from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from db import database
from api import get_user


class UserTypeFilter(BaseFilter):
    # аргумент user_types это массив подходящих значений
    # 1. anon
    # 2. reg
    # 3. admin
    def __init__(self, user_types):
        self.user_types = user_types

    async def __call__(self, message: Message, state: FSMContext) -> bool:
        
        user_id = message.from_user.id
        user_type = 'anon'

        state_data = await state.get_data()
        user = state_data.get("user_data", False)
        # user = database.get_user(user_id=user_id)

        # если пользователя нет в базе - идем на сервер
        if not user:
            try:
                user_data = get_user(user_id=user_id)

                if user_data['is_staff']:
                    user_type = 'admin'
                elif user_data['is_active']:
                    user_type = 'reg'
                
                await state.update_data(user_data=user_data)
                # database.set_user(user_id=user_id, data=user_data)
            except Exception as e:
                print("Except: ", e)
        else:
            if user['is_staff']:
                user_type = 'admin'
            elif user['is_active']:
                user_type = 'reg'

        return user_type in self.user_types
