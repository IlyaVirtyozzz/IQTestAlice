from flask import Flask, request
from functions import *
import logging, time, json, random, copy

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, filename='/home/IlyaVirtyozzz/mysite/app.log',
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')

with open("/home/IlyaVirtyozzz/mysite/info.json", "r", ) as read_file:
    info_i = json.load(read_file)

sessionStorage = {}


@app.route('/', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Request: %r', response)
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    res['response']['buttons'] = []

    if req['session']['new']:
        res['response']['text'] = \
            'Привет! Здесь можно проверить свой IQ!'
        res['response']['buttons'].extend(info_i["buttons"]['mainmenu'])
        sessionStorage[user_id] = {
            'steps': 0  # 0-главное меню, 1-помощь, 2-тест
        }
        return
    if sessionStorage[user_id]['steps'] == 0:
        if 'помощь' in list(map(lambda x: x.lower(), req['request']['nlu']["tokens"])):
            sessionStorage[user_id]['steps'] = 1  # переходим в "Помощь"
            res['response']['text'] = 'Выберите что-хотите узнать'
            res['response']['buttons'].extend(info_i["buttons"]['infomenu'])
        elif 'начать' in list(map(lambda x: x.lower(), req['request']['nlu']["tokens"])):
            sessionStorage[user_id]['steps'] = 2  # переходим в тестирование
            sessionStorage[user_id]['user_age'] = None  # здесь будет хранится возраст юзера
            sessionStorage[user_id]['attempt'] = 0  # вопрос 1
            sessionStorage[user_id][
                'start_test'] = False  # переходим в впорос но не начинаем его, так как нужно ещё спросить возраст
            sessionStorage[user_id]['percent_true'] = None  # здесь будет храниться результат пользователя в процентах
            sessionStorage[user_id]['iq'] = None  # IQ
            sessionStorage[user_id]['answers'] = list(
                map(lambda x: 0, range(60)))  # создаём список с 0, 0-неправильный ответ, 1-правильный
            res['response']['text'] = 'Приняла. А сколько вам лет? Если не секрет.'
        elif 'выйти' in list(map(lambda x: x.lower(), req['request']['nlu']["tokens"])):
            res['end_session'] = True  # выходим
            res['response']['text'] = 'Пока-пока'
        else:
            res['response']['text'] = \
                random.choice(info_i["dialogs"]["incomprehension"])  # ¯\_(ツ)_/¯
            res['response']['buttons'].extend(info_i["buttons"]['mainmenu'])
        return

    if sessionStorage[user_id]['steps'] == 1:
        info_run(res, req)
    if sessionStorage[user_id]['steps'] == 2:
        test_start(res, req)


def info_run(res, req):
    user_id = req['session']['user_id']
    res['response']['buttons'].extend(info_i["buttons"]['infomenu'])
    if 'краткая' in list(map(lambda x: x.lower(), req['request']['nlu']["tokens"])):
        res['response'][
            'text'] = 'Тест Рейвена включает в себя 60 впросов. Время на решение заданий ограничено 20 минутами.' \
                      ' Расчитан для людей возрастом от 8 до 65 лет. Все результаты приблизительны.'
    elif 'назад' in list(map(lambda x: x.lower(), req['request']['nlu']["tokens"])):
        sessionStorage[user_id]['steps'] = 0  # обратно в меню
        res['response']['buttons'] = info_i["buttons"]['mainmenu']
        res['response']['text'] = 'Привет! Здесь можно проверить свой IQ!'
    elif 'википедии' in list(map(lambda x: x.lower(), req['request']['nlu']["tokens"])):
        res['response']['text'] = "Открываю"  # открываем страницу на википедии
    else:
        res['response']['text'] = random.choice(info_i["dialogs"]["incomprehension"])  # ¯\_(ツ)_/¯


def test_start(res, req):
    user_id = req['session']['user_id']
    attempt = sessionStorage[user_id]['attempt']
    start_test = sessionStorage[user_id]['start_test']

    if sessionStorage[user_id]['user_age'] is None:
        age = get_num(req)
        if age and type(age) is int:
            if 7 < age < 80:
                sessionStorage[user_id]['user_age'] = str(age)
                sessionStorage[user_id]['start_time'] = int(time.time())
                sessionStorage[user_id]['start_test'] = True
                res['response'][
                    'text'] = 'Отправьте любое сообщение чтобы начать. У вас есть 20 минут чтобы ответить на вопросы'
                res['response']['buttons'] = [{"title": "Любое сообщение.", "hide": True}]

            elif not 7 < age < 80:
                res['response']['text'] = 'Брррррррр,введите настоящий возраст'
        else:
            res['response']['text'] = random.choice(info_i["dialogs"]["incomprehension"])  # ¯\_(ツ)_/¯
        return
    else:
        if start_test:
            if attempt == 0:
                sessionStorage[user_id]['start_time'] = int(time.time())  # засекаем время

            if sessionStorage[user_id]['start_time'] - int(time.time() - 1200) < 0:
                res['response']['text'] = 'Упс. Похоже время вышло. '
                end_test(res, user_id)  # заканчиваем тест
                return

            if attempt != 0 and attempt < 60:
                num = get_num(req)
                if num:
                    if 1 <= int(num) <= 8:
                        check_true(attempt, num, user_id)
                    else:
                        if info_i["answers_info"][attempt][2] in 'AB':
                            res['response']['buttons'].extend(info_i["buttons"]['AB'])
                        else:
                            res['response']['buttons'].extend(info_i["buttons"]['CDE'])
                        res['response']['text'] = random.choice(info_i["dialogs"]["incomprehension"])  # ¯\_(ツ)_/¯
                        return
                else:
                    if info_i["answers_info"][attempt][2] in 'AB':
                        res['response']['buttons'].extend(info_i["buttons"]['AB'])
                    else:
                        res['response']['buttons'].extend(info_i["buttons"]['CDE'])
                    res['response']['text'] = random.choice(info_i["dialogs"]["incomprehension"])  # ¯\_(ツ)_/¯
                    return
            if attempt < 60:
                sessionStorage[user_id]['attempt'] += 1
                res['response']['text'] = 'qwerty'
                res['response']['card'] = {
                    "type": "BigImage",
                    "title": "Вопрос: {}/60".format(attempt + 1),  # выводим позицию текущего вопроса
                    "description": "{}".format(
                        random.choice(info_i["dialogs"]["reassurance"]) + "\nОсталось времени: {}мин {}с".format(
                            # время
                            *check_time(sessionStorage[user_id]['start_time'] - int(time.time() - 1200)))),
                    "image_id": info_i["answers_info"][
                        (len(info_i["answers_info"]) + attempt) % len(info_i["answers_info"])][0],
                }
                # в заданиях группы А и Б по 6 возможных вариантов ответов , в С,Д,Е по 8
                if info_i["answers_info"][attempt][2] in 'AB':

                    res['response']['buttons'].extend(info_i["buttons"]['AB'])
                else:
                    res['response']['buttons'].extend(info_i["buttons"]['CDE'])
            else:
                res['response']['text'] = ''
                end_test(res, user_id)


        else:
            res['response']['buttons'] = copy.deepcopy(info_i["buttons"]['aftertest'])  # меню после теста
            res['response']['buttons'][0]['url'] = res['response']['buttons'][0]['url'].format(
                sessionStorage[user_id]['iq'])
            if sessionStorage[user_id]['iq'] == '-':
                res['response']['buttons'] = [{"title": "В главное меню", "hide": True}]
            if 'узнать' in list(
                    map(lambda x: x.lower(), req['request']['nlu']["tokens"])):  # узнать информацию о своём интеллекте
                res['response']['text'] = 'Открываю'
            elif "меню" in list(map(lambda x: x.lower(), req['request']['nlu']["tokens"])):

                sessionStorage[user_id]['steps'] = 0  # переходим в главное меню
                res['response']['buttons'] = info_i["buttons"]['mainmenu']
                res['response']['text'] = 'Привет! Здесь можно проверить свой IQ!'

            else:
                res['response']['text'] = random.choice(info_i["dialogs"]["incomprehension"])  # ¯\_(ツ)_/¯


def check_true(attempt, answer, user_id):
    # проверка на правильность ответа
    if answer == info_i["answers_info"][attempt - 1][1]:
        sessionStorage[user_id]['answers'][attempt - 1] = 1
    else:
        pass


def end_test(res, user_id):
    sessionStorage[user_id]['start_test'] = False
    sessionStorage[user_id]['percent_true'], sessionStorage[user_id]['iq'] = calculate_answer(user_id,
                                                                                              sessionStorage,
                                                                                              info_i)

    if sessionStorage[user_id]['iq'] == '-':
        res['response'][
            'text'] = "Вы выбирали ответы наугад? Это риторический вопрос." \
                      " Пройдите тест ещё раз, выбирайте ответы с умом."
        res['response']['buttons'] = [{"title": "В главное меню", "hide": True}]
        return
    res['response'][
        'text'] += "Вы выполнили этот тест на {} процентов. Это означает что у вас {}." \
                   " Ваш iq примерно составляет... {}. ".format(sessionStorage[user_id]['percent_true'],
                                                                get_info_p(
                                                                    sessionStorage[user_id]['percent_true']),
                                                                sessionStorage[user_id]['iq'] if
                                                                sessionStorage[user_id][
                                                                    'iq'] != '-' else 'Упс... невозможно вычислить')

    res['response']['buttons'] = copy.deepcopy(info_i["buttons"]['aftertest'])
    res['response']['buttons'][0]['url'] = res['response']['buttons'][0]['url'].format(
        sessionStorage[user_id]['iq'])


if __name__ == '__main__':
    app.run()
