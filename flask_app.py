from flask import Flask, request
import logging
import json

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, filename='app.log',filemode='w',
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')

with open("info.json", "r", ) as read_file:
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
            'Привет! Как я могу к вам обращаться?'
        res['response']['tts'] = \
            'Привет! Как я могу к вам обращаться?'
        res['response']['buttons'].extend([
            {
                'title': 'На "Вы"',
                'hide': True
            },
            {
                'title': 'На "Ты"',
                'hide': True
            }
        ])
        sessionStorage[user_id] = {
            'user_age': None,
            'game_started': False,
            'official_appeal': None
        }

        return
    if sessionStorage[user_id]['official_appeal'] is None:
        if req['request']['nlu']["tokens"][1].lower() in [
            'ты', 'вы'

        ]:
            if req['request']['nlu']["tokens"][1].lower() == 'ты':
                sessionStorage[user_id]['official_appeal'] = False
            if req['request']['nlu']["tokens"][1].lower() == 'вы':
                sessionStorage[user_id]['official_appeal'] = True
            res['response']['text'] = 'Приняла. А сколько {} лет? Если не секрет.'.format(
                'вам' if sessionStorage[user_id]['official_appeal'] else 'тебе')

            return
        else:
            res['response']['text'] = \
                'Не понимаю вас. Давайте ещё раз, но внятнее'
            res['response']['buttons'].extend([
                {
                    'title': 'На "Вы"',
                    'hide': True
                },
                {
                    'title': 'На "Ты"',
                    'hide': True
                }
            ])
            return
    if sessionStorage[user_id]['user_age'] is None:
        age = get_age(req)
        if age:
            sessionStorage[user_id]['user_age'] = age[0]
            res['response']['text'] = 'Приступим к тестированию?'
            res['response']['buttons'].extend([
                {
                    'title': "Да",
                    'hide': True
                },
                {
                    'title': 'Нет',
                    'hide': True
                }
            ])
        else:
            res['response']['text'] = 'Не поняла. Повторите'
        return

    else:
        if not sessionStorage[user_id]['game_started']:
            if 'да' in req['request']['nlu']['tokens']:
                sessionStorage[user_id]['game_started'] = True
                sessionStorage[user_id]['attempt'] = 0
                test_start(res, req)
            elif 'нет' in req['request']['nlu']['tokens']:
                res['response']['text'] = 'Ну и ладно!'
                res['end_session'] = True
            else:
                res['response']['text'] = 'Не поняла ответа! Так да или нет?'
                res['response']['buttons'] = [
                    {
                        'title': 'Да',
                        'hide': True
                    },
                    {
                        'title': 'Нет',
                        'hide': True
                    }
                ]
        else:
            test_start(res, req)


def get_age(req):
    age = []
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.NUMBER':
            age.append(entity['value'])

    return age


def test_start(res, req):
    user_id = req['session']['user_id']
    attempt = sessionStorage[user_id]['attempt']
    if True:
        res['response']['text'] = 'qwerty'
        res['response']['card'] = {
            "type": "BigImage",
            "image_id": info_i["images"][
                (len(info_i['images']) - attempt) % len(info_i['images'])],
            "title": "Заголовок для изображения",
            "description": "Описание изображения.",
            "button": {
                "text": "Надпись на кнопке",
                "url": "http://example.com/",
                "payload": {}
            }}


if __name__ == '__main__':
    app.run()
