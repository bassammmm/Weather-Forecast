from flask import render_template,url_for,flash,redirect,request,abort,jsonify,session  #request is imported for query parameters in routes
from webapp import app,db,bcrypt,mail
from webapp.models import *
from webapp.forms import *
from flask_login import login_user,current_user,logout_user,login_required
from flask_mail import Message
from functools import wraps
import requests
import geocoder
import requests
import json
import datetime

from apscheduler.schedulers.background import BackgroundScheduler




#-----------------------------------------------------------------------------------------------------------------------#
###########################                       SCHEDULED EMAIL                       #################################
#-----------------------------------------------------------------------------------------------------------------------#

def send_mail():
    for user in User.query.all():
        m = '''
                            Hey {}!
                            Following are the details of your forecasts for yesterday!
                            
                            '''.format(user.first_name + ' ' + user.last_name.title())
        for forecasts in user.forecasts:
            date_forecast = forecasts.time_of_forecast.date()
            yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
            yesterday = yesterday.date()
            if date_forecast==yesterday:
                m+=f'\n{forecasts.get_string}'

        email, subject, message = 'NexDegree@gmail.com', 'ForeCasts Update',m
        msg = Message(subject, sender=email, recipients=[user.email])
        msg.body = message
        mail.send(msg)

sched = BackgroundScheduler(daemon=True)
sched.add_job(send_mail,'cron',hour=9, minute=0,second=0)
sched.start()



#-----------------------------------------------------------------------------------------------------------------------#
###########################                       MISC FUNCS                       ###################################
#-----------------------------------------------------------------------------------------------------------------------#

def login_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if ((current_user.role != role) and (role != "ANY")):


                return redirect(url_for('unauthorized'))
            return fn(*args, **kwargs)


        return decorated_view


    return wrapper



#-----------------------------------------------------------------------------------------------------------------------#
###########################                       HOME PAGE                           ###################################
#-----------------------------------------------------------------------------------------------------------------------#

@app.route('/')
@app.route('/home')
def home():
    g = geocoder.ip('me')
    lat, lon = g.latlng

    API_KEY = "cc75913f8e1dafdb317ff0d22c3825e3"

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}"
    req = requests.get(url)
    data = json.loads(req.text)
    print(data)
    city_name = data["name"]

    return render_template('home.html',data=data,city_name=city_name)





@app.route('/loginreg',methods=['GET','POST'])
def loginreg():

    return render_template('loginreg.html')





#-----------------------------------------------------------------------------------------------------------------------#
###########################                       FORECAST                            ###################################
#-----------------------------------------------------------------------------------------------------------------------#


@app.route('/getforecast',methods=['GET','POST'])
def getforecast():
    if current_user.is_authenticated:
        if session["count"]>=3:
            time_right_now = datetime.datetime.now(datetime.timezone.utc)
            minutes_diff = (time_right_now - session["start_time"]).total_seconds() / 60.0
            if minutes_diff<=5:
                return jsonify({'val': True, 'msg': "Limit Exceeded!"})
            else:
                session["count"] = 1
                session['start_time'] = datetime.datetime.now(datetime.timezone.utc)

        session["count"] +=1
        g = geocoder.ip('me')
        lat, lon = g.latlng

        API_KEY = "cc75913f8e1dafdb317ff0d22c3825e3"

        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}"
        req = requests.get(url)
        data = json.loads(req.text)
        print(data)
        lon,lat,main,description,temp,feels_like,temp_min,temp_max,pressure,humidity,sea_level,grnd_level = data["coord"]["lon"],data["coord"]["lat"],data["weather"][0]["main"],data["weather"][0]["description"],data["main"]["temp"],data["main"]["feels_like"],data["main"]["temp_min"],data["main"]["temp_max"],data["main"]["pressure"],data["main"]["humidity"],data["main"]["sea_level"],data["main"]["grnd_level"]
        forecast = Forecast(lon=lon,lat=lat,main=main,description=description,temp=temp,feels_like=feels_like,temp_min=temp_min,temp_max=temp_max,pressure=pressure,humidity=humidity,sea_level=sea_level,grnd_level=grnd_level,time_of_forecast=datetime.datetime.now(datetime.timezone.utc),user=current_user)
        db.session.add(forecast)
        db.session.commit()

        time_now = str(datetime.datetime.now()).split('.')[0]
        print(time_now)
        return jsonify({'val': True,'msg':"DATA STORED : Time stamp : "+time_now})
    else:
        return jsonify({'val': False})


#-----------------------------------------------------------------------------------------------------------------------#
###########################                       Login Register                      ###################################
#-----------------------------------------------------------------------------------------------------------------------#


@app.route('/loginver',methods=['GET','POST'])
def loginver():
    session['start_time'] = datetime.datetime.now(datetime.timezone.utc)
    session["count"] = 0


    data = dict(request.form)
    email, password = data['email'], data['password']

    if email!='' and password!='':


        user = User.query.filter_by(email=email).first()
        print(user)
        if user:
            if email==user.email and password==user.password and user.role=='CUSTOMER':

                login_user(user)
                return jsonify({'val': True,'route':'home'})


        else:
            print('hereeee')
            return jsonify({'val': 'You are not yet registered! Please register first!'})

    return jsonify({'val': 'Hmm, Something unexpected has happened. Try again.'})

@app.route('/regver',methods=['GET','POST'])
def regver():
    data = dict(request.form)
    fname,lname,address,phonenum,email,password = data['fname'],data['lname'],data['add'],data['pnum'],data['email'],data['password']
    if fname!='' and lname!='' and address!='' and phonenum!='' and email!='' and password!='':
        user = User.query.filter_by(email=email).first()
        if user:
            return jsonify({'val': 'Account already registered. Please login'})
        else:

            user = User(first_name = fname, last_name = lname,email=email,password=password,role='CUSTOMER')


            db.session.add(user)
            db.session.commit()
            return jsonify({'val': 'Registered successfully, please login now :)'})



    return jsonify({'val': 'Hmm, Something unexpected has happened. Try again.'})





@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))
