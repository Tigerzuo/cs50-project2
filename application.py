import os

from flask import Flask, render_template, session, redirect, request, jsonify
from flask_socketio import SocketIO, emit
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from functools import wraps

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

channels = {"Default":[]}

def login_required(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("username") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

def check_login(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is not None:  
            return redirect("/index")
        return f(*args, **kwargs)
    return decorated_function


@app.route("/", methods=['GET','POST'])
@check_login
def login():
    if request.method == 'POST':
        name = request.form.get("username")
        session['username'] = name
        if session.get("channel") is None:
            session['channel'] = "Default"
        return redirect(f"/index/{session['channel']}")
    return render_template("login.html")


@app.route("/index/<string:channel>", methods=['GET','POST'])
@login_required
def index(channel):
    if request.method == 'GET':
        session['channel'] = channel
    return render_template("index.html", name=session["username"], channels=channels, channel=channels[channel], channel_name=channel)

@app.route("/add_channel", methods=['POST'])
@login_required
def add_channel():
    global channels
    channel = request.form.get('channel')
    if len(channel) == 0:
        return redirect("/index/" + session['channel'])
    if channel in channels:
        return redirect("/index/" + channel)
    session['channel'] = channel
    channels[channel] = []
    channel = "/index/" + channel
    print(channel)
    return redirect(channel)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', { "username": session["username"], "message": json["message"] }, callback=messageReceived)

@socketio.on('new message')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    global channels
    msg = str(json)
    print('received new message: ' + msg)
    channels[session['channel']].append((session["username"],json["message"]))




