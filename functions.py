from database import *
import logging


def check_time(before_time_s):
    # переводим в минуты и секунды
    time_m = int(before_time_s // 60)
    time_s = int(before_time_s % 60)
    return time_m, time_s


def get_num(req):
    # находим число
    age = []
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.NUMBER':
            age.append(entity['value'])

    if len(age) != 0:
        return age[0]
    return None


def check_button(res, user, info_i):
    if user.step == 0:
        res['response']['buttons'] = info_i["buttons"]['mainmenu']
    if user.step == 1:

        if user.step_test == 1:
            if user.age == 0:
                res['response']['buttons'] = []
                return
            try:
                rav_test = db.session.query(Raventesting).filter_by(user_id=user.user_id).first()
                if rav_test.start_test:

                    if info_i["tests"]["raventest"]["answers_info"][rav_test.attempt][2] in 'AB':
                        res['response']['buttons'] = info_i["tests"]["raventest"]["buttons"]['AB']
                    else:
                        res['response']['buttons'] = info_i["tests"]["raventest"]["buttons"]['CDE']
                else:
                    res['response']['buttons'] = info_i["tests"]['raventest']["buttons"]["menu"]
            except Exception as ex:
                logging.warning(ex)
                res['response']['buttons'] = info_i["tests"]['raventest']["buttons"]["menu"]
        else:
            res['response']['buttons'] = info_i["buttons"]["test_selection"]

    elif user.step == 2:
        pass

    else:
        res['response']['buttons'] = info_i["buttons"]['mainmenu']

    return res['response']['buttons']
