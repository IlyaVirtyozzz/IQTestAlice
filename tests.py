import copy
from database import *


class Raven_test():
    def __init(self):
        pass

    def calculate_answer(self, user_id, info_i):
        user = db.session.query(User).filter_by(user_id=user_id).first()
        testing = db.session.query(Raventesting).filter_by(user_id=user_id).first()
        answers = list(map(lambda x: int(x),
                           list(testing.answers.replace('[', '').replace(']', '').replace(',', '').replace(' ', ''))))
        percent_iq = int(answers.count(1) / 60 * 100)  # проценты правильных ответов
        estimated_iq = None  # IQ
        # находим по таблице приблизительных значений
        if 8 <= int(str(user.age)) <= 13:
            estimated_iq = info_i["tests"]["raventest"]["raven_diagnostics"]["table"][str(user.age)][
                answers.count(1)]
        elif 14 <= int(str(user.age)) <= 30:
            estimated_iq = info_i["tests"]["raventest"]["raven_diagnostics"]["table"]['14-30'][answers.count(1)]
        else:
            a = info_i["tests"]["raventest"]["raven_diagnostics"]["table"]['14-30'][answers.count(1)]
            if a != '0':
                if 30 <= int(str(user.age)) <= 35:
                    estimated_iq = (int(a) / 97) * 100
                elif 36 <= int(str(user.age)) <= 40:
                    estimated_iq = (int(a) / 93) * 100

                elif 41 <= int(str(user.age)) <= 50:
                    estimated_iq = (int(a) / 88) * 100
                elif 51 <= int(str(user.age)) <= 55:
                    estimated_iq = (int(a) / 82) * 100

                elif 51 <= int(str(user.age)) <= 55:
                    estimated_iq = (int(a) / 76) * 100

                else:
                    estimated_iq = (int(a) / 70) * 100
            else:
                estimated_iq = 0
        if estimated_iq == 0:
            return (percent_iq, estimated_iq)
        else:
            return (percent_iq, int(estimated_iq))

    def get_info(self, percent):
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

    def check_true(self, attempt, answer, user_id, info_i):
        # проверка на правильность ответа
        testing = db.session.query(Raventesting).filter_by(user_id=user_id).first()
        answers = list(
            map(lambda x: int(x),
                list(testing.answers.replace('[', '').replace(']', '').replace(',', '').replace(' ', ''))))
        if answer == info_i["tests"]["raventest"]["answers_info"][attempt - 1][1]:
            answers[attempt - 1] = 1
            testing.answers = str(answers)
            testing.previous_answer = True
            db.session.commit()

            return True
        else:
            testing.previous_answer = False
            db.session.commit()
            return False

    def end_test(self, res, user_id, info_i):
        testing = db.session.query(Raventesting).filter_by(user_id=user_id).first()
        user = db.session.query(User).filter_by(user_id=user_id).first()
        results = db.session.query(Ravenresults).filter_by(user_id=user_id).first()

        testing.start_test = False
        results.percent, results.iq = self.calculate_answer(user_id,
                                                            info_i)
        db.session.commit()
        correctly = ''
        try:
            if testing.previous_answer:
                correctly = "Правильно! "
            else:
                correctly = "Неправильно. "
        except:
            correctly = ''

        if results.iq == 0:
            res['response'][
                'text'] = "Вы выбирали ответы наугад? Это риторический вопрос." \
                          " Пройдите тест ещё раз, выбирайте ответы с умом."
            res['response']['buttons'] = [{"title": "В главное меню", "hide": True}]

            res['response']['text'] = correctly + res['response']['text']
            return res['response'][
                       'text'], res['response']['buttons']
        res['response'][
            'text'] += "Вы выполнили этот тест на {} процентов. Это означает что у вас {}." \
                       " Ваш IQ примерно составляет... {}. ".format(results.percent, self.get_info(results.percent),
                                                                    results.iq
                                                                    if results.iq != '-'
                                                                    else 'Упс... невозможно вычислить')

        res['response']['buttons'] = copy.deepcopy(info_i["buttons"]['aftertest'])
        res['response']['buttons'][0]['url'] = res['response']['buttons'][0]['url'].format(
            results.iq)
        res['response']['text'] = correctly + res['response']['text']
        return res['response'][
                   'text'], res['response']['buttons']


class Assinger_test():
    def __init(self):
        pass

    def get_info(self, user_id):
        testing = db.session.query(Assingertesting).filter_by(user_id=user_id).first()

        if testing.point >= 45:
            text = 'Вы излишне агрессивны, при том нередко бываете неуравновешенным и жестоким по отношению к другим.' \
                   ' Вы надеетесь добраться до управленческих "верхов", рассчитывая на собственные методы,' \
                   'добиться успеха, жертвуя интересами окружающих. Поэтому Вас не удивляет неприязнь сослуживцев,' \
                   ' но при малейшей возможности Вы стараетесь их за это наказать.'
        elif 36 <= testing.point <= 44:
            text = 'Вы умеренно агрессивны, но вполне успешно идете по жизни, поскольку в Вас достаточно' \
                   ' здорового честолюбия и самоуверенности. '
        else:
            text = 'Вы чрезмерно миролюбивы, что обусловлено недостаточной уверенностью в собственных силах' \
                   ' и возможностях. Это отнюдь не значит, что Вы как травинка гнетесь под любым ветерком.' \
                   ' И все же больше решительности Вам не помешает! '

        return text

    def end_test(self, res, user_id, info_i):
        testing = db.session.query(Assingertesting).filter_by(user_id=user_id).first()
        user = db.session.query(User).filter_by(user_id=user_id).first()
        results = db.session.query(Assingerresults).filter_by(user_id=user_id).first()
        testing.start_test = False
        results.result = self.get_info(user_id)
        db.session.commit()
        return self.get_info(user_id)
