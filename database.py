import psycopg2
import sqlalchemy
import sqlalchemy as sq
from sqlalchemy.sql import text
from datetime import date
from sqlalchemy.exc import OperationalError

class Vkinder_Database():

    def __init__(self, url):
        self.url = url
        self.engine = sq.create_engine(url)
        self.connection = self.engine.connect()

    def create_table(self):
        self.connection.execute("""CREATE TABLE IF NOT EXISTS public.matches (
            user_id int4 NOT NULL,
            search_id int4 NOT NULL,
            CONSTRAINT pk PRIMARY KEY (user_id, search_id)
        );
        """)

    def insert_table(self, user_id, search_id):
        s = text ('INSERT INTO public.matches VALUES ( :user_id , :search_id)')
        self.connection.execute(s, user_id = user_id, search_id = search_id)

    def delete_data(self):
        self.connection.execute(text('DELETE FROM public.matches'))

    def match_check(self, user_id, search_id):

        if self.connection.execute(text('SELECT * FROM public.matches WHERE user_id = :user_id AND search_id = :search_id'), user_id= user_id, search_id= search_id).fetchall() != []:
            raise ValueError("This match already exists")

    def _select(self):
       return self.connection.execute(text('SELECT * FROM public.matches')).fetchall()

try:
    vkinderdatabase = Vkinder_Database('postgresql://py47:123456@localhost:5432/course_vkinder')
except sqlalchemy.exc.OperationalError:
    print('Нет подключения к базе данных')
    vkinderdatabase = None



