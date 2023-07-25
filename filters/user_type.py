from aiogram.filters import BaseFilter
from aiogram.types import Message

from urllib.request import urlopen
import json


# Словарь, в котором будут храниться данные пользователей
users: dict = {}


class UserTypeFilter(BaseFilter):
    # аргумент user_types это массив подходящих значений
    # 1. anon
    # 2. reg
    # 3. admin
    def __init__(self, user_types):
        self.user_types = user_types

    async def __call__(self, message: Message) -> bool:
        
        user_id = message.from_user.id
        user_type = 'anon'

        # если пользователя нет в массиве, то обращаемся на сервер
        if user_id not in users:
            try:
                url = f'http://127.0.0.1:8000/users/check/telegram/{user_id}/'
                response = urlopen(url)
                user_data = json.load(response)
                users[user_id] = user_data

                if user_data['is_staff']:
                    user_type = 'admin'
                elif user_data['is_active']:
                    user_type = 'reg'
            except:
                pass
        else:
            user_data = users[user_id]
            if user_data['is_staff']:
                user_type = 'admin'
            elif user_data['is_active']:
                user_type = 'reg'

        return user_type in self.user_types
