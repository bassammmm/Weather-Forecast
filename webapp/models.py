from webapp import db,login_manager,app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    forecasts = db.relationship('Forecast', backref='user', lazy=True)

    def return_dict(self):
        user_dict = {
            'id' : self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'password': self.password,
            'role': self.role,
            }


        return user_dict

    @classmethod
    def return_all_obj(cls):
        users_dict = {}
        for user in User.query.all():
            users_dict[user.id] = user.return_dict()
        return users_dict


class Forecast(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lon = db.Column(db.String(50), nullable=True)
    lat = db.Column(db.String(50), nullable=True)
    main = db.Column(db.String(50), nullable=True)
    description = db.Column(db.String(50), nullable=True)
    temp = db.Column(db.String(50), nullable=True)
    feels_like = db.Column(db.String(50), nullable=True)
    temp_min = db.Column(db.String(50), nullable=True)
    temp_max = db.Column(db.String(50), nullable=True)
    pressure = db.Column(db.String(50), nullable=True)
    humidity = db.Column(db.String(50), nullable=True)
    sea_level = db.Column(db.String(50), nullable=True)
    grnd_level = db.Column(db.String(50), nullable=True)
    time_of_forecast = db.Column(db.DateTime,nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def get_string(self):
        return f"Time : {self.time_of_forecast}, Main : {self.main}, Temp_Min : {self.temp_min}, Temp_Max : {self.temp_max}"