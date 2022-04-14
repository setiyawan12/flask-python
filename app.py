#M. Galih Fikransyah - 19090074
#Muhamad Zaim Zamzami - 19090036
#Fatimatuzzahro - 19090039
#Nirvanna Indiranjani - 19090046
import os
import random
import string
from flask import Flask, render_template, request, jsonify
from datetime import datetime
from sqlalchemy import desc
from flask_marshmallow import Marshmallow

from flask_sqlalchemy import SQLAlchemy
project_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///{}".format(os.path.join(project_dir, "database.db"))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
ma= Marshmallow(app)
class LogSchema(ma.Schema):
    class Meta:
        fields=('username', 'log_lat', 'log_lng','created_at')

logsSchema = LogSchema(many=True)
class  User(db.Model):
    id_user = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    token = db.Column(db.String(10), unique=True, nullable=True)

    def __init__(self,username, password):
        self.username = username
        self.password = password
      

class  Event(db.Model):
    id_event = db.Column(db.Integer, primary_key=True)
    event_creator = db.Column(db.String(20), nullable=False)
    event_name = db.Column(db.String(20), unique=True, nullable=False)
    event_start_time = db.Column(db.DateTime, nullable=True)
    event_end_time = db.Column(db.DateTime, nullable=True)
    event_start_lat = db.Column(db.String(20), nullable=False)
    event_finish_lat = db.Column(db.String(20), nullable=False)
    event_start_lng = db.Column(db.String(20), nullable=False)
    event_finish_lng = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, event_creator, event_name, event_start_time,event_end_time,event_start_lat,event_finish_lat,event_start_lng,event_finish_lng):
        self.event_creator = event_creator
        self.event_name = event_name
        self.event_start_time = event_start_time
        self.event_end_time = event_end_time
        self.event_start_lat = event_start_lat
        self.event_finish_lat = event_finish_lat
        self.event_start_lng = event_start_lng
        self.event_finish_lng = event_finish_lng
       

class Log(db.Model):
    id_log = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    event_name = db.Column(db.String(20), nullable=False)
    log_lat = db.Column(db.String(20), nullable=False)
    log_lng = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, username, event_name, log_lat, log_lng):
        self.username = username
        self.event_name = event_name
        self.log_lat = log_lat
        self.log_lng = log_lng

db.create_all()

@app.route("/api/v1/users/create", methods=['POST'])
def createUser():
    newUser = User(username = request.json['username'],password = request.json['password'])

    db.session.add(newUser)
    db.session.commit()

    return jsonify({'msg': 'Registrasi Sukses'}), 200

# login
@app.route("/api/v1/users/login", methods=['POST'])
def login():
    req = request.json;
    search = User.query.filter_by(username = req['username'], password = req['password']).first();
    if search:
        letters = string.ascii_uppercase
        token = ''.join(random.choice(letters) for i in range(10))

        userLogin= User.query.filter_by(username = req['username'], password= req['password']).first()
        userLogin.token = token
        db.session.commit();

        return {
            "msg" : "Login Sukses",
            "Token" : token
        }, 200

@app.route("/api/v1/events/create", methods=['POST'])
def createEvent():
    token = request.json['token']
    userLogin = User.query.filter(User.token==token).first()
   
    newEvent = Event(
        event_creator = userLogin.username,
        event_name = request.json['event_name'],
        event_start_time = datetime.strptime(request.json['event_start_time'], "%Y-%m-%d %H:%M:%S") ,
        event_end_time = datetime.strptime(request.json['event_end_time'], "%Y-%m-%d %H:%M:%S") ,
        event_start_lat = request.json['event_start_lat'],
        event_start_lng = request.json['event_start_lng'],
        event_finish_lat = request.json['event_finish_lat'],
        event_finish_lng = request.json['event_finish_lng']
    )

    db.session.add(newEvent)
    db.session.commit()

    return jsonify({'msg': 'Membuat event sukses'}), 200

@app.route("/api/v1/events/logs", methods=['POST'])
def createEventLog():
    token = request.json['token']
    userLogin = User.query.filter(User.token==token).first()
    if(userLogin):
        newLog = Log(
        username=userLogin.username,
        event_name = request.json['event_name'],
        log_lat = request.json['log_lat'],
        log_lng = request.json['log_lng']
        
    )
        db.session.add(newLog)
        db.session.commit()
        return jsonify({'msg': 'Sukses mencatat posisi terbaru'}), 200
    else:
        data:{"Messages":"Unathorized"}
        return jsonify(data)

@app.route("/api/v1/events/logs", methods=['GET'])
def createEventLogs():
    token = request.json['token']
    userLogin = User.query.filter(User.token==token).first()
    if(userLogin):
        event_name = request.json['event_name']
        dataLog= Log.query.filter(Log.event_name == event_name).order_by(desc(Log.created_at))
        result = logsSchema.dump(dataLog)
        return jsonify(result)
    else:
        data={"Message":"Unathorized"}
        return jsonify(data)
        

    
