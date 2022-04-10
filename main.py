from random import randrange
from pprint import pprint
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from database import vkinderdatabase
from datetime import date

group_token = "692afe0615ae2320f33250351c6ea1f4fef25f7e2204ada16f56ce89a24e02d647888c61fe392cd10af1e"
service_token = "9a3180f79a3180f79a3180f7f89a4b088199a319a3180f7fb8c794c0851969fce1a6cbb"
personal_token = ''

vk_group = vk_api.VkApi(token=group_token)
vk_service = vk_api.VkApi(token=service_token)
vk_personal = vk_api.VkApi(token=personal_token)
longpoll = VkLongPoll(vk_group)

# Функция отправки сообщения из vl_api
def write_msg(user_id, message, owner_id=None, media_id=None):
    vk_group.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),
                                      'attachment': f"photo{owner_id}_{media_id}"})

class VKinder():
    def __init__(self):
        self.city_id = None
        self.sex = None
        self.bdate = None
    #  Определяем пол, год рождения, город, для кого будем искать пару
    def search(self, user_id):
        response = vk_group.method('users.get', {'user_ids': user_id, 'fields': 'city,sex,bdate,relation'})
        if response[0].get('city') != None:
            self.city_id = response[0].get('city').get('id')
        self.sex = response[0].get('sex')
        if response[0].get('bdate') != None:
            _bdate= response[0].get('bdate')
            _bdate_list = list(_bdate.split('.'))
            self.bdate = int(_bdate_list[-1])
        return vk_group.method('users.get', {'user_ids': user_id, 'fields': 'city,sex,bdate,relation'})
    #  Метод определения id города
    def find_city_id(self, city_input):
        response = vk_service.method('database.getCities', {'country_id': '1', 'q': city_input, 'count':1})
        return response.get('items')[0].get('id')
    # Метод поиска пары
    def find_person(self):
        sex_accordance = { 1 : 2 , 2 : 1 }
        self._age_from = date.today().year - int(self.bdate) - 5
        self._age_to = date.today().year - int(self.bdate) + 5
        response = vk_personal.method('users.search', {'city': self.city_id, 'sex': sex_accordance[self.sex],
                                                       'offset': randrange(1,999,1), 'count': '1' , 'has_photo':
                                                           '1', 'status' : randrange(1,7,5), 'age_from': self._age_from,
                                                       'age_to': self._age_to})
        return response.get('items')
    # Метод получения фотографий
    def best_photos(self, id):
        response = vk_personal.method('photos.get', {'owner_id': id, 'album_id': 'profile', 'extended': 1})
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
    def chat_search(self):
        while True:
            try:
                person = self.find_person()[0]
                res = self.best_photos(person['id'])
                vkinderdatabase.match_check(event.user_id, person['id'])
                vkinderdatabase.insert_table(event.user_id, person['id'])
                break
            except:
                continue

        write_msg(event.user_id, f"{person['first_name']} http://vk.com/id{person['id']}")
        for photo in self.sort_best_photo(res['items']):
            write_msg(event.user_id, f" ", person['id'], photo[0])
        write_msg(event.user_id, f"ищем дальше?")

vkinder = VKinder()

if __name__ == '__main__':

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:

            if event.to_me:
                request = event.text

                if request == "привет":
                    write_msg(event.user_id, f"Хай, {event.user_id}, найти тебе пару?")

                    for event in longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW:

                            if event.to_me:
                                request = event.text

                                if request == "да":
                                    pprint(vkinder.bdate)
                                    pprint(vkinder.sex)
                                    pprint(vkinder.city_id)
                                    write_msg(event.user_id, f"ищу...")
                                    vkinder.search(event.user_id)
                                    pprint(vkinder.bdate)
                                    pprint(vkinder.sex)
                                    pprint(vkinder.city_id)

                                    if vkinder.city_id == None:
                                        write_msg(event.user_id, f"В каком городе ты живешь?")
                                        for event in longpoll.listen():
                                            if event.type == VkEventType.MESSAGE_NEW:

                                                if event.to_me:
                                                    request = event.text
                                                    vkinder.city_id = vkinder.find_city_id(request)
                                                    pprint(vkinder.bdate)
                                                    pprint(vkinder.sex)
                                                    pprint(vkinder.city_id)
                                                    break
                                    if vkinder.bdate == None:
                                        write_msg(event.user_id, f"Напиши год рождения")
                                        for event in longpoll.listen():
                                            if event.type == VkEventType.MESSAGE_NEW:
                                                if event.to_me:
                                                    request = event.text
                                                    vkinder.bdate = request
                                                    pprint(vkinder.bdate)
                                                    pprint(vkinder.sex)
                                                    pprint(vkinder.city_id)
                                                    break
                                    while True:
                                        print('ввввв')
                                        vkinder.chat_search()
                                        print(vkinder._age_from)
                                        print(vkinder._age_to)
                                        for event in longpoll.listen():
                                            if event.type == VkEventType.MESSAGE_NEW:

                                                if event.to_me:
                                                    request = event.text
                                                    break
                                        if request == "нет":
                                            write_msg(event.user_id, f"Пока((")
                                            break
                                    break
                                else:
                                    write_msg(event.user_id, f"Пока((")
                                    break

                elif request == "пока":
                    write_msg(event.user_id, "Пока((")
                else:
                    write_msg(event.user_id, "Не поняла вашего ответа...")








