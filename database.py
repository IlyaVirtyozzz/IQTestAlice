from constants import *


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=False, nullable=False)
    age = db.Column(db.Integer, unique=False, nullable=False)
    step = db.Column(db.Integer, unique=False, nullable=False)
    step_test = db.Column(db.Integer, unique=False, nullable=False)

    def __repr__(self):
        return "<User {} {} {} {}>".format(self.id, self.age, self.step, self.step_test)


class Ravenresults(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=False, nullable=False)
    percent = db.Column(db.Integer, unique=False, nullable=False)
    iq = db.Column(db.Integer, unique=False, nullable=False)

    def __repr__(self):
        return "<Ravenresults {} {} {} {} >".format(self.id, self.id_user, self.percent, self.iq)


class Raventesting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=False, nullable=False)
    attempt = db.Column(db.Integer, unique=False, nullable=False)
    start_test = db.Column(db.Boolean)
    start_time = db.Column(db.Integer, unique=False, nullable=False)
    answers = db.Column(db.String(1000), unique=False, nullable=False)
    previous_answer = db.Column(db.Boolean)

    def __repr__(self):
        return "<Ravenresults {} {} {} {} {} {}>".format(self.id, self.id_user, self.attempt, self.start_test,
                                                         self.start_time, self.answers, self.previous_answer)


class Assingerresults(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=False, nullable=False)
    result = db.Column(db.String(1000), unique=False, nullable=False)

    def __repr__(self):
        return "<Ravenresults {} {} {}>".format(self.id, self.result, self.user_id)


class Assingertesting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=False, nullable=False)
    attempt = db.Column(db.Integer, unique=False, nullable=False)
    start_test = db.Column(db.Boolean)
    point = db.Column(db.Integer, unique=False, nullable=False)

    def __repr__(self):
        return "<Ravenresults {} {} {} {} {}>".format(self.id, self.id_user, self.attempt, self.start_test,
                                                      self.point)


def add_new_user(user_id):
    user = User(user_id=user_id, age=0, step=0, step_test=0)
    db.session.add(user)
    db.session.commit()


if __name__ == '__main__':
    db.create_all()
