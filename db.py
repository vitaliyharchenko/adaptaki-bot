# Словарь, в котором будут храниться данные пользователей

class DB:
    def __init__(self):
        self.users = {}
        self.exam_tree = []

    def get_user(self, user_id):
        try:
            return self.users[user_id]
        except:
            return None

    def set_exam_tree(self, exam_tree):
        self.exam_tree = exam_tree
    
    def get_exam(self, exam_id):
        for exam in self.exam_tree:
            if exam["pk"] == exam_id:
                return exam
        return None

    def get_subject_exam(self, exam_id, se_id):
        exam = self.get_exam(exam_id=exam_id)
        for se in exam["subject_exams"]:
            if se["pk"] == se_id:
                return se
        return None
    
    def get_subject_exam_number(self, exam_id, se_id, sen_id):
        se = self.get_subject_exam(exam_id=exam_id, se_id=se_id)
        for sen in se["subject_exam_numbers"]:
            if sen["pk"] == sen_id:
                return sen
        return None
    
    def get_subject_exam_number_tag(self, exam_id, se_id, sen_id, tag_id):
        sen = self.get_subject_exam_number(exam_id=exam_id, se_id=se_id, sen_id=sen_id)
        for exam_tag in sen["exam_tags"]:
            if exam_tag["pk"] == tag_id:
                return exam_tag
        return None

    def set_user(self, user_id, data):
        self.users[user_id] = data


database = DB()