from geopy.geocoders import Nominatim
from geopy.distance import geodesic as GD
import pymysql
import time
import random
from config import host, user, password, db_version, BASE_IMAGE_ID
from languages.languages import languages


class DataClient:
    DATABASE_NAME = "guide_bot"

    table_title = ["town", "landmark", "fact", "user", "quiz_theme", "quiz", "quiz_ask"]
    drop_tables = ["quiz_ask", "quiz", "quiz_theme", "fact", "landmark", "town", "user"]

    def __init__(self) -> None:
        self.geolocator = Nominatim(user_agent="Bar Guide")
        self.con = pymysql.Connection(
            host=host,
            user=user,
            port=3306,
            password=password,
            use_unicode=True,
            charset="utf8",
            cursorclass=pymysql.cursors.DictCursor
        )
        self.create_db()
        print(self.create_all_tables())

    def create_db(self, db_title: str = DATABASE_NAME) -> bool:
        try:
            request = f"CREATE DATABASE IF NOT EXISTS {db_title};"
            with self.con.cursor() as cur:
                cur.execute(request)
                self.con.commit()
                return True
        except Exception:
            return False

    def create_table(self, request: str) -> bool:
        try:
            with self.con.cursor() as cur:
                cur.execute(request)
                self.con.commit()
                return True
        except Exception as ex:
            print(ex)
            return False

    def create_town_table(self) -> bool:
        table = "town"
        request = f"""CREATE TABLE IF NOT EXISTS {self.DATABASE_NAME}.{table} (id int AUTO_INCREMENT,
                      title VARCHAR(50), 
                      language VARCHAR(10),
                      version VARCHAR(20) default '{db_version}',

                      PRIMARY KEY(id),
                      UNIQUE(title))"""
        return self.create_table(request=request)

    def create_landmark_table(self) -> bool:
        table = "landmark"
        request = f"""CREATE TABLE IF NOT EXISTS {self.DATABASE_NAME}.{table} (id int AUTO_INCREMENT,
                      town_id int,
                      title VARCHAR(50),
                      image_id VARCHAR(100),
                      num_facts int default 0, 
                      language VARCHAR(10),
                      version VARCHAR(20) default '{db_version}',

                      PRIMARY KEY(id),
                      UNIQUE(title),
                      FOREIGN KEY(town_id) REFERENCES town(id) ON DELETE CASCADE ON UPDATE CASCADE)"""
        return self.create_table(request=request)

    def create_fact_table(self) -> bool:
        table = "fact"
        request = f"""CREATE TABLE IF NOT EXISTS {self.DATABASE_NAME}.{table} (id int AUTO_INCREMENT,
                      landmark_id int,
                      title VARCHAR(50),
                      text TEXT,
                      num int,
                      audio_id VARCHAR(100),
                      image_id VARCHAR(100), 
                      language VARCHAR(10),
                      version VARCHAR(20) default '{db_version}',

                      PRIMARY KEY(id),
                      UNIQUE(title),
                      FOREIGN KEY(landmark_id) REFERENCES landmark(id) ON DELETE CASCADE ON UPDATE CASCADE)"""
        return self.create_table(request=request)

    def create_user_table(self) -> bool:
        table = "user"
        request = f"""CREATE TABLE IF NOT EXISTS {self.DATABASE_NAME}.{table} (id int AUTO_INCREMENT,
                      name VARCHAR(50),
                      user_id VARCHAR(50),
                      status VARCHAR(20),
                      quiz_score int, 
                      language VARCHAR(10) default 'en',
                      version VARCHAR(20) default '{db_version}',

                      PRIMARY KEY(id),
                      UNIQUE(user_id))"""
        return self.create_table(request=request)

    def create_quiz_theme_table(self) -> bool:
        table = "quiz_theme"
        request = f"""CREATE TABLE IF NOT EXISTS {self.DATABASE_NAME}.{table} (id int AUTO_INCREMENT,
                      title VARCHAR(50),
                      description TEXT, 
                      enabled VARCHAR(1) DEFAULT '1',
                      language VARCHAR(10),
                      version VARCHAR(20) default '{db_version}',

                      PRIMARY KEY(id),
                      UNIQUE(title))"""
        return self.create_table(request=request)

    def create_quiz_table(self) -> bool:
        table = "quiz"
        request = f"""CREATE TABLE IF NOT EXISTS {self.DATABASE_NAME}.{table} (id int AUTO_INCREMENT,
                      theme_id int,
                      title VARCHAR(50),
                      description TEXT, 
                      enabled VARCHAR(1) DEFAULT '1',
                      language VARCHAR(10),
                      version VARCHAR(20) default '{db_version}',

                      PRIMARY KEY(id),
                      UNIQUE(title, theme_id),
                      FOREIGN KEY(theme_id) REFERENCES quiz_theme(id) ON DELETE CASCADE ON UPDATE CASCADE)"""
        return self.create_table(request=request)

    def create_quiz_ask_table(self) -> bool:
        table = "quiz_ask"
        request = f"""CREATE TABLE IF NOT EXISTS {self.DATABASE_NAME}.{table} (id int AUTO_INCREMENT,
                      quiz_id int,
                      ask VARCHAR(500),
                      t_q VARCHAR(100),
                      f_q1 VARCHAR(100),
                      f_q2 VARCHAR(100),
                      f_q3 VARCHAR(100),
                      image_id VARCHAR(100),
                      big_answer TEXT, 
                      language VARCHAR(10),
                      version VARCHAR(20) default '{db_version}',

                      PRIMARY KEY(id),
                      UNIQUE(quiz_id, ask),
                      FOREIGN KEY(quiz_id) REFERENCES quiz(id) ON DELETE CASCADE ON UPDATE CASCADE)"""
        return self.create_table(request=request)

    def create_user_quiz_table(self) -> bool:
        table = "user_quiz"
        request = f"""CREATE TABLE IF NOT EXISTS {self.DATABASE_NAME}.{table} (id int AUTO_INCREMENT,
                      user_id int,
                      quiz_id int,
                      score int, 
                      language VARCHAR(10),
                      version VARCHAR(20) default '{db_version}',

                      PRIMARY KEY(id),
                      UNIQUE(user_id, quiz_id),
                      FOREIGN KEY(user_id) REFERENCES user(id) ON DELETE CASCADE ON UPDATE CASCADE,
                      FOREIGN KEY(quiz_id) REFERENCES quiz(id) ON DELETE CASCADE ON UPDATE CASCADE)"""
        return self.create_table(request=request)

    def create_event_type_table(self) -> bool:
        table = "event_type"
        request = f"""CREATE TABLE IF NOT EXISTS {self.DATABASE_NAME}.{table} (id int AUTO_INCREMENT PRIMARY KEY,
                             title VARCHAR(50) UNIQUE,
                             description TEXT, 
                             language VARCHAR(10),
                             version VARCHAR(20) default '{db_version}' )"""
        return self.create_table(request=request)

    def create_event_table(self) -> bool:
        table = "event"
        request = f"""CREATE TABLE IF NOT EXISTS {self.DATABASE_NAME}.{table} (id int AUTO_INCREMENT PRIMARY KEY,
                      title VARCHAR(50) UNIQUE,
                      description TEXT,
                      town_id int,
                      event_type_id int, 
                      language VARCHAR(10),
                      version VARCHAR(20) default '{db_version}',
                      
                      UNIQUE(title, event_type_id),
                      FOREIGN KEY(town_id) REFERENCES town(id) ON DELETE CASCADE ON UPDATE CASCADE,
                      FOREIGN KEY(event_type_id) REFERENCES event_type(id) ON DELETE CASCADE ON UPDATE CASCADE)"""
        return self.create_table(request=request)

    def create_event_group_table(self) -> bool:
        table = "event_group"
        request = f"""CREATE TABLE IF NOT EXISTS {self.DATABASE_NAME}.{table} (id int AUTO_INCREMENT PRIMARY KEY,
                      count_place int,
                      guide_name VARCHAR(20),
                      event_id int,
                      description TEXT,
                      language VARCHAR(10),
                      local_info TEXT,
                      version VARCHAR(20) default '{db_version}',
                    
                      UNIQUE(guide_name, event_id),
                      FOREIGN KEY(event_id) REFERENCES event(id) ON DELETE CASCADE ON UPDATE CASCADE)"""
        return self.create_table(request=request)

    def create_participants_table(self) -> bool:
        table = "participants"
        request = f"""CREATE TABLE IF NOT EXISTS {self.DATABASE_NAME}.{table} (id int AUTO_INCREMENT PRIMARY KEY,
                      group_id int,
                      user_id int,
                      contact VARCHAR(20) default 0, 
                      edu_program VARCHAR (100) DEFAULT 'empty',
                      edu_faculty VARCHAR (100) DEFAULT 'empty',
                      language VARCHAR(10),
                      version VARCHAR(20) default '{db_version}',
                      
                      UNIQUE(user_id, group_id),
                      FOREIGN KEY(group_id) REFERENCES event_group(id) ON DELETE CASCADE ON UPDATE CASCADE,
                      FOREIGN KEY(user_id) REFERENCES user(id) ON DELETE CASCADE ON UPDATE CASCADE)"""
        return self.create_table(request=request)

    def create_trip_table(self) -> bool:
        table = "trip"
        request = f"""CREATE TABLE IF NOT EXISTS {self.DATABASE_NAME}.{table} (id int AUTO_INCREMENT,
                      town_id int,
                      title VARCHAR(50),
                      description TEXT, 
                      count_stages int DEFAULT 0,
                      language VARCHAR(10),
                      version VARCHAR(20) default '{db_version}',

                      PRIMARY KEY(id),
                      UNIQUE(title),
                      FOREIGN KEY(town_id) REFERENCES town(id) ON DELETE CASCADE ON UPDATE CASCADE)"""
        return self.create_table(request=request)

    def create_trip_stage_table(self) -> bool:
        table = "trip_stage"
        request = f"""CREATE TABLE IF NOT EXISTS {self.DATABASE_NAME}.{table} (id int AUTO_INCREMENT,
                      trip_id int,
                      title VARCHAR(50),
                      description TEXT, 
                      num_stage int,
                      count_elem INT DEFAULT 0,
                      language VARCHAR(10),
                      version VARCHAR(20) default '{db_version}',

                      PRIMARY KEY(id),
                      UNIQUE(title, trip_id),
                      FOREIGN KEY(trip_id) REFERENCES trip(id) ON DELETE CASCADE ON UPDATE CASCADE)"""
        return self.create_table(request=request)

    def create_stage_element_table(self) -> bool:
        table = "stage_element"
        request = f"""CREATE TABLE IF NOT EXISTS {self.DATABASE_NAME}.{table} (id int AUTO_INCREMENT,
                      trip_stage_id int,
                      title VARCHAR(50),
                      description TEXT, 
                      image_link VARCHAR(200) DEFAULT '0',
                      audio_link VARCHAR(200) DEFAULT '0',
                      num_elem int,
                      language VARCHAR(10),
                      version VARCHAR(20) default '{db_version}',

                      PRIMARY KEY(id),
                      UNIQUE(title, trip_stage_id),
                      FOREIGN KEY(trip_stage_id) REFERENCES trip_stage(id) ON DELETE CASCADE ON UPDATE CASCADE)"""
        return self.create_table(request=request)

    def create_all_tables(self) -> bool:
        result = (self.create_town_table()
                  & self.create_landmark_table()
                  & self.create_fact_table()
                  & self.create_user_table()
                  & self.create_quiz_theme_table()
                  & self.create_quiz_table()
                  & self.create_quiz_ask_table()
                  & self.create_user_quiz_table()
                  & self.create_event_type_table()
                  & self.create_event_table()
                  & self.create_event_group_table()
                  & self.create_participants_table()
                  & self.create_trip_table()
                  & self.create_trip_stage_table()
                  & self.create_stage_element_table()
                  )
        return result

    def drop_table(self, table_title: str):
        request = f"DROP TABLE {self.DATABASE_NAME}.{table_title}"
        with self.con.cursor() as cur:
            cur.execute(request)
            self.con.commit()
        print("ok")

    def drop_all_tables(self) -> bool:
        try:
            for elem in self.drop_tables:
                self.drop_table(elem)
            return True
        except Exception as ex:
            print(ex)
            return False

    def set_new_data(self,
                     request: str,
                     record: list) -> bool:
        try:
            with self.con.cursor() as cur:
                cur.executemany(request, record)
                self.con.commit()
            return True
        except Exception as ex:
            print(ex)
            return False

    def set_new_data_2(self, request: str) -> bool:
        try:
            with self.con.cursor() as cur:
                cur.execute(request)
                self.con.commit()
            return True
        except Exception as ex:
            print(ex)
            return False

    # def get_data(self, request: str):
    #     result = self.con.cursor().

    def set_new_town(self,
                     title: str,
                     language: str) -> bool:
        table = "town"
        request = f"INSERT INTO {self.DATABASE_NAME}.{table} (title, language) " \
                  "VALUES (%s, %s);"
        record = [(title, language)]
        return self.set_new_data(request=request, record=record)

    def set_new_landmark(self,
                         town_id: int,
                         title: str,
                         image_id: str,
                         language: str) -> bool:
        table = "landmark"
        request = f"INSERT INTO {self.DATABASE_NAME}.{table} (town_id, title, image_id, language) " \
                  "VALUES (%s, %s, %s, %s);"
        record = [(town_id, title, image_id, language)]
        return self.set_new_data(request=request, record=record)

    def set_new_fact(self,
                     landmark_id: int,
                     title: str,
                     text: str,
                     audio_id: str,
                     image_id: str,
                     language: str) -> bool:
        table = "fact"
        request = f"INSERT INTO {self.DATABASE_NAME}.{table} (landmark_id, title, text, audio_id, image_id, language) " \
                  "VALUES (%s, %s, %s, %s, %s, %s);"
        record = [(landmark_id, title, text, audio_id, image_id, language)]
        return self.set_new_data(request=request, record=record)

    def set_new_user(self,
                     name: str,
                     user_id: str,
                     ) -> bool:
        table = "user"
        request = f"INSERT INTO {self.DATABASE_NAME}.{table} (name, user_id, status, quiz_score) " \
                  "VALUES (%s, %s, %s, %s);"
        record = [(name, user_id, "base", 0)]
        return self.set_new_data(request=request, record=record)

    def set_new_quiz_theme(self,
                           title: str,
                           description: str,
                           language: str, ) -> bool:
        table = "quiz_theme"
        request = f"INSERT INTO {self.DATABASE_NAME}.{table} (title, description, language) " \
                  "VALUES (%s, %s, %s);"
        record = [(title, description, language)]
        return self.set_new_data(request=request, record=record)

    def set_new_quiz(self,
                     theme_id: int,
                     title: str,
                     description: str,
                     language: str) -> bool:
        table = "quiz"
        request = f"INSERT INTO {self.DATABASE_NAME}.{table} (theme_id, title, description, language) " \
                  "VALUES (%s, %s, %s, %s);"
        record = [(theme_id, title, description, language)]
        return self.set_new_data(request=request, record=record)

    def set_new_quiz_ask(self,
                         quiz_id: int,
                         quiz_ask: str,
                         t_q: str,
                         f_q1: str,
                         f_q2: str,
                         f_q3: str,
                         language: str,
                         image_id: str = None,
                         big_answer: str = "no") -> bool:
        table = "quiz_ask"
        image_id = image_id if image_id else BASE_IMAGE_ID
        request = f"INSERT INTO {self.DATABASE_NAME}.{table} (quiz_id, ask, t_q, f_q1, f_q2, f_q3, image_id, big_answer, language) " \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
        record = [(quiz_id, quiz_ask, t_q, f_q1, f_q2, f_q3, image_id, big_answer, language)]
        return self.set_new_data(request=request, record=record)

    def set_new_user_quiz(self,
                          user_id: int,
                          quiz_id: int,
                          language: str) -> bool:
        table = "user_quiz"
        request = f"INSERT INTO {self.DATABASE_NAME}.{table} (user_id, quiz_id, score, language) " \
                  "VALUES (%s, %s, %s, %s);"
        record = [(user_id, quiz_id, 0, language)]
        return self.set_new_data(request=request, record=record)

    def set_new_event_type(self,
                           title: str,
                           description: str,
                           language: str) -> bool:
        table = "event_type"
        request = f"INSERT INTO {self.DATABASE_NAME}.{table} (title, description, language) VALUES " \
                  f"('{title}', '{description}', '{language}');"
        result = self.set_new_data_2(request=request)
        return result

    def set_new_event(self,
                      title: str,
                      description: str,
                      town_id: int,
                      event_type_id: int,
                      language: str) -> bool:
        table = "event"
        request = f"INSERT INTO {self.DATABASE_NAME}.{table} (title, description, town_id, event_type_id, language) VALUES " \
                  f"('{title}', '{description}', '{town_id}', '{event_type_id}', '{language}');"
        result = self.set_new_data_2(request=request)
        return result

    def set_new_event_group(self,
                            count_place: int,
                            guide_name: str,
                            event_id: int,
                            description: str,
                            local_info: str,
                            language: str) -> bool:
        table = "event_group"
        request = f"INSERT INTO {self.DATABASE_NAME}.{table} (count_place, guide_name, event_id, description, language, local_info) VALUES " \
                  f"('{count_place}', '{guide_name}', '{event_id}', '{description}', '{language}', '{local_info}');"
        result = self.set_new_data_2(request=request)
        return result

    def set_new_participant(self,
                            group_id: int,
                            user_id: int,
                            language: str
                            ) -> bool:
        table = "participants"
        request = f"INSERT INTO {self.DATABASE_NAME}.{table} (group_id, user_id, language) VALUES " \
                  f"('{group_id}', '{user_id}', '{language}');"
        result = self.set_new_data_2(request=request)
        return result

    def set_new_trip(self,
                     town_id: int,
                     title: str,
                     description: str,
                     language: str
                     ) -> bool:
        table = "trip"
        request = f"INSERT INTO {self.DATABASE_NAME}.{table} (town_id, title, description, language) VALUES " \
                  f"('{town_id}', '{title}', '{description}', '{language}');"
        result = self.set_new_data_2(request=request)
        return result

    def set_new_trip_stage(self,
                           trip_id: int,
                           title: str,
                           description: str,
                           language: str
                           ) -> bool:
        table1, table2 = "trip_stage", "trip"
        request = f"SELECT COUNT(*) as count FROM {self.DATABASE_NAME}.{table1} WHERE trip_id = '{trip_id}';"
        num_elem = self.get_info(request=request)[0]["count"] + 1
        request = f"INSERT INTO {self.DATABASE_NAME}.{table1} (trip_id, title, description, num_stage, language) VALUES " \
                  f"('{trip_id}', '{title}', '{description}', '{num_elem}', '{language}');"
        result = self.set_new_data_2(request=request)
        if result:
            request = f"UPDATE {self.DATABASE_NAME}.{table2} SET count_stages = '{num_elem}';"
            self.set_new_data_2(request=request)
        return result

    def set_new_stage_element(self,
                              trip_stage_id: int,
                              title: str,
                              description: str,
                              language: str,
                              image_link: str,
                              audio_link: str,
                              ) -> bool:
        table1, table2 = "stage_element", "trip_stage"
        request = f"SELECT COUNT(*) as count FROM {self.DATABASE_NAME}.{table1} WHERE trip_stage_id = '{trip_stage_id}';"
        num_elem = self.get_info(request=request)[0]["count"] + 1
        request = f"INSERT INTO {self.DATABASE_NAME}.{table1} (trip_stage_id, title, image_link, audio_link, description, num_elem, language) VALUES " \
                  f"('{trip_stage_id}', '{title}', '{image_link}', '{audio_link}', '{description}', '{num_elem}', '{language}');"
        result = self.set_new_data_2(request=request)
        res2 = False
        if result:
            request = f"UPDATE {self.DATABASE_NAME}.{table2} SET count_elem = '{num_elem}' WHERE id = '{trip_stage_id}';"
            res2 = self.set_new_data_2(request=request)
        return res2

    def get_info(self, request: str) -> list:
        with self.con.cursor() as cur:
            cur.execute(request)
            return cur.fetchall()

    def execute_request(self, request: str) -> bool:
        try:
            with self.con.cursor() as cur:
                cur.execute(request)
                self.con.commit()
            return True
        except Exception:
            return False

    def exist_elem(self, request: str) -> bool:
        with self.con.cursor() as cur:
            cur.execute(request)
            return len(cur.fetchall()) > 0

    def exist_user_quiz(self, user_id: int, quiz_id: int) -> [bool, int, int]:
        table = "user_quiz"
        request = f"SELECT * FROM {self.DATABASE_NAME}.{table} WHERE user_id = '{user_id}' AND quiz_id = '{quiz_id}';"
        with self.con.cursor() as cur:
            cur.execute(request)
            response = cur.fetchall()
            if len(response) > 0:
                return [True, response[0]["id"], response[0]["score"]]
            else:
                return [False, -1]

    def set_score_user_quiz(self, user_id: int, quiz_id: int, score: int):
        table = "user_quiz"
        result = self.exist_user_quiz(user_id=user_id, quiz_id=quiz_id)
        if result[0]:
            user_score = result[2] + score
            request = f"UPDATE {self.DATABASE_NAME}.{table} SET score='{user_score}' WHERE id = '{result[1]}';"
            result_2 = self.execute_request(request)
        else:
            self.set_new_user_quiz(user_id=user_id, quiz_id=quiz_id, language="ru")

    ## Wrong function
    def get_data(self, table_title: str) -> str:
        request = f"SELECT * FROM {self.DATABASE_NAME}.{table_title};"
        return str(self.get_info(request))

    def get_all_data(self) -> str:
        text = ""
        for title in self.table_title:
            text += self.get_data(title) + "\n\n"
        return text

    def get_user_data(self):
        table = "user"
        request = f"SELECT * FROM {self.DATABASE_NAME}.{table};"
        return str(self.get_info(request))

    def get_user_quiz_data(self):
        table = "user_quiz"
        request = f"SELECT * FROM {self.DATABASE_NAME}.{table};"
        return str(self.get_info(request))

    #################
    # Program for program work
    #################

    def user_exist(self, user_id: str) -> bool:
        table = "user"
        request = f"SELECT id FROM {self.DATABASE_NAME}.{table} where user_id = '{user_id}';"
        return self.exist_elem(request=request)

    def set_new_admin(self, user_id: str) -> bool:
        table = "user"
        request = f"UPDATE {self.DATABASE_NAME}.{table} SET status = 'admin' WHERE user_id = '{user_id}';"
        return self.execute_request(request=request)

    def town_exist(self, town_title: str) -> bool:
        table = "town"
        request = f"SELECT id FROM {self.DATABASE_NAME}.{table} WHERE title = '{town_title}';"
        return self.exist_elem(request=request)

    def landmark_exist(self, landmark_title: str, town_id: int) -> bool:
        table = "landmark"
        request = f"SELECT id FROM {self.DATABASE_NAME}.{table} WHERE title = '{landmark_title}' AND town_id = '{town_id}';"
        return self.exist_elem(request=request)

    def fact_exist(self, fact_title: str, landmark_id: int) -> bool:
        table = "fact"
        request = f"SELECT id FROM {self.DATABASE_NAME}.{table} " \
                  f"WHERE title = '{fact_title}' AND landmark_id = '{landmark_id}';"
        return self.exist_elem(request=request)

    def user_quiz_exist(self, user_id: str, quiz_id: int) -> bool:
        user_id = self.get_user_id(user_id=user_id)
        table = "user_quiz"
        request = f"SELECT id FROM {self.DATABASE_NAME}.{table} " \
                  f"WHERE user_id = '{user_id}' AND quiz_id = '{quiz_id}';"
        return self.exist_elem(request=request)

    def get_all_town_title(self) -> list:
        table = "town"
        request = f"SELECT title FROM {self.DATABASE_NAME}.{table};"
        data = [elem["title"] for elem in self.get_info(request)]
        return [len(data) > 0, data]

    def get_all_landmark_by_town_id(self, town_id: int) -> list:
        table = "landmark"
        request = f"SELECT title FROM {self.DATABASE_NAME}.{table} WHERE town_id = '{town_id}';"
        data = [elem["title"] for elem in self.get_info(request)]
        return [len(data) > 0, data]

    def get_town_id(self, town_title: str) -> int:
        table = "town"
        request = f"SELECT id FROM {self.DATABASE_NAME}.{table} WHERE title = '{town_title}';"
        return self.get_info(request)[0]["id"]

    def get_landmark_id(self, town_id: int, landmark_title: str) -> int:
        table = "landmark"
        request = f"SELECT id FROM {self.DATABASE_NAME}.{table} " \
                  f"WHERE title = '{landmark_title}' AND town_id = '{town_id}';"
        return self.get_info(request)[0]["id"]

    def get_quiz_theme_list(self, user_lang: str) -> [bool, list]:
        table = "quiz_theme"
        request = f"SELECT title FROM {self.DATABASE_NAME}.{table} WHERE language = '{user_lang}';"
        data = [elem["title"] for elem in self.get_info(request)]
        return [len(data) > 0, data]

    def get_quiz_list(self, theme_id: int) -> list:
        table = "quiz"
        request = f"SELECT title FROM {self.DATABASE_NAME}.{table} WHERE theme_id = '{theme_id}' AND enabled = '1';"
        data = [elem["title"] for elem in self.get_info(request)]
        return [len(data) > 0, data]

    def get_quiz_theme_id(self, theme_title: str) -> int:
        table = "quiz_theme"
        request = f"SELECT id FROM {self.DATABASE_NAME}.{table} WHERE title = '{theme_title}';"
        return self.get_info(request)[0]["id"]

    def get_quiz_id(self, theme_title: str) -> int:
        table = "quiz"
        request = f"SELECT id FROM {self.DATABASE_NAME}.{table} WHERE title = '{theme_title}';"
        return self.get_info(request)[0]["id"]

    def get_quiz_title(self, quiz_id: int) -> str:
        table = "quiz"
        request = f"SELECT title FROM {self.DATABASE_NAME}.{table} WHERE id = '{quiz_id}';"
        return self.get_info(request)[0]["title"]

    def get_user_id(self, user_id: str) -> int:
        table = "user"
        request = f"SELECT id FROM {self.DATABASE_NAME}.{table} WHERE user_id = '{user_id}';"
        return self.get_info(request)[0]["id"]

    def get_quiz_ask(self, quiz_id: int, ask_id: list) -> [bool, dict]:
        table = "quiz_ask"
        request = f"SELECT * FROM {self.DATABASE_NAME}.{table} WHERE quiz_id = '{quiz_id}';"
        data = self.get_info(request)
        index_ask = len(ask_id)
        return [True, data[index_ask]] if index_ask != len(data) else [False, dict()]

    def get_statistics(self, user_id: int, user_lang: str) -> str:
        table = "user_quiz"
        total_score = 0
        msg_back = f"{languages[user_lang]['stat_start']}\n"
        request = f"SELECT * FROM {self.DATABASE_NAME}.{table} WHERE user_id = '{user_id}';"
        for elem in self.get_info(request):
            quiz_title = self.get_quiz_title(elem["quiz_id"])
            msg_back += f"{languages[user_lang]['stat_1_step']}'{quiz_title}'" \
                        f"{languages[user_lang]['stat_2_step']}{elem['score']}{languages[user_lang]['stat_3_step']}\n"
            total_score += elem['score']
        msg_back += f"{languages[user_lang]['stat_total']}{total_score}."
        return msg_back

    def get_ask_id_list(self, quiz_id: int) -> list:
        table = "quiz_ask"
        request = f"SELECT id FROM {self.DATABASE_NAME}.{table} WHERE quiz_id = '{quiz_id}';"
        data = self.get_info(request)
        ask_id_list = list()
        for elem in data:
            ask_id_list.append(elem["id"])
        return ask_id_list

    def get_random_ask(self, quiz_id: int, ask_id_ready: list) -> [bool, dict]:
        table = "quiz_ask"
        ask_id_list = self.get_ask_id_list(quiz_id=quiz_id)
        random_ask_id = random.choice(ask_id_list)
        while random_ask_id in ask_id_ready:
            random_ask_id = random.choice(ask_id_list)
        request = f"SELECT * FROM {self.DATABASE_NAME}.{table} WHERE id = '{random_ask_id}';"
        data = self.get_info(request)[0]
        return data

    def get_user_lang(self, user_id: str) -> str:
        table = "user"
        request = f"SELECT language FROM {self.DATABASE_NAME}.{table} WHERE user_id = '{user_id}';"
        data = self.get_info(request=request)[0]["language"]
        return data

    def change_user_lang(self, user_id: str, new_lang: str) -> bool:
        table = "user"
        request = f"UPDATE {self.DATABASE_NAME}.{table} SET language='{new_lang}' WHERE user_id = '{user_id}';"
        return self.execute_request(request=request)

    ####################################
    #
    # NEW VARIATION
    #
    ####################################

    def get_list_btn(self, request: str, key: str = "title") -> list:
        with self.con.cursor() as cur:
            cur.execute(request)
            result = cur.fetchall()
        btn_list = list()
        for elem in result:
            btn_list.append(elem[key])
        return btn_list

    def get_element_id(self, request: str) -> int:
        with self.con.cursor() as cur:
            cur.execute(request)
            result = cur.fetchall()[0]
        return result["id"]

    def get_element_info(self, request: str) -> dict:
        with self.con.cursor() as cur:
            cur.execute(request)
            result = cur.fetchall()[0]
        return result

    def get_event_type_btn(self, language: str = "en") -> list:
        table = "event_type"
        request = f"SELECT title FROM {self.DATABASE_NAME}.{table} WHERE language = '{language}';"
        return self.get_list_btn(request=request)

    def get_event_btn(self, event_type_id: int, town_id: int, language: str = "en") -> list:
        table = "event"
        request = f"SELECT title FROM {self.DATABASE_NAME}.{table} WHERE event_type_id = '{event_type_id}' AND " \
                  f"town_id ='{town_id}' AND language = '{language}';"
        return self.get_list_btn(request=request)

    def get_event_group_btn(self, event_id: int, language: str = "en") -> list:
        table = "event_group"
        key = "guide_name"
        request = f"SELECT {key} FROM {self.DATABASE_NAME}.{table} WHERE event_id = '{event_id}'" \
                  f" AND language = '{language}';"
        return self.get_list_btn(request=request, key=key)

    def get_trip_btn(self, town_id: int, language: str = "en") -> list:
        table = "trip"
        request = f"SELECT title FROM {self.DATABASE_NAME}.{table} WHERE " \
                  f"town_id ='{town_id}' AND language = '{language}';"
        return self.get_list_btn(request=request)

    def get_trip_stage_btn(self, trip_id: int, language: str = "en") -> list:
        table = "trip_stage"
        request = f"SELECT title FROM {self.DATABASE_NAME}.{table} WHERE trip_id = '{trip_id}'" \
                  f" AND language = '{language}';"
        return self.get_list_btn(request=request)

    def get_list_participants(self, group_id: int, language: str = "en") -> list:
        table_1, table_2 = "user", "participants"
        key = "name"
        request = f"SELECT CONCAT(a.name, ':', b.id) as name FROM {self.DATABASE_NAME}.{table_1} as a " \
                  f"INNER JOIN {self.DATABASE_NAME}.{table_2} as b " \
                  f"ON b.user_id = a.id " \
                  f"WHERE group_id = '{group_id}';"
        return self.get_list_btn(request=request, key=key)

    def get_event_type_id(self, title: str, language: str = "en") -> int:
        table = "event_type"
        request = f"SELECT id FROM {self.DATABASE_NAME}.{table} WHERE title = '{title}';"
        return self.get_element_id(request=request)

    def get_event_id(self, title: str, event_type_id: int, language: str = "en") -> int:
        table = "event"
        request = f"SELECT id FROM {self.DATABASE_NAME}.{table} WHERE title = '{title}' AND " \
                  f"event_type_id = '{event_type_id}' AND language = '{language}';"
        return self.get_element_id(request=request)

    def get_event_group_id(self, guide_name: str, event_id: int, language: str = "en") -> int:
        table = "event_group"
        request = f"SELECT id FROM {self.DATABASE_NAME}.{table} WHERE guide_name = '{guide_name}' AND " \
                  f"event_id = '{event_id}' AND language = '{language}';"
        return self.get_element_id(request=request)

    def get_participants_id(self, guide_name: str, event_id: int, language: str = "en") -> int:
        table = "event_group"
        request = f"SELECT id FROM {self.DATABASE_NAME}.{table} WHERE guide_name = '{guide_name}' AND " \
                  f"event_id = '{event_id}' AND language = '{language}';"
        return self.get_element_id(request=request)

    def get_trip_id(self, title: str, language: str = "ru") -> int:
        table = "trip"
        request = f"SELECT id FROM {self.DATABASE_NAME}.{table} WHERE title = '{title}'" \
                  f" AND language = '{language}';"
        return self.get_element_id(request=request)

    def get_trip_stage_id(self, title: str, trip_id: int, num: int, language: str = "en") -> int:
        table = "trip_stage"
        print(title, trip_id, num, language)
        request = f"SELECT id FROM {self.DATABASE_NAME}.{table} WHERE title = '{title}' AND " \
                  f"trip_id = {trip_id} AND language = '{language}';"
        print(request)
        result = self.get_element_id(request=request)
        print(result)
        return self.get_element_id(request=request)

    def get_trip_stage_id_2(self, title: str, trip_id: int, language: str = "en") -> int:
        table = "trip_stage"
        request = f"SELECT id FROM {self.DATABASE_NAME}.{table} WHERE title = '{title}' AND " \
                  f"trip_id = {trip_id} AND language = '{language}';"
        return self.get_element_id(request=request)

    def get_event_type_info(self, event_type_id: int,language: str = "en") -> dict:
        table = "event_type"
        request = f"SELECT * FROM {self.DATABASE_NAME}.{table} WHERE id = '{event_type_id}'" \
                  f" AND language = '{language}';"
        return self.get_element_info(request=request)

    def get_event_info(self, event_id: int, language: str = "en") -> dict:
        table = "event"
        request = f"SELECT * FROM {self.DATABASE_NAME}.{table} WHERE id = '{event_id}'" \
                  f" AND language = '{language}';"
        return self.get_element_info(request=request)

    def get_event_group_info(self, event_group_id: int, language: str = "en") -> dict:
        table = "event_group"
        request = f"SELECT * FROM {self.DATABASE_NAME}.{table} WHERE id = '{event_group_id}'" \
                  f" AND language = '{language}';"
        return self.get_element_info(request=request)

    def get_participants_info(self, participant_id: int) -> dict:
        table_1, table_2 = "participants", "user"
        request = f"SELECT * FROM {self.DATABASE_NAME}.{table_1} as a " \
                  f"INNER JOIN {self.DATABASE_NAME}.{table_2} as b " \
                  f"ON a.user_id = b.id WHERE a.id = '{participant_id}';"
        return self.get_element_info(request=request)

    def get_trip_info(self, trip_id: int, language: str = "en") -> dict:
        table = "trip"
        request = f"SELECT * FROM {self.DATABASE_NAME}.{table} WHERE id = '{trip_id}'" \
                  f" AND language = '{language}';"
        return self.get_element_info(request=request)

    def get_trip_stage_info(self, trip_stage_id: int, num: int, language: str = "en") -> dict:
        table = "trip_stage"
        request = f"SELECT * FROM {self.DATABASE_NAME}.{table} WHERE id = '{trip_stage_id}'" \
                  f" AND language = '{language}';"
        return self.get_element_info(request=request)

    def get_stage_element_info(self, trip_stage_id: int, num_elem: int, language: str = "en") -> dict:
        table = "stage_element"
        request = f"SELECT * FROM {self.DATABASE_NAME}.{table} WHERE trip_stage_id = '{trip_stage_id}' AND " \
                  f"num_elem = '{num_elem}' AND language = '{language}';"
        return self.get_element_info(request=request)

    def get_count_participants(self, group_id: int) -> int:
        table_1, table_2 = "user", "participants"
        key = "count"
        request = f"SELECT COUNT(a.name) as count FROM {self.DATABASE_NAME}.{table_1} as a " \
                  f"INNER JOIN {self.DATABASE_NAME}.{table_2} as b " \
                  f"ON b.user_id = a.id " \
                  f"WHERE group_id = '{group_id}';"
        return self.get_element_info(request=request)[key]


"""
Needed functions:
set_new_user
set_new_town
set_new_landmark
set_new_fact
"""
