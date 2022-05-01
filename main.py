from random import randrange
import sqlalchemy
import vk_api
import jconfig
from vk_api.longpoll import VkLongPoll, VkEventType
from database import vkinderdatabase
from datetime import date
from config import group_token,  personal_token
from vk_api.vk_api import VkApi
from vk_api.enums import VkUserPermissions
from vk_api.vk_api import DEFAULT_USER_SCOPE
from vk_api.exceptions import ApiError
from sqlalchemy.exc import OperationalError

vk_group = VkApi(token=group_token)
longpoll = VkLongPoll(vk_group)




class VKbot(VkApi):
    def __init__(self,vkinder_item, longpoll, login=None, password=None, token=None,
                 auth_handler=None, captcha_handler=None,
                 config=jconfig.Config, config_filename='vk_config.v2.json',
                 api_version='5.92', app_id=6222115, scope=DEFAULT_USER_SCOPE,
                 client_secret=None, session=None):
        super().__init__( login, password, token,
                 auth_handler, captcha_handler,
                 config, config_filename,
                 api_version, app_id, scope,
                 client_secret, session)
        self.longpoll = longpoll
        self.vkinder_item = vkinder_item

        """ vkinder_item - экземпляр класса Vkinder
        
            longpoll - экземпляр класса VkLongPoll
            """

    def write_msg(self, user_id, message, owner_id=None, media_id=None):
        self.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),
                                            'attachment': f"photo{owner_id}_{media_id}"})
    def chat_bot_(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:

                if event.to_me:
                    request = event.text

                    if request == "привет":
                        self.write_msg(event.user_id, f"Хай, {event.user_id}, найти тебе пару?")

                        for event in self.longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW:

                                if event.to_me:
                                    request = event.text

                                    if request == "да":

                                        self.write_msg(event.user_id, f"ищу...")
                                        self.vkinder_item.search(event.user_id)
                                        print(self.vkinder_item.city_id)
                                        print(self.vkinder_item.bdate)

                                        if self.vkinder_item.city_id == None:
                                            self.write_msg(event.user_id, f"В каком городе ты живешь?")
                                            for event in self.longpoll.listen():
                                                if event.type == VkEventType.MESSAGE_NEW:

                                                    if event.to_me:
                                                        request = event.text
                                                        self.vkinder_item.city_id = self.vkinder_item.find_city_id(request)

                                                        break
                                        if self.vkinder_item.bdate == None:
                                            self.write_msg(event.user_id, f"Напиши год рождения")
                                            for event in self.longpoll.listen():
                                                if event.type == VkEventType.MESSAGE_NEW:
                                                    if event.to_me:
                                                        request = event.text
                                                        self.vkinder_item.bdate = request

                                                        break
                                        while True:

                                            chat_search = self.vkinder_item.chat_search(event.user_id)

                                            self.write_msg(event.user_id,
                                                            f"{chat_search['person']['first_name']} http://vk.com/id{chat_search['person']['id']}")
                                            for photo in self.vkinder_item.sort_best_photo(chat_search['res']['items']):
                                                self.write_msg(event.user_id, f" ", chat_search['person']['id'], photo[0])
                                            self.write_msg(event.user_id, f"ищем дальше?")

                                            for event in self.longpoll.listen():
                                                if event.type == VkEventType.MESSAGE_NEW:

                                                    if event.to_me:
                                                        request = event.text
                                                        break
                                            if request == "нет":
                                                self.write_msg(event.user_id, f"Пока((")
                                                break
                                        break
                                    else:
                                        self.write_msg(event.user_id, f"Пока((")
                                        break

                    elif request == "пока":
                        self.write_msg(event.user_id, "Пока((")
                    else:
                        self.write_msg(event.user_id, "Не поняла вашего ответа...")


class VKinder(VkApi):
    def __init__(self, database_item, login=None, password=None, token=None,
                 auth_handler=None, captcha_handler=None,
                 config=jconfig.Config, config_filename='vk_config.v2.json',
                 api_version='5.92', app_id=6222115, scope=DEFAULT_USER_SCOPE,
                 client_secret=None, session=None):
        super().__init__( login, password, token,
                 auth_handler, captcha_handler,
                 config, config_filename,
                 api_version, app_id, scope,
                 client_secret, session)
        self.city_id = None
        self.sex = None
        self.bdate = None
        self.database_item = database_item

        """ database_item - экземпляр класса Vkinder_Database модуля database.py
                    """

    #  Определяем пол, год рождения, город, для кого будем искать пару
    def search(self, user_id):
        response = self.method('users.get', {'user_ids': user_id, 'fields': 'city,sex,bdate,relation'})
        if response[0].get('city') != None:
            self.city_id = response[0].get('city').get('id')
        self.sex = response[0].get('sex')
        if response[0].get('bdate') != None:
            _bdate= response[0].get('bdate')
            _bdate_list = list(_bdate.split('.'))
            self.bdate = int(_bdate_list[-1])
        return self.method('users.get', {'user_ids': user_id, 'fields': 'city,sex,bdate,relation'})
    #  Метод определения id города
    def find_city_id(self, city_input):
        response = vk_service.method('database.getCities', {'country_id': '1', 'q': city_input, 'count':1})
        return response.get('items')[0].get('id')
    # Метод поиска пары
    def find_person(self):
        sex_accordance = { 1 : 2 , 2 : 1 }
        self._age_from = date.today().year - int(self.bdate) - 5
        self._age_to = date.today().year - int(self.bdate) + 5
        response = self.method('users.search', {'city': self.city_id, 'sex': sex_accordance[self.sex],
                                                       'offset': randrange(1,999,1), 'count': '1' , 'has_photo':
                                                           '1', 'status' : randrange(1,7,5), 'age_from': self._age_from,
                                                       'age_to': self._age_to})
        return response.get('items')
    # Метод получения фотографий
    def best_photos(self, id):
        response = self.method('photos.get', {'owner_id': id, 'album_id': 'profile', 'extended': 1})
        return response
    # Метод получения 3 лучших фото
    def sort_best_photo(self, income_list):
        unsorted_dict = {}
        for photo in income_list:
            unsorted_dict[photo['id']] = photo['comments']['count'] + photo['likes']['count']
        sorted_tuple = sorted(unsorted_dict.items(), key=lambda x: x[1])
        sorted_tuple.reverse()
        photo_tuple_list = []
        for photo_tuple in sorted_tuple:
            if len(photo_tuple_list) < 3:
                photo_tuple_list.append(photo_tuple)
            else:
                break
        return photo_tuple_list
    # Поиск пары и вывод фото в чат
    def chat_search(self, my_id):
        if self.database_item != None:
            while True:
                try:
                    person = self.find_person()[0]
                    res = self.best_photos(person['id'])
                    self.database_item.match_check(my_id, person['id'])
                    self.database_item.insert_table(my_id, person['id'])
                    break
                except IndexError:
                    print('профиль не найден, пробуем найти с другими параметрами...')
                    continue
                except vk_api.exceptions.ApiError:
                    print('профиль закрыт, пробуем найти другой профиль...')
                    continue
                except ValueError:
                    print('уже была данная пара, подбираем другую...')
                    continue
                except sqlalchemy.exc.OperationalError:
                    print('потеря связи с базой...возможны повторы, пока связь не восстановится')
                    break

            result_dict = { 'person': person, 'res' : res }
            return result_dict
        if self.database_item == None:
            print('Возможны повторы, нет подключения к базе...')
            while True:
                try:
                    person = self.find_person()[0]
                    res = self.best_photos(person['id'])

                    break
                except IndexError:
                    print('профиль не найден, пробуем найти с другими параметрами...')
                    continue
                except vk_api.exceptions.ApiError:
                    print('профиль закрыт, пробуем найти другой профиль...')
                    continue
            result_dict = {'person': person, 'res': res}
            return result_dict

if __name__ == '__main__':

    # Создаем экземпляр класса Vkinder. Передаем в инициализацию экземпляр класса Vkinder_database и личный токен
    vkinder = VKinder(vkinderdatabase, token=personal_token)
    # Создаем экземпляр класса Vkbot. Передаем в инициализацию экземпляр класса Vkinder и VKlongpoll
    vkbot = VKbot(vkinder, longpoll, token=group_token)

    vkbot.chat_bot_()






