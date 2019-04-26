def calculate_answer(user_id, sessionStorage, info_i):
    percent_iq = int(sessionStorage[user_id]['answers'].count(1) / 60 * 100)  # проценты правильных ответов
    estimated_iq = None  # неточный IQ
    # находим по таблице приблизительных значений
    if 8 <= int(sessionStorage[user_id]['user_age']) <= 13:
        estimated_iq = info_i["raven_diagnostics"]["table"][sessionStorage[user_id]['user_age']][
            sessionStorage[user_id]['answers'].count(1)]
    elif 14 <= int(sessionStorage[user_id]['user_age']) <= 30:
        estimated_iq = info_i["raven_diagnostics"]["table"]['14-30'][sessionStorage[user_id]['answers'].count(1)]
    else:
        a = info_i["raven_diagnostics"]["table"]['14-30'][sessionStorage[user_id]['answers'].count(1)]
        if a != '-':
            if 30 <= int(sessionStorage[user_id]['user_age']) <= 35:
                estimated_iq = (int(a) / 97) * 100
            elif 36 <= int(sessionStorage[user_id]['user_age']) <= 40:
                estimated_iq = (int(a) / 93) * 100

            elif 41 <= int(sessionStorage[user_id]['user_age']) <= 50:
                estimated_iq = (int(a) / 88) * 100
            elif 51 <= int(sessionStorage[user_id]['user_age']) <= 55:
                estimated_iq = (int(a) / 82) * 100

            elif 51 <= int(sessionStorage[user_id]['user_age']) <= 55:
                estimated_iq = (int(a) / 76) * 100

            else:
                estimated_iq = (int(a) / 70) * 100
        else:
            estimated_iq = '-'
    if estimated_iq == '-':
        return (percent_iq, estimated_iq)
    else:
        return (percent_iq, int(estimated_iq))


def get_info_p(percent):
    percent = int(percent)
    text = None
    if percent <= 5:
        text = 'дефектная интеллектуальная способность'
    elif 5 <= percent <= 24:
        text = 'интеллект ниже среднего.'
    elif 25 <= percent <= 74:
        text = 'средник интеллект'
    elif 75 <= percent <= 95:
        text = 'незаурядный интеллект'
    elif 95 <= percent:
        text = 'особо высокоразвитый интеллект'

    return text


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
