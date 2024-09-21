class DataClient:
    table_title = ["town", "landmark", "fact", "user", "quiz_theme", "quiz", "quiz_ask"]

    def __init__(self) -> None:
        self.data = dict()
        self.data["town"] = list()
        self.data["landmark"] = list()
        self.data["fact"] = list()
        self.data["user"] = list()
        self.data["quiz_theme"] = list()
        self.data["quiz"] = list()
        self.data["quiz_ask"] = list()
        self.data["user_quiz"] = list()

        self.templates = dict()
        self.templates["town"] = {
            "id": 0,
            "title": ""
        }
        self.templates["landmark"] = {
            "id": 0,
            "town_id": 0,
            "title": "",
            "image_link": "",
        }
        self.templates["fact"] = {
            "id": 0,
            "landmark_id": 0,
            "title": "",
            "text": "",
            "audio": "",
            "image_link": "",
        }
        self.templates["user"] = {
            "id": 0,
            "name": "",
            "link": "",
            "status": "",
            "quiz_score": 0
        }
        self.templates["quiz_theme"] = {
            "id": 0,
            "title": "",
            "description": "",
        }
        self.templates["quiz"] = {
            "id": 0,
            "theme_id": 0,
            "title": "",
            "description": "",
        }
        self.templates["quiz_ask"] = {
            "id": 0,
            "quiz_id": 0,
            "true_q": "",
            "ask": "",
            "false_q1": "",
            "false_q2": "",
            "false_q3": "",
            "image_id": "",
        }
        self.templates["user_quiz"] = {
            "id": 0,
            "user_id": 0,
            "quiz_id": 0,
            "score": 0,
        }

    def set_new_town(self, title: str) -> bool:
        try:
            index = len(self.data["town"])
            template = self.templates["town"].copy()
            template["id"] = index
            template["title"] = title
            self.data["town"].append(template)
            return True
        except Exception:
            return False

    def set_new_landmark(self, town_id: int, title: str, image_link: str) -> bool:
        try:
            index = len(self.data["landmark"])
            template = self.templates["landmark"].copy()
            template["id"] = index
            template["town_id"] = town_id
            template["title"] = title
            template["image_link"] = image_link
            self.data["landmark"].append(template)
            return True
        except Exception:
            return False

    def set_new_fact(self, landmark_id: int, title: str, text: str, audio: str, image_link: str) -> bool:
        try:
            index = len(self.data["fact"])
            template = self.templates["fact"].copy()
            template["id"] = index
            template["landmark_id"] = landmark_id
            template["title"] = title
            template["text"] = text
            template["audio"] = audio
            template["image_link"] = image_link
            self.data["fact"].append(template)
            return True
        except Exception:
            return False

    def set_new_user(self, user_name: str, user_id: str, status: str = "base", quiz_score: float = 0.) -> bool:
        try:
            index = len(self.data["user"])
            template = self.templates["user"].copy()
            template["id"] = index
            template["user_name"] = user_name
            template["user_id"] = user_id
            template["status"] = status
            template["quiz_score"] = quiz_score
            self.data["user"].append(template)
            return True
        except Exception:
            return False

    def set_new_quiz_theme(self, title: str, description: str) -> bool:
        try:
            index = len(self.data["quiz_theme"])
            template = self.templates["quiz_theme"].copy()
            template["id"] = index
            template["title"] = title
            template["description"] = description
            self.data["quiz_theme"].append(template)
            return True
        except Exception:
            return False

    def set_new_quiz(self, quiz_theme_id: int, title: str, description: str) -> bool:
        try:
            index = len(self.data["quiz"])
            template = self.templates["quiz"].copy()
            template["id"] = index
            template["quiz_theme_id"] = quiz_theme_id
            template["title"] = title
            template["description"] = description
            self.data["quiz"].append(template)
            return True
        except Exception:
            return False

    def set_new_quiz_ask(self, quiz_id: int, quiz_ask: str, t_q: str,
                         f_q1: str, f_q2: str, f_q3: str, image_id: str) -> bool:
        try:
            index = len(self.data["quiz_ask"])
            template = self.templates["quiz_ask"].copy()
            template["id"] = index
            template["quiz_id"] = quiz_id
            template["quiz_ask"] = quiz_ask
            template["t_q"] = t_q
            template["f_q1"] = f_q1
            template["f_q2"] = f_q2
            template["f_q3"] = f_q3
            template["image_id"] = image_id
            self.data["quiz_ask"].append(template)
            return True
        except Exception:
            return False

    def set_new_user_quiz(self, quiz_id: int, user_id: int, score: int) -> bool:
        try:
            index = len(self.data["user_quiz"])
            template = self.templates["user_quiz"].copy()
            template["id"] = index
            template["user_id"] = user_id
            template["quiz_id"] = quiz_id
            template["score"] = score
            self.data["user_quiz"].append(template)
            return True
        except Exception:
            return False

    def exist_user_quiz(self, user_id: int, quiz_id: int) -> [bool, int]:
        try:
            for elem in self.data["user_quiz"]:
                if elem["user_id"] == user_id and elem["quiz_id"] == quiz_id:
                    return [True, elem["id"]]
            return [False, -1]
        except Exception:
            return [False, -1]

    def set_score_user_quiz(self, user_id: int, quiz_id: int, score: int):
        result = self.exist_user_quiz(user_id=user_id, quiz_id=quiz_id)
        if result[0]:
            for elem in self.data["user_quiz"]:
                if elem["id"] == result[1]:
                    elem["score"] += score
            # self.data["user_quiz"][result[1]] += score
        else:
            self.set_new_user_quiz(user_id=user_id, quiz_id=quiz_id, score=score)

    ## Wrong function
    def get_data(self, table_title: str) -> str:
        return str(self.data[table_title])

    def get_all_data(self) -> str:
        text = ""
        for title in self.table_title:
            text += self.get_data(title) + "\n\n"
        return text

    def get_user_data(self):
        return self.data["user"]

    def get_user_quiz_data(self):
        return self.data["user_quiz"]

    #################
    # Program for program work
    #################

    def user_exist(self, user_id: str) -> bool:
        for elem in self.data["user"]:
            if elem["user_id"] == user_id:
                return True
        return False

    def set_new_admin(self, user_id: str) -> bool:
        for elem in self.data["user"]:
            if elem["user_id"] == user_id:
                elem["status"] = "admin"
                return True
        return False

    def town_exist(self, town_title: str) -> bool:
        for elem in self.data["town"]:
            if elem["title"] == town_title:
                return True
        return False

    def landmark_exist(self, landmark_title: str, town_id: int) -> bool:
        for elem in self.data["landmark"]:
            if elem["town_id"] == town_id and elem["title"] == landmark_title:
                return True
        return False

    def fact_exist(self, fact_title: str, landmark_id: int, town_id: int) -> bool:
        for elem in self.data["fact"]:
            if elem["town_id"] == town_id and elem["landmark_id"] == landmark_id and elem["title"] == fact_title:
                return True
        return False

    def get_all_town_title(self) -> list:
        town_title = list()
        for elem in self.data["town"]:
            town_title.append(elem["title"])
        return town_title

    def get_all_landmark_by_town_id(self, town_id: int) -> list:
        landmark_title = list()
        for elem in self.data["landmark"]:
            if elem["town_id"] == town_id:
                landmark_title.append(elem["title"])
        return landmark_title

    def get_town_id(self, town_title: str) -> int:
        for elem in self.data["town"]:
            if elem["title"] == town_title:
                return elem["id"]

    def get_landmark_id(self, town_id: int, landmark_title: str) -> int:
        for elem in self.data["landmark"]:
            if elem["town_id"] == town_id and elem["title"] == landmark_title:
                return elem["id"]

    def get_quiz_theme_list(self) -> list:
        themes = list()
        for elem in self.data["quiz_theme"]:
            themes.append(elem["title"])
        return [len(themes) > 0, themes]

    def get_quiz_list(self, theme_id: int) -> list:
        quiz = list()
        for elem in self.data["quiz"]:
            if elem["theme_id"] == theme_id:
                quiz.append(elem["title"])
        return [len(quiz) > 0, quiz]

    def get_quiz_theme_id(self, theme_title: str) -> int:
        for elem in self.data["quiz_theme"]:
            if elem["title"] == theme_title:
                return elem["id"]

    def get_quiz_id(self, theme_title: str) -> int:
        for elem in self.data["quiz"]:
            if elem["title"] == theme_title:
                return elem["id"]

    def get_user_id(self, user_id: str) -> int:
        for elem in self.data["user"]:
            if elem["user_id"] == user_id:
                return elem["id"]

    def get_quiz_ask(self, quiz_id: int, ask_id: list) -> [bool, dict]:
        for elem in self.data["quiz_ask"]:
            if elem["quiz_id"] == quiz_id and elem["id"] not in ask_id:
                return [True, elem]
        return [False, dict()]

    def get_statistics(self, user_id: int) -> str:
        total_score = 0
        msg_back = f"Ваш счет за викторины:\n"
        for elem in self.data["user_quiz"]:
            if elem["user_id"] == user_id:
                msg_back += f"В викторине {elem['quiz_id'] + 1} Вы набрали {elem['score']} баллов.\n"
                total_score += elem['score']
        msg_back += f"Всего Вы набрали: {total_score}."
        return msg_back




    """
    Needed functions:
    set_new_user
    set_new_town
    set_new_landmark
    set_new_fact
    """








