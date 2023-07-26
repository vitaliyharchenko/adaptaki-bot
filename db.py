# Словарь, в котором будут храниться данные пользователей

class DB:
    def __init__(self):
        self.users = {}

    def get_user(self, user_id):
        try:
            return self.users[user_id]
        except:
            return None
    
    def set_user(self, user_id, data):
        self.users[user_id] = data


database = DB()