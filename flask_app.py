from database import *
from functions import *
from tests import *
import logging, time, json, random, copy

logging.basicConfig(level=logging.INFO, filename='/home/Testsss/mysite/app.log',
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')

with open("/home/Testsss/mysite/info.json", "r", ) as read_file:
    info_i = json.load(read_file)

t_raven = Raven_test()
t_assinger = Assinger_test()


@app.route('/', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {}
    }
    handle_dialog(response, request.json)
    logging.info('Request: %r', response)
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    res['response']['buttons'] = []
    user = db.session.query(User).filter_by(user_id=user_id).first()
    if req['session']['new']:
        if not user:
            add_new_user(user_id)
            user.step_test = 0
            user.step = 0
            db.session.commit()
            res['response']['text'] = \
                'Привет! Проходи тесты, узнавай о своём мышлении! Скажи "Помощь"' \
                ' или "Что ты умеешь?" чтобы узнать больше.'
            res['response']['buttons'] = info_i["buttons"]['mainmenu']
            return

        if user.step == 1:

            if user.step_test == 1:

                try:
                    rav_test = db.session.query(Raventesting).filter_by(user_id=user.user_id).first()
                    if rav_test.start_test:
                        if user.age == 0:
                            res['response']['text'] = 'Cколько вам лет? Если не секрет?'
                            return

                        db.session.commit()
                        if rav_test.attempt == 0:
                            rav_test.attempt += 1
                            rav_test.start_time = int(time.time())  # засекаем время
                            db.session.commit()
                        res['response']['text'] = 'qwerty'
                        res['response']['card'] = {
                            "type": "BigImage",
                            "title": "Вопрос: {}/60".format(rav_test.attempt),  # выводим позицию текущего вопроса
                            "description": "{}".format(
                                random.choice(
                                    info_i["dialogs"]["reassurance"]) + "\nОсталось времени: {}мин {}с".format(
                                    # время
                                    *check_time(rav_test.start_time - int(time.time() - 1200)))),
                            "image_id": info_i["tests"]["raventest"]["answers_info"][
                                (len(info_i["tests"]["raventest"]["answers_info"]) + rav_test.attempt - 1) % len(
                                    info_i["tests"]["raventest"]["answers_info"])][0],
                        }
                        # в заданиях группы А и Б по 6 возможных вариантов ответов , в С,Д,Е по 8
                        if info_i["tests"]["raventest"]["answers_info"][rav_test.attempt][2] in 'AB':
                            res['response']['buttons'] = info_i["tests"]["raventest"]["buttons"]['AB']
                        else:
                            res['response']['buttons'] = info_i["tests"]["raventest"]["buttons"]['CDE']
                    else:
                        res['response']['text'] = 'Этот тест может определть ваше IQ'
                        res['response']['buttons'] = info_i["tests"]['raventest']["buttons"]["menu"]
                except Exception as ex:
                    logging.warning(ex)
                    res['response']['text'] = 'Этот тест может определть ваше IQ'
                    res['response']['buttons'] = info_i["tests"]['raventest']["buttons"]["menu"]
                    return
            elif user.step_test == 2:
                try:
                    assinger_test = db.session.query(Assingertesting).filter_by(user_id=user.user_id).first()
                    if assinger_test.start_test:
                        if assinger_test.attempt == 0:
                            assinger_test.attempt = 1
                            db.session.commit()

                        res['response']['text'] = 'Вопрос: {}/20\n'.format(assinger_test.attempt)
                        res['response']['text'] += "{}\n" \
                                                   "{}\n" \
                                                   "{}\n" \
                                                   "{}\n".format(
                            info_i["tests"]["assingertest"]["answers_info"][assinger_test.attempt - 1]['question'],
                            *info_i["tests"]["assingertest"]["answers_info"][assinger_test.attempt - 1]['answers'])

                        res['response']['buttons'] = info_i["tests"]["assingertest"]["buttons"]['testing']

                    else:
                        res['response']['text'] = 'Этот тест может проверить насколько вы агрессивны'
                        res['response']['buttons'] = info_i["tests"]['assingertest']["buttons"]["menu"]
                except Exception as ex:

                    res['response']['text'] = 'Этот тест может проверить насколько вы агрессивны'
                    res['response']['buttons'] = info_i["tests"]['assingertest']["buttons"]["menu"]

            else:
                res['response']['text'] = "Выберите тест"
                res['response']['buttons'] = info_i["buttons"]["test_selection"]

        elif user.step == 2:
            res['response']['text'] = "Введите возраст"

        else:
            res['response']['text'] = \
                'Привет! Проходи тесты, узнавай о своём мышлении! Скажи "Помощь"' \
                ' или "Что ты умеешь?" чтобы узнать больше.'
            res['response']['buttons'].extend(info_i["buttons"]['mainmenu'])
        return

    res['response']['buttons'] = check_button(res, user, info_i)

    if 'помощь' in list(map(lambda x: x.lower(), req['request']['nlu']["tokens"])) or 'умеешь' in list(
            map(lambda x: x.lower(), req['request']['nlu']["tokens"])):
        res['response'][
            'text'] = 'Здесь ты можешь пройти несколько тестов'

        return
    if user.step == 0:

        if 'выбрать' in list(map(lambda x: x.lower(), req['request']['nlu']["tokens"])):
            user.step = 1
            db.session.commit()
            res['response']['text'] = 'Выберите тест'
            res['response']['buttons'] = info_i["buttons"]["test_selection"]
        elif 'возраст' in list(map(lambda x: x.lower(), req['request']['nlu']["tokens"])):
            user.step = 2
            db.session.commit()
            change_age(res, req)
            res['response']['text'] = "Введите возраст"
            res['response']['buttons'] = []
            return
        elif 'результаты' in list(map(lambda x: x.lower(), req['request']['nlu']["tokens"])):
            get_results(res, req, user_id)
            res['response']['buttons'] = info_i["buttons"]['mainmenu']
        else:
            res['response']['text'] = \
                random.choice(info_i["dialogs"]["incomprehension"])  # ¯\_(ツ)_/¯
            res['response']['buttons'] = info_i["buttons"]['mainmenu']
        return
    if user.step == 1:
        res['response']['buttons'] = info_i["buttons"]["test_selection"]
        test_selection(res, req, user)

    if user.step == 2:
        res['response']['buttons'] = []
        change_age(res, req)


def get_results(res, req, user_id):
    results_rav = db.session.query(Ravenresults).filter_by(user_id=user_id).first()
    results_ass = db.session.query(Assingerresults).filter_by(user_id=user_id).first()
    res['response']['text'] = 'Тест Равена:'
    if results_rav:
        res['response']['text'] += '\n' \
                                   'IQ: {}\n' \
                                   'Процент правильных: {}'.format(results_rav.iq, results_rav.percent)
    else:
        res['response']['text'] += '\n' \
                                   'Вы ещё не прошли этот тест'
    res['response']['text'] += '\nТест Ассингера:'
    if results_ass:
        res['response']['text'] += '\n' \
                                   '{}'.format(results_ass.result)
    else:
        res['response']['text'] += '\n' \
                                   'Вы ещё не прошли этот тест'


def change_age(res, req):
    user_id = req['session']['user_id']
    user = db.session.query(User).filter_by(user_id=user_id).first()
    age = get_num(req)
    if age and type(age) is int:
        if 7 < age < 80:
            user.age = age
            user.step = 0
            db.session.commit()
            res['response'][
                'text'] = 'Запомнила.'
            res['response']['buttons'] = info_i["buttons"]['mainmenu']

        elif not 7 < age < 80:
            res['response']['text'] = 'Брррррррр,введите настоящий возраст'
    else:
        res['response']['text'] = random.choice(info_i["dialogs"]["incomprehension"])  # ¯\_(ツ)_/¯
    return


def test_selection(res, req, user):
    if user.step_test == 0:
        if 'равена' in list(map(lambda x: x.lower(), req['request']['nlu']["tokens"])):
            user.step_test = 1
            db.session.commit()
            res['response']['text'] = 'Этот тест может определть ваше IQ'
            res['response']['buttons'] = info_i["tests"]['raventest']["buttons"]["menu"]
            return
        if 'ассингера' in list(map(lambda x: x.lower(), req['request']['nlu']["tokens"])):
            user.step_test = 2
            db.session.commit()
            res['response']['text'] = 'Этот тест может проверить насколько вы агрессивны'
            res['response']['buttons'] = info_i["tests"]['assingertest']['buttons']["menu"]
            return
        elif "главное" in list(map(lambda x: x.lower(), req['request']['nlu']["tokens"])):
            user.step = 0
            db.session.commit()
            res['response'][
                'text'] = 'Привет! Проходи тесты, узнавай о своём мышлении!' \
                          ' Скажи "Помощь" или "Что ты умеешь?" чтобы узнать больше.'
            res['response']['buttons'] = info_i["buttons"]["mainmenu"]
            return
        else:
            res['response']['text'] = random.choice(info_i["dialogs"]["incomprehension"])  # ¯\_(ツ)_/¯
            return
    if user.step_test == 1:
        current_test = db.session.query(Raventesting).filter_by(user_id=user.user_id).first()
        try:

            if current_test.start_test:
                res['response']['buttons'] = []
                raven_test_start(res, req, user)
            elif user.age == 0:
                res['response']['buttons'] = []
                raven_test_start(res, req, user)
            else:
                test_menu(res, req, 'raventest', user)
        except Exception as ex:
            logging.warning(ex)
            test_menu(res, req, 'raventest', user)
    elif user.step_test == 2:
        current_test = db.session.query(Assingertesting).filter_by(user_id=user.user_id).first()
        try:
            logging.warning(current_test.start_test)
            if current_test.start_test:
                res['response']['buttons'] = []
                assinger_test_start(res, req, user)
            else:
                test_menu(res, req, 'assingertest', user)
        except Exception as ex:
            logging.warning(ex)
            test_menu(res, req, 'assingertest', user)
    else:
        res['response']['text'] = random.choice(info_i["dialogs"]["incomprehension"])  # ¯\_(ツ)_/¯
    return


def test_menu(res, req, selected_test, user):
    res['response']['buttons'] = info_i["tests"][selected_test]["buttons"]["menu"]
    if 'начать' in list(map(lambda x: x.lower(), req['request']['nlu']["tokens"])):
        if selected_test == 'raventest':
            res['response']['buttons'] = []
            user_id = req['session']['user_id']
            current_test = db.session.query(Raventesting).filter_by(user_id=user_id).first()

            results = db.session.query(Ravenresults).filter_by(user_id=user_id).first()
            if current_test and not current_test.start_test:
                db.session.delete(current_test)
                db.session.commit()
            current_test = Raventesting(user_id=user_id, attempt=0, start_time=0, start_test=True,
                                        answers=str(list(map(lambda x: 0, range(60)))))
            db.session.add(current_test)
            db.session.commit()
            if not results:
                results = Ravenresults(user_id=user_id, percent=0, iq=0)
                db.session.add(results)
                db.session.commit()

            if user.age == 0:
                res['response']['text'] = 'Приняла. А сколько вам лет? Если не секрет.'

            else:
                res['response'][
                    'text'] = 'Отправьте любое сообщение чтобы начать. У вас есть 20 минут чтобы ответить на вопросы'
                res['response']['buttons'] = [{"title": "Любое сообщение.", "hide": True}]

            return
        if selected_test == 'assingertest':
            res['response']['buttons'] = []
            user_id = req['session']['user_id']
            current_test = db.session.query(Assingertesting).filter_by(user_id=user_id).first()

            results = db.session.query(Assingerresults).filter_by(user_id=user_id).first()
            if current_test and not current_test.start_test:
                db.session.delete(current_test)
                db.session.commit()
            current_test = Assingertesting(user_id=user_id, attempt=0, start_test=True, point=0)
            db.session.add(current_test)
            db.session.commit()
            if not results:
                results = Assingerresults(user_id=user_id, result='')
                db.session.add(results)
                db.session.commit()

            res['response'][
                'text'] = 'Отправьте любое сообщение чтобы начать.'
            res['response']['buttons'] = [{"title": "Любое сообщение.", "hide": True}]

            return
    elif 'найти' in list(map(lambda x: x.lower(), req['request']['nlu']["tokens"])):
        res['response']['text'] = 'Открываю'
    elif 'краткая' in list(map(lambda x: x.lower(), req['request']['nlu']["tokens"])):
        res['response']['text'] = info_i["tests"][selected_test]["info"]
    elif 'назад' in list(map(lambda x: x.lower(), req['request']['nlu']["tokens"])):
        user.step_test = 0
        db.session.commit()
        res['response']['text'] = 'Выберите тест'
        res['response']['buttons'] = info_i["buttons"]["test_selection"]
    elif 'узнать' in list(
            map(lambda x: x.lower(), req['request']['nlu']["tokens"])):  # узнать информацию о своём интеллекте
        if selected_test == 'assingertest':
            res['response']['text'] = 'Открываю'
        else:
            res['response']['text'] = random.choice(info_i["dialogs"]["incomprehension"])
    elif 'главное' in list(map(lambda x: x.lower(), req['request']['nlu']["tokens"])):
        user.step = 0
        user.step_test = 0
        db.session.commit()
        res['response']['buttons'] = info_i["buttons"]['mainmenu']
        res['response'][
            'text'] = 'Привет! Проходи тесты, узнавай о своём мышлении!' \
                      ' Скажи "Помощь" или "Что ты умеешь?" чтобы узнать больше.'
    else:
        res['response']['text'] = random.choice(info_i["dialogs"]["incomprehension"])
    return


def assinger_test_start(res, req, user):
    user_id = req['session']['user_id']
    current_test = db.session.query(Assingertesting).filter_by(user_id=user_id).first()
    results = db.session.query(Assingerresults).filter_by(user_id=user_id).first()

    attempt = current_test.attempt
    start_test = current_test.start_test
    if start_test:
        if attempt != 0 and attempt < 20:
            num = get_num(req)
            if num:
                if 1 <= int(num) <= 3:

                    if int(num) == 1:

                        current_test.point += 1
                    elif int(num) == 2:

                        current_test.point += 2
                    elif int(num) == 3:
                        current_test.point += 3
                    db.session.commit()
                else:
                    res['response']['buttons'] = info_i["tests"]["assingertest"]["buttons"]['testing']
                    res['response']['text'] = random.choice(info_i["dialogs"]["incomprehension"])
                    return
            else:
                res['response']['buttons'] = info_i["tests"]["assingertest"]["buttons"]['testing']
                res['response']['text'] = random.choice(info_i["dialogs"]["incomprehension"])  # ¯\_(ツ)_/¯
                return

        if attempt < 20:

            current_test.attempt += 1
            db.session.commit()

            res['response']['text'] = 'Вопрос: {}/20\n'.format(attempt + 1)
            res['response']['text'] += "{}\n" \
                                       "{}\n" \
                                       "{}\n" \
                                       "{}\n".format(
                info_i["tests"]["assingertest"]["answers_info"][attempt]['question'],
                *info_i["tests"]["assingertest"]["answers_info"][attempt]['answers'])

            res['response']['buttons'] = info_i["tests"]["assingertest"]["buttons"]['testing']
        else:
            logging.warning('end')
            res['response']['buttons'] = info_i["tests"]["assingertest"]["buttons"]["menu"]
            res['response'][
                'text'] = t_assinger.end_test(res, user_id, info_i)
            return


def raven_test_start(res, req, user):
    user_id = req['session']['user_id']
    current_test = db.session.query(Raventesting).filter_by(user_id=user_id).first()
    results = db.session.query(Ravenresults).filter_by(user_id=user_id).first()
    attempt = current_test.attempt
    start_test = current_test.start_test

    if user.age == 0:
        age = get_num(req)
        if age and type(age) is int:
            if 7 < age < 80:
                user.age = age
                db.session.commit()
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
                current_test.start_time = int(time.time())  # засекаем время
                db.session.commit()
            if current_test.start_time - int(time.time() - 1200) < 0:
                res['response']['text'] = 'Упс. Похоже время вышло. '
                res['response']['text'], _ = \
                    t_raven.end_test(res, user_id, info_i)  # заканчиваем тест
                return

            if attempt != 0 and attempt < 60:
                num = get_num(req)
                if num:
                    if 1 <= int(num) <= 8:
                        t_raven.check_true(attempt, num, user_id, info_i)
                    else:
                        if info_i["tests"]["raventest"]["answers_info"][attempt][2] in 'AB':
                            res['response']['buttons'] = info_i["tests"]["raventest"]["buttons"]['AB']
                        else:
                            res['response']['buttons'] = info_i["tests"]["raventest"]["buttons"]['CDE']
                        res['response']['text'] = random.choice(info_i["dialogs"]["incomprehension"])  # ¯\_(ツ)_/¯
                        return
                else:
                    if info_i["tests"]["raventest"]["answers_info"][attempt][2] in 'AB':
                        res['response']['buttons'] = info_i["tests"]["raventest"]["buttons"]['AB']
                    else:
                        res['response']['buttons'] = info_i["tests"]["raventest"]["buttons"]['CDE']
                    res['response']['text'] = random.choice(info_i["dialogs"]["incomprehension"])  # ¯\_(ツ)_/¯
                    return
            if attempt < 60:
                correctly = ''
                try:
                    if current_test.previous_answer:
                        correctly = "Правильно! "
                    else:
                        correctly = "Неправильно. "
                except:
                    correctly = ''
                current_test.attempt += 1
                db.session.commit()
                res['response']['text'] = 'qwerty'
                res['response']['card'] = {
                    "type": "BigImage",
                    "title": "{}Вопрос: {}/60".format(correctly, attempt + 1),  # выводим позицию текущего вопроса
                    "description": "{}".format(
                        random.choice(info_i["dialogs"]["reassurance"]) + "\nОсталось времени: {}мин {}с".format(
                            # время
                            *check_time(current_test.start_time - int(time.time() - 1200)))),
                    "image_id": info_i["tests"]["raventest"]["answers_info"][
                        (len(info_i["tests"]["raventest"]["answers_info"]) + attempt) % len(
                            info_i["tests"]["raventest"]["answers_info"])][0],
                }
                # в заданиях группы А и Б по 6 возможных вариантов ответов , в С,Д,Е по 8
                if info_i["tests"]["raventest"]["answers_info"][attempt][2] in 'AB':

                    res['response']['buttons'] = info_i["tests"]["raventest"]["buttons"]['AB']
                else:
                    res['response']['buttons'] = info_i["tests"]["raventest"]["buttons"]['CDE']
            else:
                logging.warning('end')
                res['response']['text'] = ''
                res['response'][
                    'text'], _ = t_raven.end_test(res, user_id, info_i)


        else:
            res['response']['buttons'] = copy.deepcopy(info_i["buttons"]['aftertest'])  # меню после теста
            res['response']['buttons'][0]['url'] = res['response']['buttons'][0]['url'].format(
                results.iq)
            if results.iq == 0:
                res['response']['buttons'] = [{"title": "В главное меню", "hide": True}]
            if 'узнать' in list(
                    map(lambda x: x.lower(), req['request']['nlu']["tokens"])):  # узнать информацию о своём интеллекте
                res['response']['text'] = 'Открываю'
            elif "меню" in list(map(lambda x: x.lower(), req['request']['nlu']["tokens"])):

                user.step = 0  # переходим в главное меню
                user.step_test = 0
                db.session.commit()
                res['response']['buttons'] = info_i["buttons"]['mainmenu']
                res['response']['text'] = 'Привет! Здесь можно проверить свой IQ!'

            else:
                res['response']['text'] = random.choice(info_i["dialogs"]["incomprehension"])  # ¯\_(ツ)_/¯
